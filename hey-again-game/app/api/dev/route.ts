import { NextResponse } from "next/server";
import { admin } from "@/lib/supabase";
// creates a free game for testing. disabled unless DEV_FREE=true
export async function POST() {
  if (process.env.DEV_FREE !== "true") return NextResponse.json({ error: "off" }, { status: 403 });
  const { data } = await admin().from("games").insert({}).select("id").single();
  return NextResponse.json({ id: data!.id });
}
