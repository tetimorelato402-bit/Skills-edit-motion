"""hey again. — the eight decks.

Everything maps back to the three product categories: general (the stranger deck, never
named that on camera), ex, and couple. `lead` is the small line above the title, `subject`
is the big one. Five questions per deck, all forty distinct: the reel takes the first
three, the carousel takes all five.
"""

DECKS = [
    dict(key="partner", cat="couple", lead="questions for", subject="your partner",
         questions=[
             "what have you forgiven me for without telling me?",
             "when do you feel furthest from me?",
             "what have you stopped telling me?",
             "what version of me are you scared of losing?",
             "what do you wish i asked you more often?",
         ]),
    dict(key="ex", cat="ex", lead="questions for", subject="your ex",
         questions=[
             "what did you know before i did?",
             "when did you stop trying?",
             "who did you tell first?",
             "do you still defend me to people?",
             "what would you do differently?",
         ]),
    dict(key="general", cat="general", lead="a round of", subject="general questions",
         questions=[
             "what are you pretending not to need?",
             "who would you call at 3am?",
             "what would you change if nobody found out?",
             "what do you want someone to ask you?",
             "when did you last surprise yourself?",
         ]),
    dict(key="situationship", cat="couple", lead="questions for", subject="your situationship",
         questions=[
             "what are we when nobody is watching?",
             "who have you told about me?",
             "what are you waiting for?",
             "are you keeping me or keeping your options?",
             "what would make you leave?",
         ]),
    dict(key="firstdate", cat="general", lead="questions for", subject="a first date",
         questions=[
             "what is the fastest way to lose you?",
             "what do you lie about on purpose?",
             "what are you hoping i do not ask?",
             "how do you know when you are done?",
             "what did your last person teach you?",
         ]),
    dict(key="bestfriend", cat="general", lead="questions for", subject="your best friend",
         questions=[
             "what do you protect me from?",
             "when did you last lie to spare me?",
             "who am i when i am not around?",
             "what have i never thanked you for?",
             "what would you never say to my face?",
         ]),
    dict(key="gotaway", cat="ex", lead="questions for", subject="your almost",
         questions=[
             "what were you waiting for me to say?",
             "would you have stayed if i asked?",
             "how long did you keep the door open?",
             "what do you still not tell anyone?",
             "where do you think we would be?",
         ]),
    dict(key="someonenew", cat="couple", lead="questions for", subject="someone new",
         questions=[
             "what should i know before i fall for you?",
             "what do people get wrong about you first?",
             "what are you still carrying?",
             "how much are you willing to want this?",
             "what would you need me to be patient with?",
         ]),
]

BY_KEY = {d["key"]: d for d in DECKS}

# forty questions, no repeats — worth asserting, since a duplicate across decks would
# quietly ship as two identical slides in two different posts
_all = [q for d in DECKS for q in d["questions"]]
assert len(_all) == len(set(_all)) == 40, "deck questions must be unique"
