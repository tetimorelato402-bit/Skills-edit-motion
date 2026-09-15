// A seat is held by a random token. The browser keeps it in localStorage and the
// server also drops it in an httpOnly cookie, so clearing one does not lose the
// seat. Either source proves the same thing: you were here first.
export const TOKEN_RE = /^[A-Za-z0-9_-]{16,64}$/;

export const cookieName = (gameId: string) => `hg_${gameId.replace(/-/g, "")}`;

export function readCookie(header: string | null, name: string): string | null {
  if (!header) return null;
  for (const part of header.split(";")) {
    const i = part.indexOf("=");
    if (i < 0) continue;
    if (part.slice(0, i).trim() === name) return decodeURIComponent(part.slice(i + 1).trim());
  }
  return null;
}

// cookie first: it survives a cleared localStorage and cannot be read by script.
export function seatToken(cookieHeader: string | null, headerToken: string | null, gameId: string): string | null {
  const fromCookie = readCookie(cookieHeader, cookieName(gameId));
  if (fromCookie && TOKEN_RE.test(fromCookie)) return fromCookie;
  if (headerToken && TOKEN_RE.test(headerToken)) return headerToken;
  return null;
}
