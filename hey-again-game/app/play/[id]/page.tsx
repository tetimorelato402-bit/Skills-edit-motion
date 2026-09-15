import Play from "./play";
export default function Page({ params }: { params: { id: string } }) { return <Play id={params.id} />; }
