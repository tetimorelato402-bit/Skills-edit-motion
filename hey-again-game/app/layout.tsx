import "./globals.css";
export const metadata = { title: "hey again. the game", description: "One link. Two people. Same question, answered in secret, revealed together." };
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (<html lang="en"><head><link rel="preconnect" href="https://fonts.googleapis.com" /><link href="https://fonts.googleapis.com/css2?family=Inter:wght@500&display=swap" rel="stylesheet" /></head><body><a className="mark" href="/">hey again.</a>{children}</body></html>);
}
