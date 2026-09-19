"""Minimal TrueType metrics reader.

Only what the reel needs: how wide a string is, and where a given character sits inside
it. Pillow is not installable in this sandbox, so the advance widths come straight out of
the font's own hmtx/cmap tables.
"""
import struct


class Font:
    def __init__(self, path):
        self.data = open(path, "rb").read()
        self.tables = {}
        num = struct.unpack(">H", self.data[4:6])[0]
        for i in range(num):
            off = 12 + i * 16
            tag = self.data[off:off + 4].decode("latin-1")
            start, length = struct.unpack(">II", self.data[off + 8:off + 16])
            self.tables[tag] = (start, length)

        head = self.tables["head"][0]
        self.upem = struct.unpack(">H", self.data[head + 18:head + 20])[0]

        hhea = self.tables["hhea"][0]
        self.num_h = struct.unpack(">H", self.data[hhea + 34:hhea + 36])[0]
        self.ascender = struct.unpack(">h", self.data[hhea + 4:hhea + 6])[0]
        self.descender = struct.unpack(">h", self.data[hhea + 6:hhea + 8])[0]

        self.cmap = self._cmap()
        self.adv = self._hmtx()

    def _cmap(self):
        start = self.tables["cmap"][0]
        n = struct.unpack(">H", self.data[start + 2:start + 4])[0]
        best = None
        for i in range(n):
            off = start + 4 + i * 8
            pid, eid, sub = struct.unpack(">HHI", self.data[off:off + 8])
            fmt = struct.unpack(">H", self.data[start + sub:start + sub + 2])[0]
            if fmt == 4 and (pid, eid) in ((3, 1), (0, 3), (0, 4), (3, 10), (0, 6)):
                best = start + sub
                break
        if best is None:
            raise ValueError("no format-4 cmap")
        segx2 = struct.unpack(">H", self.data[best + 6:best + 8])[0]
        seg = segx2 // 2
        base = best + 14
        ends = struct.unpack(f">{seg}H", self.data[base:base + segx2])
        starts = struct.unpack(f">{seg}H", self.data[base + segx2 + 2:base + 2 * segx2 + 2])
        deltas = struct.unpack(f">{seg}h", self.data[base + 2 * segx2 + 2:base + 3 * segx2 + 2])
        ro_at = base + 3 * segx2 + 2
        ranges = struct.unpack(f">{seg}H", self.data[ro_at:ro_at + segx2])

        m = {}
        for i in range(seg):
            for c in range(starts[i], min(ends[i], 0xFFFF) + 1):
                if ranges[i] == 0:
                    g = (c + deltas[i]) & 0xFFFF
                else:
                    gi = ro_at + i * 2 + ranges[i] + (c - starts[i]) * 2
                    if gi + 2 > len(self.data):
                        continue
                    g = struct.unpack(">H", self.data[gi:gi + 2])[0]
                    if g:
                        g = (g + deltas[i]) & 0xFFFF
                if g:
                    m[c] = g
        return m

    def _hmtx(self):
        start = self.tables["hmtx"][0]
        adv, last = {}, 0
        for i in range(self.num_h):
            last = struct.unpack(">H", self.data[start + i * 4:start + i * 4 + 2])[0]
            adv[i] = last
        self.default_adv = last
        return adv

    def advance(self, ch, size):
        g = self.cmap.get(ord(ch))
        a = self.adv.get(g, self.default_adv) if g is not None else self.default_adv
        return a * size / self.upem

    def width(self, text, size):
        return sum(self.advance(c, size) for c in text)

    def char_x(self, text, index, size):
        """Left edge and width of the character at `index`, relative to the string start."""
        left = self.width(text[:index], size)
        return left, self.advance(text[index], size)

    def baseline(self, top_y, size):
        """drawtext places the box top at `top_y`; the baseline sits an ascender below."""
        return top_y + self.ascender * size / self.upem

    def line_h(self, size):
        return (self.ascender - self.descender) * size / self.upem
