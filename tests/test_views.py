import os
import unittest

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "examples.settings")

import django

django.setup()

from django.test import Client, SimpleTestCase


class ExampleViewTests(SimpleTestCase):
    def setUp(self) -> None:
        self.client = Client()

    def test_homepage_renders_python_components_and_interaction_hooks(self) -> None:
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Build pages with Python")
        self.assertContains(response, "data-pyui-toggle")
        self.assertContains(response, 'hx-get="/search/"')

    def test_search_returns_matching_html_fragment(self) -> None:
        response = self.client.get("/search/", {"q": "ht"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "HTMX")
        self.assertNotContains(response, "Django")

    def test_search_returns_empty_state_for_no_matches(self) -> None:
        response = self.client.get("/search/", {"q": "not-found"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No matching items.")


if __name__ == "__main__":
    unittest.main()
