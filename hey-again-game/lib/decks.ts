export type Mode = "couples" | "exes" | "strangers";
export const MODES: { id: Mode; label: string; line: string }[] = [
  { id: "couples", label: "Couples", line: "warm. the things you assume they already know." },
  { id: "exes", label: "Exes", line: "honest. the things you never said out loud." },
  { id: "strangers", label: "Strangers", line: "playful. the things you'd say before you knew better." },
];
export const ROUNDS = ["before", "between", "again"];
// 3 rounds x 7 cards. Cards starting with "dare:" are typed dares, never physical.
export const DECKS: Record<Mode, string[][]> = {
  couples: [
    ["what did you notice about me first?", "what did you think i thought of you?", "what's a small thing i do that you'd miss?", "when did you first feel safe with me?", "what did you almost not tell me early on?", "dare: describe our first kiss in one sentence, no names.", "what did you think this would be, back then?"],
    ["what's something i did that hurt and you never said?", "when did you feel furthest from me?", "what do you protect me from knowing?", "what do i get wrong about you?", "what's the fight we keep having, underneath?", "dare: send the last photo of us you didn't delete.", "what do you need more of from me? one thing."],
    ["if we met today, would you say hey?", "what's the version of us you're afraid of?", "what's the version of us you want?", "what do you still not believe about me?", "what will you remember about this year?", "dare: write the text you'd send me if i moved away tomorrow.", "say the thing. the one you've been holding."],
  ],
  exes: [
    ["what did you notice about me first?", "what did you tell your friends about me?", "what's the moment you knew?", "what did i get right, at the start?", "what did you pretend not to see?", "dare: describe the last good day in one sentence.", "what did you think this would be, back then?"],
    ["what's something i did that hurt and you never said?", "when did it actually end for you?", "what did you lie about?", "what do you think i lied about?", "what did you keep of mine?", "dare: send the last photo of us you didn't delete.", "what would you have done differently? one thing."],
    ["if we met today, would you say hey?", "what do you still not believe about me?", "what are you grateful i did?", "what are you grateful you left?", "what do you hope i think of you?", "dare: write the text you almost sent and deleted.", "say the thing. the one you've been holding."],
  ],
  strangers: [
    ["what did you notice about me first?", "what's a thing you assumed about me?", "what do people get wrong about you?", "what's your most on-purpose habit?", "what would your 16-year-old self say about tonight?", "dare: describe me in three words, no compliments.", "what did you think this would be, back then?"],
    ["what's a thing you stopped telling people?", "when did you last feel like a kid?", "what's the idea you shelved?", "what are you avoiding this week?", "who did you stop texting on purpose?", "dare: send a photo of the room you're in, no cleaning up.", "what do you need more of? one thing."],
    ["if we met again in five years, would you say hey?", "what are you scared you'll become?", "what are you scared you won't?", "what do you want me to remember about you?", "what will you remember about this?", "dare: write the text you'd send me tomorrow morning.", "say the thing. the one you've been holding."],
  ],
};
