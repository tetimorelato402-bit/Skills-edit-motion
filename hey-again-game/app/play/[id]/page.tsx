import Play from "./play";
import { againLink, paymentLink } from "@/lib/env";

export default function Page({ params }: { params: { id: string } }) {
  // built on the server: the client never needs to know the payment link shape
  return <Play id={params.id} again={againLink(params.id)} buy={paymentLink()} />;
}
