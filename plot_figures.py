"""Generate the activation and softmax JPGs using Python and ffmpeg."""

import math
import subprocess
import tempfile
from pathlib import Path

WIDTH, HEIGHT = 900, 560
INK = (35, 50, 70)
BLUE = (37, 100, 200)
ORANGE = (225, 90, 42)
GRID = (220, 225, 232)


class Canvas:
    def __init__(self):
        self.pixels = bytearray([255, 255, 255] * WIDTH * HEIGHT)

    def dot(self, x, y, color, radius=2):
        x, y = round(x), HEIGHT - 1 - round(y)
        for yy in range(max(0, y - radius), min(HEIGHT, y + radius + 1)):
            for xx in range(max(0, x - radius), min(WIDTH, x + radius + 1)):
                offset = 3 * (yy * WIDTH + xx)
                self.pixels[offset:offset + 3] = bytes(color)

    def line(self, x0, y0, x1, y1, color, radius=1):
        steps = max(1, math.ceil(max(abs(x1-x0), abs(y1-y0))))
        for step in range(steps + 1):
            t = step / steps
            self.dot(x0 + (x1-x0)*t, y0 + (y1-y0)*t, color, radius)

    def curve(self, points, color):
        for first, second in zip(points, points[1:]):
            self.line(*first, *second, color)

    def axes(self):
        for y in (100, 188, 275, 362, 450):
            self.line(100, y, 820, y, GRID, 0)
        self.line(100, 100, 100, 450, INK, 0)
        self.line(100, 100, 820, 100, INK, 0)

    def bar(self, x, height, color):
        for xx in range(x, x + 55):
            self.line(xx, 101, xx, 100 + height, color, 0)

    def save(self, destination):
        with tempfile.TemporaryDirectory() as temporary:
            ppm = Path(temporary) / "figure.ppm"
            with ppm.open("wb") as output:
                output.write(f"P6\n{WIDTH} {HEIGHT}\n255\n".encode())
                output.write(self.pixels)
            command = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(ppm)]
            command += ["-frames:v", "1", "-q:v", "2", str(destination)]
            subprocess.run(command, check=True)


def softmax(scores):
    shifted = [math.exp(x - max(scores)) for x in scores]
    return [x / sum(shifted) for x in shifted]


def main():
    output = Path("figures")
    output.mkdir(exist_ok=True)

    canvas = Canvas()
    canvas.axes()
    canvas.line(100, 275, 820, 275, GRID, 0)
    canvas.line(460, 100, 460, 450, GRID, 0)
    xs = [-3 + index / 100 for index in range(601)]
    canvas.curve([(460 + x*120, 275 + max(0, x)*78) for x in xs], BLUE)
    canvas.curve([(460 + x*120, 275 + 0.5*x*(1 + math.erf(x/math.sqrt(2)))*78) for x in xs], ORANGE)
    canvas.save(output / "activations.jpg")

    canvas = Canvas()
    canvas.axes()
    xs = [-5 + index / 50 for index in range(501)]
    canvas.curve([(100 + (x+5)*72, 100 + softmax([x, 0])[0]*350) for x in xs], BLUE)
    canvas.curve([(100 + (x+5)*72, 100 + softmax([x, 0])[1]*350) for x in xs], ORANGE)
    canvas.save(output / "softmax.jpg")

if __name__ == "__main__":
    main()
