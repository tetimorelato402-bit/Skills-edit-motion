import { test, describe } from "node:test";
import assert from "node:assert/strict";
import { hit, callerKey, type Bucket } from "./ratelimit.ts";

const NOW = 1_000_000;
const store = () => new Map<string, Bucket>();

describe("hit", () => {
  test("allows up to max in a window, then refuses", () => {
    const s = store();
    for (let i = 0; i < 3; i++) assert.equal(hit(s, "ip", 3, 1000, NOW).ok, true, `call ${i}`);
    const over = hit(s, "ip", 3, 1000, NOW);
    assert.equal(over.ok, false);
    assert.equal(over.retryAfter, 1);
  });

  test("keys are independent", () => {
    const s = store();
    assert.equal(hit(s, "a", 1, 1000, NOW).ok, true);
    assert.equal(hit(s, "a", 1, 1000, NOW).ok, false);
    assert.equal(hit(s, "b", 1, 1000, NOW).ok, true);
  });

  test("the window reopens", () => {
    const s = store();
    assert.equal(hit(s, "ip", 1, 1000, NOW).ok, true);
    assert.equal(hit(s, "ip", 1, 1000, NOW + 999).ok, false);
    assert.equal(hit(s, "ip", 1, 1000, NOW + 1000).ok, true);
  });

  test("reports whole seconds until the window reopens", () => {
    const s = store();
    hit(s, "ip", 1, 60_000, NOW);
    assert.equal(hit(s, "ip", 1, 60_000, NOW + 1_500).retryAfter, 59);
  });

  test("sweeps expired buckets instead of growing forever", () => {
    const s = store();
    for (let i = 0; i < 5001; i++) hit(s, "k" + i, 1, 1000, NOW);
    assert.equal(s.size > 5000, true);
    hit(s, "later", 1, 1000, NOW + 2000);
    assert.equal(s.size, 1);
  });
});

describe("callerKey", () => {
  const req = (h: Record<string, string>) => new Request("https://x.test", { headers: h });
  test("takes the first forwarded address", () => {
    assert.equal(callerKey(req({ "x-forwarded-for": "1.2.3.4, 5.6.7.8" })), "1.2.3.4");
  });
  test("falls back to x-real-ip, then unknown", () => {
    assert.equal(callerKey(req({ "x-real-ip": "9.9.9.9" })), "9.9.9.9");
    assert.equal(callerKey(req({})), "unknown");
  });
});
