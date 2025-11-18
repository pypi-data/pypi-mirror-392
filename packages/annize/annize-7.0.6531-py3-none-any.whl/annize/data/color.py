# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import colorsys


class Color:
    """
    A color.
    """

    def __init__(self, *, red: float, green: float, blue: float):
        """
        :param red: The color's red component. A value between 0 and 1.
        :param green: The color's green component. A value between 0 and 1.
        :param blue: The color's blue component. A value between 0 and 1.
        """
        self.__red = self.__get_normed_value(None, red)
        self.__green = self.__get_normed_value(None, green)
        self.__blue = self.__get_normed_value(None, blue)

    @property
    def red(self) -> float:
        """
        The color's red component. A value between 0 and 1.

        This is a component of the RGB color space, as :py:attr:`green` and :py:attr:`blue`.
        There are other color spaces supported as well.
        """
        return self.__red

    @property
    def green(self) -> float:
        """
        The color's green component. A value between 0 and 1.

        This is a component of the RGB color space, as :py:attr:`red` and :py:attr:`blue`.
        There are other color spaces supported as well.
        """
        return self.__green

    @property
    def blue(self) -> float:
        """
        The color's blue component. A value between 0 and 1.

        This is a component of the RGB color space, as :py:attr:`red` and :py:attr:`green`.
        There are other color spaces supported as well.
        """
        return self.__blue

    @property
    def hue(self) -> float:
        """
        The color's hue component. A value between 0 and 1.

        This is a component of the HLS color space, as :py:attr:`lightness` and :py:attr:`saturation`.
        There are other color spaces supported as well.
        """
        return colorsys.rgb_to_hls(self.red, self.green, self.blue)[0]

    @property
    def lightness(self) -> float:
        """
        The color's hue component. A value between 0 and 1.

        This is a component of the HLS color space, as :py:attr:`hue` and :py:attr:`saturation`.
        There are other color spaces supported as well.
        """
        return colorsys.rgb_to_hls(self.red, self.green, self.blue)[1]

    @property
    def saturation(self) -> float:
        """
        The color's hue component. A value between 0 and 1.

        This is a component of the HLS color space, as :py:attr:`hue` and :py:attr:`lightness`.
        There are other color spaces supported as well.
        """
        return colorsys.rgb_to_hls(self.red, self.green, self.blue)[2]

    def with_modified(self, *, red: float|None = None, green: float|None = None,
                      blue: float|None = None, hue: float|None = None,
                      lightness: float|None = None, saturation: float|None = None) -> "Color":
        """
        Return a color with some components set to new values.

        :param red: See :py:attr:`red`.
        :param green: See :py:attr:`green`.
        :param blue: See :py:attr:`blue`.
        :param hue: See :py:attr:`hue`.
        :param lightness: See :py:attr:`lightness`.
        :param saturation: See :py:attr:`saturation`.
        """
        red = Color.__get_normed_value(red, self.red)
        green = Color.__get_normed_value(green, self.green)
        blue = Color.__get_normed_value(blue, self.blue)
        result_color = Color(red=red, green=green, blue=blue)

        if any(_ is not None for _ in (hue, lightness, saturation)):
            hue = Color.__get_normed_value(hue, result_color.hue)
            lightness = Color.__get_normed_value(lightness, result_color.lightness)
            saturation = Color.__get_normed_value(saturation, result_color.saturation)
            red, green, blue = colorsys.hls_to_rgb(hue, lightness, saturation)
            result_color = Color(red=red, green=green, blue=blue)

        return result_color

    @property
    def html_color_spec(self) -> str:
        """
        The HTML color specification of this color.
        """
        large_r, large_g, large_b = (round(x * 255) for x in (self.red, self.green, self.blue))
        return (f"#{Color.__html_color_spec__part(large_r)}"
                f"{Color.__html_color_spec__part(large_g)}"
                f"{Color.__html_color_spec__part(large_b)}")

    @staticmethod
    def __get_normed_value(value_1: float|None, value_2: float) -> float:
        return min(max(0.0, value_2 if (value_1 is None) else value_1), 1.0)

    @staticmethod
    def __html_color_spec__part(part_value: int) -> str:
        return ("0" + hex(part_value)[2:])[-2:]
