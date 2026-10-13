"""
The deck, and the clock it is cut to.

Both the picture and the sound import this, so a cut and the click that lands
on it cannot drift apart: they are the same number, read twice.

100 BPM. A beat is 0.6s, a bar is 2.4s, and every slide is exactly one bar —
so every transition in the film lands on a downbeat, and the strike that marks
it is the same event, not an accompaniment to it.
"""

BPM = 100
BEAT = 60.0 / BPM          # 0.6s
BAR = 4 * BEAT             # 2.4s
FPS = 30
FRAMES_PER_BAR = round(BAR * FPS)      # 72
W, H = 1080, 1920

# section title, blurb, then (screen id, caption, one line of what it is)
DECK = [
    ("Onboarding", "Four screens to a circle", [
        ("s01-welcome",    "Prove it",        "The whole pitch in two words and one sentence"),
        ("s02-name",       "Your name",       "The name your circle sees on everything you prove"),
        ("s03-circle",     "Your circle",     "Join with a code, or start one. Four to eight people"),
        ("s04-permission", "Location",        "Asked once, at the end, with the reason in plain terms"),
    ]),
    ("The promise", "Say it before you do it", [
        ("s06-commit",  "New commitment", "Where, how often, who sees it, and the deal in three clauses"),
        ("s07-place",   "New place",      "A drawn map and a 150m ring. Your circle only sees the name"),
        ("s08-promise", "It is binding",  "A receipt for the promise, and everyone has been told"),
    ]),
    ("The proof", "A place, and a photo taken in it", [
        ("s09-watching", "In range",   "Anvil knows you are there, and says so before you shoot"),
        ("s10-captured", "The proof",  "Location, distance and time attached. It cannot be deleted"),
        ("s05-home",     "Standings",  "Streaks with a number on them, and this week under each name"),
    ]),
    ("The consequence", "What a broken promise looks like", [
        ("s11-miss",   "A Miss",     "Announced, in rust, at the top of everybody's board"),
        ("s13-week",   "The week",   "Nobody is ranked mid-week. It settles on Sunday"),
        ("s12-streak", "The record", "Every square is a day with a photo and a location behind it"),
    ]),
    ("The circle", "The people who notice", [
        ("s14-circle", "Geeked",     "Six people, and what each of them is carrying"),
        ("s15-invite", "The invite", "A code that dies in a day, and only two seats left"),
        ("s16-member", "A member",   "Their commitments, their record, their last proof"),
        ("s17-board",  "All time",   "Longest unbroken run. Volume is not the point"),
    ]),
    ("The routine", "What you owe this week", [
        ("s18-routine",     "Due today",    "One card, one action, and the week under it"),
        ("s20-commitments", "Promises",     "Three live, one retired, each with its own streak"),
        ("s19-detail",      "A commitment", "Eight weeks of it, and the way out if you need one"),
    ]),
    ("You", "Your own record", [
        ("s21-profile",  "You",              "Two misses in nine weeks. Both were Fridays"),
        ("s22-settings", "Settings",         "Short, because there is not much to configure"),
        ("s23-privacy",  "What Anvil knows", "Three things shared, two things never collected"),
    ]),
]

# The sub note under each section. It moves, so seven sections do not sound
# like one long drone, but it stays in one mode so it never sounds like a
# key change either.
SECTION_ROOT = [55.00, 55.00, 48.99, 65.41, 48.99, 55.00, 41.20]   # A1 A1 G1 C2 G1 A1 E1


def sequence():
    """Every slide in order: (kind, slide_id, section_index).

    kind is 'card' or 'screen', which is the whole reason the two transitions
    can sound different: a section change is a bigger event than a page turn,
    so it gets a bigger sound.
    """
    out, n = [], 0
    for si, (sec, blurb, screens) in enumerate(DECK):
        out.append(("card", f"c{n}", si)); n += 1
        for _ in screens:
            out.append(("screen", f"s{n}", si)); n += 1
    return out


N_BARS = len(sequence())
DURATION = N_BARS * BAR
