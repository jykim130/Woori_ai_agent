"""Shared vector card style matching the user's blue reference cards."""

from reportlab.lib.colors import HexColor


def draw_step_card(canvas, x, top, width, height, page_height):
    bottom = page_height - top - height
    radius = 7.5

    canvas.saveState()
    canvas.setFillColor(HexColor('#79B8C8'))
    for spread, opacity, offset in (
        (2.2, 0.025, -1.2),
        (1.5, 0.035, -1.0),
        (0.8, 0.050, -0.7),
    ):
        canvas.setFillAlpha(opacity)
        canvas.roundRect(
            x - spread, bottom + offset - spread,
            width + 2 * spread, height + 2 * spread,
            radius + spread, stroke=0, fill=1,
        )
    canvas.restoreState()

    canvas.saveState()
    clip = canvas.beginPath()
    clip.roundRect(x, bottom, width, height, radius)
    canvas.clipPath(clip, stroke=0, fill=0)
    canvas.linearGradient(
        x, bottom, x + width, bottom,
        (HexColor('#F7FCFF'), HexColor('#E5F3FD')),
    )
    canvas.setFillColor(HexColor('#CDEDFC'))
    canvas.setFillAlpha(0.48)
    canvas.ellipse(
        x + width * 0.70, bottom + height * 0.21,
        x + width * 1.55, bottom + height * 0.96,
        stroke=0, fill=1,
    )
    canvas.setStrokeColor(HexColor('#FFFFFF'))
    canvas.setStrokeAlpha(0.90)
    canvas.setLineWidth(0.7)
    canvas.line(x + 7, bottom + height - 1.1,
                x + width - 7, bottom + height - 1.1)
    canvas.restoreState()

    canvas.saveState()
    canvas.setStrokeColor(HexColor('#CFEAF8'))
    canvas.setLineWidth(0.65)
    canvas.roundRect(x, bottom, width, height, radius, stroke=1, fill=0)
    canvas.restoreState()
