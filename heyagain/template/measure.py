"""Find the ink bounding box of a glyph as ffmpeg actually draws it."""
import subprocess, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
SP = os.path.dirname(os.path.abspath(__file__))
FF = f"{SP}/tools/ffmpeg-master-latest-linux64-gpl/bin/ffmpeg"
FONT = "/home/user/Skills-edit-motion/heyagain/assets/Inter-Medium.ttf"

def ink(ch, size, x, y, W=1080, H=1920):
    """Render one glyph white-on-black and scan the raw gray plane for its extent."""
    p = subprocess.run(
        [FF, "-v", "error", "-f", "lavfi", "-i", f"color=c=black:s={W}x{H}",
         "-vf", (f"drawtext=fontfile='{FONT}':text='{ch}':fontcolor=white:fontsize={int(size)}"
                 f":x={int(x)}:y={int(y)}"),
         "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "gray", "-"],
        stdout=subprocess.PIPE, check=True).stdout
    xs, ys = [], []
    for row in range(H):
        base = row * W
        line = p[base:base + W]
        if max(line) > 60:
            ys.append(row)
            for col in range(W):
                if line[col] > 60:
                    xs.append(col)
    if not xs:
        return None
    return min(xs), min(ys), max(xs), max(ys)


def ink_region(text, size, x, y, x_from=0, x_to=10**9, y_from=0, W=1080, H=1920, thr=60):
    """Ink bbox of `text` restricted to a window, so one glyph can be isolated."""
    p = subprocess.run(
        [FF, "-v", "error", "-f", "lavfi", "-i", f"color=c=black:s={W}x{H}",
         "-vf", (f"drawtext=fontfile='{FONT}':text='{text}':fontcolor=white:fontsize={int(size)}"
                 f":x={int(x)}:y={int(y)}"),
         "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "gray", "-"],
        stdout=subprocess.PIPE, check=True).stdout
    xs, ys = [], []
    for row in range(max(0, y_from), H):
        line = p[row * W:(row + 1) * W]
        for col in range(max(0, x_from), min(W, x_to)):
            if line[col] > thr:
                xs.append(col); ys.append(row)
    if not xs:
        return None
    return min(xs), min(ys), max(xs), max(ys)
