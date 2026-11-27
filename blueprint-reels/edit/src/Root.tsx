import React from 'react';
import { AbsoluteFill, Composition, Sequence } from 'remotion';
import { Fonts } from './fonts';
import { C, FPS, H, W } from './theme';
import { HookCaption, Subtitle, TitleCard } from './kit/Type';
import { ChatScreen, FloatingBubble } from './kit/Chat';
import { CallFrame, FingerprintStamp, IDEAS, NdaScreen, NewIdeaForm, Placeholder, ReviewScreen, SearchScreen, SoldScreen } from './kit/App';
import { EndCard } from './kit/EndCard';

const Frame: React.FC<{ children: React.ReactNode; bg?: string }> = ({ children, bg = '#000' }) => (
  <Fonts>
    <AbsoluteFill style={{ background: bg }}>{children}</AbsoluteFill>
  </Fonts>
);

// ---------------------------------------------------------------- kit pieces (each its own composition)
const KitCaption = () => (
  <Frame bg="linear-gradient(170deg,#1B2A7A,#0A1446)">
    <Placeholder label="AI shot goes here" />
    <HookCaption text="When you share your business idea in the group chat" extra="…and then you sell it" extraFrom={20} />
    <Subtitle text="So! What's the new idea?" from={0} to={999} />
  </Frame>
);

const KitChat = () => (
  <Frame>
    <ChatScreen
      messages={[
        { at: 0, from: 'me', text: "ok hear me out. a swap shelf for neighbors' spare pantry stuff" },
        { at: 6, from: 'tay', text: 'bro 😭' },
        { at: 18, from: 'marcus', text: "just say you're hungry" },
        { at: 30, from: 'priya', text: 'who would pay for that' },
        { at: 42, from: 'marcus', text: 'next idea pls' },
        { at: 52, from: 'tay', sticker: '💀' },
      ]}
      typing={[{ from: 'priya', start: 54, end: 60 }]}
    />
  </Frame>
);

const KitBubble = () => (
  <Frame>
    <Placeholder label="F01-S02 · Jordan's eyes (AI)" />
    <FloatingBubble text="LMAOOO 💀" at={0} from="tay" />
  </Frame>
);

const KitForm = () => (
  <Frame>
    <NewIdeaForm what={IDEAS.larder.pitch} start={0} />
  </Frame>
);
const KitStamp = () => (
  <Frame>
    <FingerprintStamp idea={IDEAS.larder} at={3} />
  </Frame>
);
const KitReview = () => (
  <Frame>
    <ReviewScreen idea={IDEAS.larder} checks={[3, 9]} liveAt={20} />
  </Frame>
);
const KitSearch = () => (
  <Frame>
    <SearchScreen idea={IDEAS.larder} query="pantry" start={1} />
  </Frame>
);
const KitNda = () => (
  <Frame>
    <NdaScreen idea={IDEAS.larder} signStart={0} signFrames={18} buyAt={25} chipAt={28} />
  </Frame>
);
const KitSold = () => (
  <Frame>
    <SoldScreen idea={IDEAS.larder} at={0} />
  </Frame>
);
const KitCall = () => (
  <Frame>
    <CallFrame main={<Placeholder label="Rosa on the call (AI clip)" tone="#2A2F5E" />} self={<Placeholder label="Jordan (AI clip)" />} />
  </Frame>
);
const KitLater = () => (
  <Frame>
    <TitleCard text="Later." />
  </Frame>
);
const KitDinner = () => (
  <Frame>
    <TitleCard text="Next family dinner." />
  </Frame>
);

// End card on its own: 120 frames = AT .. end of film. on = 10 (film 01) / 9 (films 02-04).
const EndCard01 = () => (
  <Frame bg={C.blue}>
    <EndCard on={10} />
  </Frame>
);
const EndCard02 = () => (
  <Frame bg={C.blue}>
    <EndCard on={9} />
  </Frame>
);

const kit: [string, React.FC, number][] = [
  ['KitCaption', KitCaption, 40],
  ['KitChat', KitChat, 70],
  ['KitBubble', KitBubble, 20],
  ['KitForm', KitForm, 30],
  ['KitStamp', KitStamp, 20],
  ['KitReview', KitReview, 30],
  ['KitSearch', KitSearch, 30],
  ['KitNda', KitNda, 40],
  ['KitSold', KitSold, 30],
  ['KitCall', KitCall, 10],
  ['KitLater', KitLater, 18],
  ['KitDinner', KitDinner, 18],
  ['EndCard01', EndCard01, 120],
  ['EndCard02', EndCard02, 120],
];

export const Root: React.FC = () => (
  <>
    {kit.map(([id, comp, dur]) => (
      <Composition key={id} id={id} component={comp} durationInFrames={dur} fps={FPS} width={W} height={H} />
    ))}
  </>
);

export { Sequence };
