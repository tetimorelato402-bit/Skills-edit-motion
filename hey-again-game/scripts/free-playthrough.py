"""Plays the free game against a running server, as two phones would.

    npm run demo                            # terminal 1, no database needed
    python3 scripts/free-playthrough.py http://localhost:3000

The free game is a product, not a trial flag: it must be five cards, the same
five for everyone, and it must end. Exits non-zero on the first broken promise.
"""
import json, sys, urllib.request, urllib.error

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:3000"
fails = []

def check(name, cond, detail=""):
    print(("  ok   " if cond else "  FAIL ") + name + ("" if cond else f"  <- {detail}"))
    if not cond:
        fails.append(name)

class Player:
    def __init__(self, token):
        self.token = token
        self.cookies = {}

    def _remember(self, headers):
        for raw in headers.get_all("Set-Cookie") or []:
            pair = raw.split(";", 1)[0]
            if "=" in pair:
                k, v = pair.split("=", 1)
                self.cookies[k.strip()] = v.strip()

    def call(self, path, body=None):
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(BASE + path, data=data, method="POST" if body is not None else "GET")
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

# the free door on the landing page: a plain form post, no keys, no stripe
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k): return None

opener = urllib.request.build_opener(NoRedirect)
req = urllib.request.Request(BASE + "/api/free", data=b"", method="POST")
try:
    with opener.open(req) as r:
        status, location = r.status, r.headers.get("Location", "")
except urllib.error.HTTPError as e:
    status, location = e.code, e.headers.get("Location", "")

check("free game created without paying", status == 303 and "/start?game=" in location, f"{status} {location}")
if fails:
    sys.exit("could not start a free game")
gid = location.split("game=", 1)[1].split("&")[0]
G = f"/api/game/{gid}"

p1, p2 = Player("f" * 20), Player("g" * 20)
st, r1 = p1.call(G)
check("first phone gets a seat", st == 200 and r1["seat"] == "p1", f"{st} {r1}")
st, r2 = p2.call(G)
check("second phone gets the other", st == 200 and r2["seat"] == "p2", f"{st} {r2}")
check("a free game still only seats two", p1.call(G)[1]["seat"] == "p1")
st, third = Player("h" * 20).call(G)
check("third phone is refused", st == 403 and third["seat"] == "full", f"{st} {third}")

st, _ = p1.call(G, body={"type": "mode", "mode": "couples"})
check("mode picked", st == 200)

st, v = p1.call(G)
check("a free game says it is five cards long", v["game"]["total"] == 5, v["game"]["total"])
check("and knows it is the free tier", v["game"]["tier"] == "free", v["game"].get("tier"))

asked, leak = [], False
for n in range(1, 6):
    st, v = p1.call(G)
    g = v["game"]
    if g["n"] != n:
        check(f"card {n} is current", False, f"got {g['n']}")
        break
    asked.append(g["card"])
    st, _ = p1.call(G, body={"type": "answer", "key": g["key"], "text": f"p1 free {n}"})
    if st != 200:
        check(f"p1 locks card {n}", False, st)
        break
    _, peek = p2.call(G)
    if peek["game"]["answers"].get(g["key"]) is not None:
        leak = True
        break
    st, _ = p2.call(G, body={"type": "answer", "key": g["key"], "text": f"p2 free {n}"})
    if st != 200:
        check(f"p2 locks card {n}", False, st)
        break
    st, _ = p1.call(G, body={"type": "next", "key": g["key"]})
    if st != 200:
        check(f"advance past card {n}", False, st)
        break
else:
    check("played all 5 cards in order", True)

check("no answer leaked before both were locked", not leak)
check("five distinct cards", len(set(asked)) == 5, asked)

_, done = p1.call(G)
check("the game is over after five", done["game"]["status"] == "done", done["game"]["status"])

# the whole point of a fixed free set: the next pair gets exactly these five
req2 = urllib.request.Request(BASE + "/api/free", data=b"", method="POST")
try:
    with opener.open(req2) as r:
        loc2 = r.headers.get("Location", "")
except urllib.error.HTTPError as e:
    loc2 = e.headers.get("Location", "")
if "/start?game=" in loc2:
    gid2 = loc2.split("game=", 1)[1].split("&")[0]
    H = f"/api/game/{gid2}"
    q1, q2 = Player("i" * 20), Player("j" * 20)
    q1.call(H); q2.call(H)
    q1.call(H, body={"type": "mode", "mode": "couples"})
    second = []
    for n in range(1, 6):
        _, v = q1.call(H)
        g = v["game"]
        second.append(g["card"])
        q1.call(H, body={"type": "answer", "key": g["key"], "text": "a"})
        q2.call(H, body={"type": "answer", "key": g["key"], "text": "b"})
        q1.call(H, body={"type": "next", "key": g["key"]})
    check("every free game is the same five, in the same order", second == asked, f"{second} != {asked}")
else:
    check("second free game created", False, loc2)

print()
if fails:
    print("FAILED: " + ", ".join(fails))
    sys.exit(1)
print("all checks passed")
