import { devFree } from "@/lib/env";

export default function Home({ searchParams }: { searchParams: { error?: string } }) {
  const dev = devFree();
  return (
    <main className="wrap fade">
      <h1 className="q">one link. two people. the same question, answered in secret, revealed at the same time.</h1>
      <p className="small">21 cards, about 20 minutes. Pick couples, exes or strangers. Nobody can change their answer after seeing yours. That&apos;s the game.</p>
      <form action="/api/checkout" method="POST"><button className="btn" type="submit">play it with them, $2.99</button></form>
      {searchParams.error === "checkout" && <p className="small" role="alert" style={{ marginTop: 16 }}>checkout didn&apos;t open. try again in a moment.</p>}
      {dev && <a className="small" style={{ marginTop: 18, display: "block" }} href="/start">testing: start a free game</a>}
      <p className="progress">you get one link. it opens for exactly one other person. then it locks.</p>
    </main>
  );
}
