"""Generate labeled SVG figures for the worksheet using standard Python."""

import math
from html import escape
from pathlib import Path

BLUE = "#2564c8"
RED = "#d64b35"


def softmax(scores):
    shifted = [math.exp(x - max(scores)) for x in scores]
    return [x / sum(shifted) for x in shifted]


def plot(destination, title, xlabel, ylabel, xlim, ylim, xticks, yticks, curves):
    left, top, width, height = 100, 110, 700, 350

    def px(x):
        return left + (x - xlim[0]) / (xlim[1] - xlim[0]) * width

    def py(y):
        return top + height - (y - ylim[0]) / (ylim[1] - ylim[0]) * height

    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="900" height="560" '
             'viewBox="0 0 900 560" role="img" '
             f'aria-label="{escape(title)}">',
             '<rect width="900" height="560" fill="white"/>',
             '<g font-family="sans-serif" fill="#233246">',
             f'<text x="450" y="35" text-anchor="middle" font-size="23">{escape(title)}</text>']
    for i, (label, color, _) in enumerate(curves):
        x = 135 + i * 350
        parts += [f'<line x1="{x}" y1="70" x2="{x+35}" y2="70" stroke="{color}" stroke-width="3"/>',
                  f'<text x="{x+45}" y="76" font-size="16">{escape(label)}</text>']
    for x in xticks:
        parts += [f'<line x1="{px(x)}" y1="{top}" x2="{px(x)}" y2="{top+height}" stroke="#dce1e8"/>',
                  f'<text x="{px(x)}" y="490" text-anchor="middle" font-size="15">{x:g}</text>']
    for y in yticks:
        parts += [f'<line x1="{left}" y1="{py(y)}" x2="{left+width}" y2="{py(y)}" stroke="#dce1e8"/>',
                  f'<text x="85" y="{py(y)+5}" text-anchor="end" font-size="15">{y:g}</text>']
    parts += [f'<rect x="{left}" y="{top}" width="{width}" height="{height}" fill="none" stroke="#233246"/>',
              f'<text x="450" y="535" text-anchor="middle" font-size="18">{escape(xlabel)}</text>',
              f'<text transform="translate(28 285) rotate(-90)" text-anchor="middle" font-size="18">{escape(ylabel)}</text>']
    xs = [xlim[0] + i * (xlim[1]-xlim[0])/600 for i in range(601)]
    for _, color, function in curves:
        points = ' '.join(f'{px(x):.2f},{py(function(x)):.2f}' for x in xs)
        parts.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="3"/>')
    parts.append('</g></svg>')
    destination.write_text(''.join(parts), encoding='utf-8')


def source_heatmap():
    """Render the fixed example without filling in student functions."""
    import attention as worksheet

    weights = [softmax([
        sum(q * k for q, k in zip(query, key)) / math.sqrt(len(query))
        for key in worksheet.source_keys
    ]) for query in worksheet.target_queries]
    Path("figures/source_attention.svg").write_text(
        worksheet.source_attention_svg(weights), encoding="utf-8")
    return weights



def xor_figures():
    """Illustrate XOR targets, then overlay one illustrative linear boundary."""
    for name, title, boundary in [
        ("xor_target", "XOR: бажані класи", []),
        ("xor_linear", "Одна пряма: правильно 2 з 4 точок", [(.5, 0, .5, 1)]),
    ]:
        # Smooth target illustration only; XOR is defined at the four corners.
        def score(x, y):
            return (1-math.tanh(7*(x-.5))*math.tanh(7*(y-.5)))/2
        parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="640" height="570" viewBox="0 0 640 570" role="img" '
                 f'aria-label="{title}"><rect width="640" height="570" fill="white"/>',
                 f'<g font-family="sans-serif"><text x="320" y="30" text-anchor="middle" font-size="22">{title}</text>']
        def px(x): return 80+400*x
        def py(y): return 460-400*y
        def color(v):
            v = min(1, max(0, v))
            a, b, t = ((33, 102, 172), (247, 247, 247), 2*v) if v < .5 else ((247, 247, 247), (178, 24, 43), 2*v-1)
            return '#'+''.join(f'{round(i+(j-i)*t):02x}' for i,j in zip(a,b))
        for i in range(80):
            for j in range(80):
                parts.append(f'<rect x="{px(i/80)}" y="{py((j+1)/80)}" width="5.1" height="5.1" fill="{color(score((i+.5)/80,(j+.5)/80))}"/>')
        for x,y,u,v in boundary:
            parts.append(f'<line x1="{px(x)}" y1="{py(y)}" x2="{px(u)}" y2="{py(v)}" stroke="black" stroke-width="2" stroke-dasharray="6 4"/>')
        for x,y,target in [(0,0,0),(0,1,1),(1,0,1),(1,1,0)]:
            cx,cy=px(x),py(y)
            if target:
                parts.append(f'<circle cx="{cx}" cy="{cy}" r="8" fill="#55ee66" stroke="white" stroke-width="3"/>')
            else:
                parts.append(f'<path d="M {cx} {cy-9} l 9 9 l -9 9 l -9 -9 Z" fill="#182b43" stroke="white" stroke-width="3"/>')
        if boundary:
            for x,y,target in [(0,0,0),(0,1,1),(1,0,1),(1,1,0)]:
                correct = int(x > .5) == target
                parts.append(f'<text x="{px(x)+ (16 if x == 0 else -16)}" y="{py(y)+(25 if y == 1 else -15)}" text-anchor="{"start" if x == 0 else "end"}" font-size="18" fill="white" stroke="#182b43" stroke-width=".4">{"✓" if correct else "✗"}</text>')
            parts.append('<text x="180" y="90" text-anchor="middle" fill="white">прогноз 0</text><text x="380" y="90" text-anchor="middle" fill="white">прогноз 1</text>')
        for tick in [0,.5,1]:
            parts.append(f'<text x="{px(tick)}" y="485" text-anchor="middle">{tick:g}</text><text x="60" y="{py(tick)+5}" text-anchor="end">{tick:g}</text>')
        for i in range(100):
            parts.append(f'<rect x="525" y="{460-4*(i+1)}" width="20" height="4.1" fill="{color((i+.5)/100)}"/>')
        parts.append('<text x="552" y="65">1</text><text x="552" y="265">0.5</text><text x="552" y="465">0</text>')
        parts.append('<text x="280" y="515" text-anchor="middle">x₁</text><text x="28" y="260">x₂</text><text x="320" y="545" text-anchor="middle">● клас 1    ◆ клас 0</text></g></svg>')
        Path(f"figures/{name}.svg").write_text(''.join(parts), encoding="utf-8")


def main():
    output = Path("figures")
    output.mkdir(exist_ok=True)
    plot(output / 'activations.svg', 'ReLU та GELU', 'Вхід x', 'Значення функції f(x)',
         (-3, 3), (-0.3, 3.2), [-3, -2, -1, 0, 1, 2, 3], [0, 1, 2, 3],
         [('ReLU(x)', BLUE, lambda x: max(0, x)),
          ('GELU(x)', RED, lambda x: x/2*(1+math.erf(x/math.sqrt(2))))])
    plot(output / 'softmax.svg', 'Softmax для оцінок [x, 0]', 'Перша оцінка x (друга = 0)',
         'Вага після softmax', (-5, 5), (0, 1), [-5, -3, -1, 0, 1, 3, 5], [0, .25, .5, .75, 1],
         [('Вага першого елемента', BLUE, lambda x: softmax([x, 0])[0]),
          ('Вага другого елемента', RED, lambda x: softmax([x, 0])[1])])
    source_heatmap()
    xor_figures()


if __name__ == '__main__':
    main()
