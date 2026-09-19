"""hey again. — the eight topics.

Everything maps back to the three product categories: general (the stranger deck, never
named that on camera), ex, and couple.

Each topic carries two separate question sets, because a reel and a post are two pieces of
content and must never ask the same thing:

    reel  three questions, typed out in the video
    post  five questions, one per slide on the carousel

`sub` is the single line under the wordmark on the carousel title card. `lead`/`subject`
are the two stacked lines the reel's theme card uses.
"""

DECKS = [
    dict(key="partner", sub="questions for your partner", cat="couple",
         lead="questions for", subject="your partner",
         reel=[
             "what have you forgiven me for without telling me?",
             "when do you feel furthest from me?",
             "what have you stopped telling me?",
         ],
         post=[
             "what part of me do you edit for other people?",
             "when did you last choose me out loud?",
             "what would you never let me read?",
             "what am i taking for granted right now?",
             "what do you need me to notice?",
         ]),
    dict(key="ex", sub="questions for your ex", cat="ex",
         lead="questions for", subject="your ex",
         reel=[
             "what did you know before i did?",
             "when did you stop trying?",
             "who did you tell first?",
         ],
         post=[
             "what version of the story do you tell?",
             "what did i never apologise for?",
             "when did you know it was over?",
             "what do you miss that you would never admit?",
             "what should i stop doing to the next person?",
         ]),
    dict(key="general", sub="general questions", cat="general",
         lead="a round of", subject="general questions",
         reel=[
             "what are you pretending not to need?",
             "who would you call at 3am?",
             "what would you change if nobody found out?",
         ],
         post=[
             "what do you do when nobody is keeping score?",
             "what compliment do you not believe?",
             "who are you still trying to prove wrong?",
             "what would you do with one honest day?",
             "what do you want to be asked at 40?",
         ]),
    dict(key="situationship", sub="questions for your situationship", cat="couple",
         lead="questions for", subject="your situationship",
         reel=[
             "what are we when nobody is watching?",
             "who have you told about me?",
             "what are you waiting for?",
         ],
         post=[
             "what would you call this out loud?",
             "who would you pick if you had to choose today?",
             "what are you protecting by not naming it?",
             "would you be jealous or relieved?",
             "what happens to us in six months?",
         ]),
    dict(key="firstdate", sub="questions for a first date", cat="general",
         lead="questions for", subject="a first date",
         reel=[
             "what is the fastest way to lose you?",
             "what do you lie about on purpose?",
             "what are you hoping i do not ask?",
         ],
         post=[
             "what do you want me to ask twice?",
             "what are you done pretending about?",
             "what would your friends warn me about?",
             "when did you last change your mind about someone?",
             "what makes you stay past the awkward part?",
         ]),
    dict(key="bestfriend", sub="questions for your best friend", cat="general",
         lead="questions for", subject="your best friend",
         reel=[
             "what do you protect me from?",
             "when did you last lie to spare me?",
             "who am i when i am not around?",
         ],
         post=[
             "what have you watched me do too many times?",
             "when did i last disappoint you?",
             "what do you envy about my life?",
             "who do you think i should have left?",
             "what would you tell me if i could take it?",
         ]),
    dict(key="gotaway", sub="questions for your almost", cat="ex",
         lead="questions for", subject="your almost",
         reel=[
             "what were you waiting for me to say?",
             "would you have stayed if i asked?",
             "how long did you keep the door open?",
         ],
         post=[
             "what almost happened that i missed?",
             "who ended it, really?",
             "what do you do when a song comes on?",
             "would you pick up if i called tonight?",
             "what did you never let yourself want?",
         ]),
    dict(key="someonenew", sub="questions for someone new", cat="couple",
         lead="questions for", subject="someone new",
         reel=[
             "what should i know before i fall for you?",
             "what do people get wrong about you first?",
             "what are you still carrying?",
         ],
         post=[
             "what are you hoping i am different about?",
             "what would make you stop trying?",
             "how do you know when you trust someone?",
             "what part of your past should i not touch yet?",
             "what are you scared this becomes?",
         ]),
]

BY_KEY = {d["key"]: d for d in DECKS}

# Sixty-four questions, none repeated — asserted rather than trusted, because a question
# shared between a reel and its own post is exactly the duplicate nobody notices until it
# is live, and one shared across topics ships as the same slide in two different posts.
_all = [q for d in DECKS for q in d["reel"] + d["post"]]
assert len(_all) == 64, f"expected 64 questions, got {len(_all)}"
assert len(set(_all)) == 64, "questions must be unique across every reel and post"
