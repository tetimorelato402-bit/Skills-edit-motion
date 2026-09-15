# hey again. — carousel pipeline

Brand rules (never change):
- Tangerine #D8652B, cream #F4EEE4 text, font assets/Inter-Medium.ttf, caption centered.
- Every slide is 4:5 (2160x2700). Video slides are 3 seconds with a silent audio track.
- Background fills the frame, slightly blurred, with a tangerine overlay (~35% opacity) so every slide reads as our orange.
- Slides marked "flat tangerine, no scene" are a solid #D8652B card with the caption only.
- No logos, no mirror, no people, no visible text in backgrounds.

Source: Pexels API (photos + videos). Key is in .env as PEXELS_API_KEY.

Layout: captions/posts.json = 25 posts, 5 slides each (caption + background_prompt).
Output: output/postXX/1..5. Slides 1 and 3 are videos (Pexels video, or photo with a slow 3s ffmpeg zoom). Others are photos.

Dependencies: ffmpeg, python3, pillow, numpy, requests.
