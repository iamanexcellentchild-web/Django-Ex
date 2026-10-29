import re
from typing import TypeAlias

from django.utils.html import conditional_escape, format_html, format_html_join
from django.utils.safestring import SafeString

Child: TypeAlias = "Component | str | int | float | None"

_ATTRIBUTE_NAME = re.compile(r"^[A-Za-z_:][A-Za-z0-9_:.-]*$")
_TAG_NAME = re.compile(r"^[A-Za-z][A-Za-z0-9:-]*$")
_VOID_ELEMENTS = {
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
}
_BOOLEAN_ATTRIBUTES = {
    "allowfullscreen",
    "async",
    "autofocus",
    "autoplay",
    "checked",
    "controls",
    "default",
    "defer",
    "disabled",
    "formnovalidate",
    "hidden",
    "inert",
    "ismap",
    "itemscope",
    "loop",
    "multiple",
    "muted",
    "nomodule",
    "novalidate",
    "open",
    "playsinline",
    "readonly",
    "required",
    "reversed",
    "selected",
}


class Component:
    def render(self) -> SafeString:
        raise NotImplementedError

    def __html__(self) -> SafeString:
        return self.render()

    def __str__(self) -> str:
        return str(self.render())


class Element(Component):
    def __init__(self, tag: str, *children: Child, **attributes: object) -> None:
        if not _TAG_NAME.fullmatch(tag):
            raise ValueError(f"Invalid HTML tag name: {tag!r}")
        if tag.lower() in _VOID_ELEMENTS and children:
            raise ValueError(f"The void element {tag!r} cannot have children.")

        for key in attributes:
            _attribute_name(key)

        self.tag = tag
        self.children = children
        self.attributes = attributes

    def render(self) -> SafeString:
        attrs = _render_attributes(self.attributes)
        if self.tag.lower() in _VOID_ELEMENTS:
            return format_html("<{}{}>", self.tag, attrs)

        children = format_html_join("", "{}", ((_render_child(child),) for child in self.children))
        return format_html("<{}{}>{}</{}>", self.tag, attrs, children, self.tag)


class Text(Component):
    def __init__(self, value: str | int | float) -> None:
        self.value = value

    def render(self) -> SafeString:
        return conditional_escape(self.value)


def _render_child(child: Child) -> object:
    if child is None:
        return ""
    if isinstance(child, Component):
        return child.render()
    return child


def _attribute_name(key: str) -> str:
    name = key[:-1] if key.endswith("_") else key
    name = name.replace("_", "-")
    if not _ATTRIBUTE_NAME.fullmatch(name):
        raise ValueError(f"Invalid HTML attribute name: {key!r}")
    if name.lower().startswith("on"):
        raise ValueError("Inline event-handler attributes are not supported.")
    return name


def _render_attributes(attributes: dict[str, object]) -> SafeString:
    rendered: list[SafeString] = []
    for key, value in attributes.items():
        name = _attribute_name(key)
        if value is None:
            continue
        if isinstance(value, bool):
            if name.lower() in _BOOLEAN_ATTRIBUTES:
                if value:
                    rendered.append(format_html(" {}", name))
                continue
            value = str(value).lower()
        rendered.append(format_html(' {}="{}"', name, value))
    return format_html_join("", "{}", ((attribute,) for attribute in rendered))


def Div(*children: Child, **attributes: object) -> Element:
    return Element("div", *children, **attributes)


def Card(*children: Child, **attributes: object) -> Element:
    attributes.setdefault("class_", "pyui-card")
    return Div(*children, **attributes)


def Column(*children: Child, **attributes: object) -> Element:
    attributes.setdefault("class_", "pyui-column")
    return Div(*children, **attributes)


def Row(*children: Child, **attributes: object) -> Element:
    attributes.setdefault("class_", "pyui-row")
    return Div(*children, **attributes)


def Heading(text: Child, level: int = 1, **attributes: object) -> Element:
    if level not in range(1, 7):
        raise ValueError("Heading level must be between 1 and 6.")
    return Element(f"h{level}", text, **attributes)


def Button(*children: Child, **attributes: object) -> Element:
    attributes.setdefault("type", "button")
    return Element("button", *children, **attributes)


def Input(**attributes: object) -> Element:
    return Element("input", **attributes)


def TextField(label: str, *, name: str, type: str = "text", **attributes: object) -> Element:
    field_id = str(attributes.get("id", name))
    input_attributes: dict[str, object] = {
        "type": type,
        "name": name,
        "id": field_id,
    }
    input_attributes.update(attributes)
    input_attributes.setdefault("class_", "pyui-input")
    return Column(
        Element("label", label, for_=field_id, class_="pyui-label"),
        Input(**input_attributes),
        class_="pyui-field",
    )


def Form(*children: Child, **attributes: object) -> Element:
    return Element("form", *children, **attributes)


def Link(*children: Child, **attributes: object) -> Element:
    return Element("a", *children, **attributes)
