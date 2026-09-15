import Link from "next/link";
export default function NotFound() {
  return (
    <main className="wrap fade">
      <h1 className="q">there's nothing here.</h1>
      <p className="small">The link might be mistyped, or it was never a link at all.</p>
      <Link className="btn" href="/">start a game</Link>
    </main>
  );
}
