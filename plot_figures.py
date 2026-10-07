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


if __name__ == '__main__':
    main()
