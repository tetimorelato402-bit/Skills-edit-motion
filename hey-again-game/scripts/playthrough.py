"""Plays a whole game against a running server, as two phones would.

    npm run demo                       # terminal 1, no database needed
    python3 scripts/playthrough.py http://localhost:3000

Checks the things the game is actually for: two seats and no more, answers
staying secret until both are locked, 21 cards in order, a shared card of one
answer each. Exits non-zero on the first broken promise.
"""
import json, sys, urllib.request, urllib.error

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:3000"
fails = []

def check(name, cond, detail=""):
    print(("  ok   " if cond else "  FAIL ") + name + ("" if cond else f"  <- {detail}"))
    if not cond:
        fails.append(name)

class Player:
    """One phone: its own cookies and its own seat token.
    Cookies are tracked by hand; http.cookiejar refuses to send them to
    'localhost', which would make this test lie."""
    def __init__(self, token):
        self.token = token
        self.cookies = {}

    def _remember(self, headers):
        for raw in headers.get_all("Set-Cookie") or []:
            pair = raw.split(";", 1)[0]
            if "=" in pair:
                k, v = pair.split("=", 1)
                self.cookies[k.strip()] = v.strip()

    def call(self, path, body=None, send_token=True):
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(BASE + path, data=data, method="POST" if body is not None else "GET")
        if send_token:
            req.add_header("x-hg-token", self.token)
        if data:
            req.add_header("content-type", "application/json")
        if self.cookies:
            req.add_header("cookie", "; ".join(f"{k}={v}" for k, v in self.cookies.items()))
        try:
            with urllib.request.urlopen(req) as r:
                self._remember(r.headers)
                return r.status, json.loads(r.read() or b"{}")
        except urllib.error.HTTPError as e:
            self._remember(e.headers)
            return e.code, json.loads(e.read() or b"{}")

    def has_cookie(self):
        return any(k.startswith("hg_") for k in self.cookies)

# create a game
st, body = Player("x" * 20).call("/api/dev", body={})
check("free game created", st == 200 and "id" in body, f"{st} {body}")
gid = body["id"]
G = f"/api/game/{gid}"

p1, p2, p3 = Player("a" * 20), Player("b" * 20), Player("c" * 20)

st, r1 = p1.call(G)
check("first phone gets seat p1", st == 200 and r1["seat"] == "p1", f"{st} {r1}")
check("p1 waits for the other seat", r1["game"]["ready"] is False)
check("seat cookie was set", p1.has_cookie())

st, r2 = p2.call(G)
check("second phone gets seat p2", st == 200 and r2["seat"] == "p2", f"{st} {r2}")
check("game is ready once both are in", r2["game"]["ready"] is True)

st, r3 = p3.call(G)
check("third phone is refused", st == 403 and r3["seat"] == "full", f"{st} {r3}")

# the seat survives losing localStorage: cookie only, no token header
st, rc = p1.call(G, send_token=False)
check("p1 keeps its seat from the cookie alone", st == 200 and rc["seat"] == "p1", f"{st} {rc}")

st, _ = p1.call(G, body={"type": "mode", "mode": "exes"})
check("p1 picks the mode", st == 200)
st, _ = p2.call(G, body={"type": "mode", "mode": "couples"})
check("the mode cannot be changed", st == 409)

leak = False
mine = []
for n in range(1, 22):
    st, v = p1.call(G)
    g = v["game"]
    if g["n"] != n:
        check(f"card {n} is current", False, f"got {g['n']}")
        break
    key, card = g["key"], g["card"]
    if not isinstance(card, str) or not card:
        check(f"card {n} has text", False)
        break

    a, b = f"p1 answer {n}", f"p2 answer {n}"
    mine.append(a)
    st, _ = p1.call(G, body={"type": "answer", "key": key, "text": a})
    if st != 200:
        check(f"p1 locks card {n}", False, st)
        break

    # the whole point of the game: p2 must not see p1's answer yet
    _, peek = p2.call(G)
    if peek["game"]["answers"].get(key) is not None:
        leak = True
        break
    if json.dumps(peek).find(a) != -1:
        leak = True
        break

    st, _ = p1.call(G, body={"type": "next", "key": key})
    if st != 409:
        check(f"p1 cannot advance alone on card {n}", False, st)
        break

    st, both = p2.call(G, body={"type": "answer", "key": key, "text": b})
    if st != 200 or both["game"]["answers"].get(key) != {"p1": a, "p2": b}:
        check(f"card {n} reveals both answers", False, f"{st} {both.get('game', {}).get('answers', {}).get(key)}")
        break

    st, _ = p1.call(G, body={"type": "next", "key": key})
    if st != 200:
        check(f"advance past card {n}", False, st)
        break
else:
    check("played all 21 cards in order", True)

check("no answer leaked before both were locked", not leak)

_, end = p1.call(G)
check("game is done after the last card", end["game"]["status"] == "done", end["game"]["status"])
check("game has not faded yet", end["game"]["faded"] is False)

st, _ = p1.call(G, body={"type": "share", "text": "p2 answer 1"})
check("cannot share the other player's answer", st == 400, st)
st, _ = p1.call(G, body={"type": "share", "text": mine[0]})
check("p1 shares one of its own", st == 200, st)
st, shared = p2.call(G, body={"type": "share", "text": "p2 answer 5"})
check("p2 shares one of its own", st == 200, st)
check("the shared card holds one answer each",
      shared["game"]["shared"] == {"p1": "p1 answer 1", "p2": "p2 answer 5"}, shared["game"]["shared"])

st, _ = p3.call(G, body={"type": "answer", "key": "0-0", "text": "sneak"})
check("a stranger still cannot write", st == 403, st)

print()
print("FAILED: " + ", ".join(fails) if fails else "all checks passed")
sys.exit(1 if fails else 0)
