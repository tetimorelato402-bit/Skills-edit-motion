import { test, describe } from "node:test";
import assert from "node:assert/strict";
import { cookieName, readCookie, seatToken, TOKEN_RE } from "./seat.ts";

const ID = "11111111-2222-3333-4444-555555555555";
const NAME = cookieName(ID);
const A = "aaaaaaaaaaaaaaaaaaaa";
const B = "bbbbbbbbbbbbbbbbbbbb";

describe("cookieName", () => {
  test("is a legal cookie name derived from the id", () => {
    assert.equal(NAME, "hg_11111111222233334444555555555555");
    assert.match(NAME, /^[A-Za-z0-9_]+$/);
  });
  test("differs per game", () => assert.notEqual(NAME, cookieName("99999999-2222-3333-4444-555555555555")));
});

describe("readCookie", () => {
  test("finds a value among others", () => {
    assert.equal(readCookie(`other=1; ${NAME}=${A}; last=2`, NAME), A);
  });
  test("tolerates spacing and missing values", () => {
    assert.equal(readCookie(`${NAME}=${A}`, NAME), A);
    assert.equal(readCookie("novalue; x=1", NAME), null);
    assert.equal(readCookie(null, NAME), null);
  });
  test("does not match a name that merely ends with it", () => {
    assert.equal(readCookie(`not_${NAME}=${A}`, NAME), null);
  });
});

describe("seatToken", () => {
  test("prefers the cookie over the header", () => {
    assert.equal(seatToken(`${NAME}=${A}`, B, ID), A);
  });
  test("falls back to the header on a first visit", () => {
    assert.equal(seatToken(null, B, ID), B);
    assert.equal(seatToken("unrelated=1", B, ID), B);
  });
  test("rejects malformed tokens from either source", () => {
    assert.equal(seatToken(null, "short", ID), null);
    assert.equal(seatToken(null, "has spaces and is long enough", ID), null);
    assert.equal(seatToken(null, "x".repeat(65), ID), null);
    assert.equal(seatToken(`${NAME}=nope`, null, ID), null);
  });
  test("accepts a crypto.randomUUID token", () => {
    const uuid = crypto.randomUUID();
    assert.match(uuid, TOKEN_RE);
    assert.equal(seatToken(null, uuid, ID), uuid);
  });
  test("is null when nothing is supplied", () => assert.equal(seatToken(null, null, ID), null));
});
