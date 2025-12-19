import pygame as pg

def draw_text_wrapped(
    surface: pg.Surface,
    text: str,
    font: pg.font.Font,
    color: tuple[int, int, int],
    rect: pg.Rect,
    line_spacing: int = 2
):
    """
    Draw text inside rect with automatic word wrapping.
    """
    words = text.split(" ")
    x, y = rect.topleft
    max_width = rect.width
    line_height = font.get_height()

    line = ""
    for word in words:
        test_line = line + word + " "
        test_surface = font.render(test_line, True, color)

        if test_surface.get_width() <= max_width:
            line = test_line
        else:
            surface.blit(font.render(line, True, color), (x, y))
            y += line_height + line_spacing
            line = word + " "

        if y + line_height > rect.bottom:
            break  

    if line:
        surface.blit(font.render(line, True, color), (x, y))
