_color_rgb256 = {}
_color_rgb256["sky"] = (35, 192, 241)
_color_rgb256["ocean"] = (29, 139, 204)
_color_rgb256["night"] = (100, 120, 186)
_color_rgb256["forest"] = (39, 182, 123)
_color_rgb256["lime"] = (128, 189, 1)
_color_rgb256["orange"] = (246, 147, 0)
_color_rgb256["red"] = (246, 1, 0)
_color_rgb256["salmon"] = (250, 128, 114)
_color_rgb256["pink"] = (255, 192, 203)
_color_rgb256["hotpink"] = (255, 105, 180)
_color_rgb256["crimson"] = (220, 20, 60)
_color_rgb256["gold"] = (255, 215, 0)
_color_rgb256["orchid"] = (218, 112, 214)
_color_rgb256["seagreen"] = (46, 139, 87)
_color_rgb256["mediumaquamarine"] = (102, 205, 170)
_color_rgb256["turquoise"] = (64, 224, 208)
_color_rgb256["goldenrod"] = (218, 165, 32)
_color_rgb256["powderblue"] = (176, 224, 230)


def hexcolor(color):
    if color.startswith("#"):
        return color
    c = _color_rgb256[color.casefold()]
    return "#{}{}{}".format(
        *(hex(c[i])[-2:] if c[i] > 15 else "0" + hex(c[i])[-1:] for i in range(3))
    )


def strcolor_rgb256(color):
    if color.startswith("#"):
        color = color[1:]
        if len(color) == 3:
            color = color[0] * 2 + color[1] * 2 + color[2] * 2
        c = tuple(int(color[i : i + 2], 16) for i in range(0, 6, 2))
        return "{},{},{}".format(*c)
    c = _color_rgb256[color.casefold()]
    return "{},{},{}".format(*c)
