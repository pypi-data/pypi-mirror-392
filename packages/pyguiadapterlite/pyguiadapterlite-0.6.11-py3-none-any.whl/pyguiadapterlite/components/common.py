from typing import Literal

_DEFAULT_PARAMETER_NAME_LABEL_JUSTIFY: Literal["left", "right", "center"] = "center"
_DEFAULT_WIDGET_FONT = ("Consolas", 11)


def set_default_parameter_label_justify(justify: Literal["left", "right", "center"]):
    global _DEFAULT_PARAMETER_NAME_LABEL_JUSTIFY
    _DEFAULT_PARAMETER_NAME_LABEL_JUSTIFY = justify


def get_default_parameter_label_justify() -> Literal["left", "right", "center"]:
    return _DEFAULT_PARAMETER_NAME_LABEL_JUSTIFY


def set_default_widget_font(font: tuple):
    global _DEFAULT_WIDGET_FONT
    _DEFAULT_WIDGET_FONT = font


def get_default_widget_font() -> tuple:
    return _DEFAULT_WIDGET_FONT
