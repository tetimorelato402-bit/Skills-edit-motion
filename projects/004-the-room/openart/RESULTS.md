# OpenArt run 1 — eight plates, all Seedance 2.0, text2video, 720p 9:16 5s, no audio

Generated 2026-09-04. **Nothing here has been viewed from this session** — `cdn.openart.ai`
is denied by the egress proxy on every route (curl and WebFetch alike), so these are
recorded by historyId for teti to judge in the OpenArt UI.

| # | section of the film | historyId | outputs |
|---|---|---|---|
| 1 | the room — wide pull-back through the crowd | `MPGGuKeL7DFePUbdYQyj` | 1 |
| 2 | booth — CDJs, jog wheels, hands | `pIv2kT4GgdZQB2BxsrAC` | 1 |
| 3 | the drop — strobes, CO2, crowd mid-jump | `17O5OMSyd6MJYAol6IMM` | 1 |
| 4 | the build — near black, one strobe, smoke | `lx3Pd27a5zxHFhNAS6l7` | 1 |
| 5 | the waveform corridor — magenta LED columns | `ntSVl3tMdeLCwF7xcVHu` | 1 |
| 6 | the room again, 3 variants, seed 4210 | `deRekASjPOjDdYccaZUz` | 3 |

**Spend: 8 clips × 360 credits = 2,880.** (720p/5s/9:16/no audio is 400 list, and this Pro
account is charged round(400 × 0.9) = 360 each.) 1080p would be 900 each.

## What these are and are not

They are **text2video** — no reference. They test whether the *look* lands: the Good Girl
palette, the direct-flash nightlife photography, the fisheye club. They do **not** inherit
`the-room-v1.mp4`'s composition, camera or timing, because OpenArt has no video-to-video
restyle mode and because the 1080x1920 master is over Seedance's 720p reference cap.

The reference pass needs `room-ref-720p-room-section.mp4` uploaded from teti's side —
this session has no upload tool.

## The thing worth deciding before spending more

Generated footage cannot carry the beat-locked shake; that came from the 128 grid, not from
pixels. So the question is not "replace the render with this" but **which of the two is the
plate and which is the treatment**:

- **Generated as the world, render as the overlay.** Use a plate like #1 as the club, and
  composite the render's paint strokes, waveform bars and specimen annotations over it.
  Keeps teti's language, buys photoreal depth.
- **Render as the world, generated as inserts.** Keep the film exactly as cut and drop
  generated shots in as 2-4 beat cutaways on the downbeats. Sync survives everywhere.

The second is safer and the first is more striking. It is teti's call, and it is worth
making before more credits go anywhere.
