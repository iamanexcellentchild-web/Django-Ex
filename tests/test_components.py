import unittest

from django_pyui import Button, Card, Column, Div, Element, Heading, Input, Text, TextField


class ComponentTests(unittest.TestCase):
    def test_nested_components_render_and_escape_content_and_attributes(self) -> None:
        component = Column(
            Heading("Hello <world>"),
            Div("Safe & sound", title='"quoted"'),
            class_="layout",
            data_testid="main",
        )

        self.assertEqual(
            str(component),
            '<div class="layout" data-testid="main">'
            "<h1>Hello &lt;world&gt;</h1>"
            '<div title="&quot;quoted&quot;">Safe &amp; sound</div>'
            "</div>",
        )

    def test_htmx_attributes_are_rendered_as_html_attributes(self) -> None:
        component = Input(hx_get="/search/", hx_trigger="keyup changed")

        self.assertEqual(
            str(component),
            '<input hx-get="/search/" hx-trigger="keyup changed">',
        )

    def test_button_defaults_to_non_submit(self) -> None:
        self.assertEqual(str(Button("Open")), '<button type="button">Open</button>')
        self.assertEqual(
            str(Button("Save", type="submit")),
            '<button type="submit">Save</button>',
        )

    def test_column_has_default_layout_class(self) -> None:
        self.assertEqual(str(Column("Content")), '<div class="pyui-column">Content</div>')

    def test_card_has_default_style_class_and_accepts_custom_class(self) -> None:
        self.assertEqual(str(Card("Content")), '<div class="pyui-card">Content</div>')
        self.assertEqual(
            str(Card("Content", class_="custom-card")),
            '<div class="custom-card">Content</div>',
        )

    def test_text_field_links_label_to_input_and_accepts_attributes(self) -> None:
        self.assertEqual(
            str(TextField("Email", name="email", type="email", required=True)),
            '<div class="pyui-field"><label for="email" class="pyui-label">Email</label>'
            '<input type="email" name="email" id="email" required class="pyui-input"></div>',
        )

    def test_boolean_and_omitted_attributes(self) -> None:
        self.assertEqual(
            str(Input(disabled=True, required=False, title=None)),
            "<input disabled>",
        )

    def test_void_elements_reject_children(self) -> None:
        with self.assertRaises(ValueError):
            Element("input", "not allowed")

    def test_inline_event_handlers_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            Div("Click", onclick="alert(1)")

    def test_heading_level_is_validated(self) -> None:
        with self.assertRaises(ValueError):
            Heading("Not a heading", level=7)

    def test_text_component_escapes_markup(self) -> None:
        self.assertEqual(str(Text("<script>")), "&lt;script&gt;")


if __name__ == "__main__":
    unittest.main()
