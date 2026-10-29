# Django PyUI guide

Django PyUI is a small component layer for building server-rendered Django
interfaces in Python. Its components produce ordinary HTML. Django remains in
charge of URLs, views, templates, forms, models, validation, authentication,
and persistence.

This guide covers setup, composing pages, styling, HTMX, safety, testing, and
the current limits of the toolkit.

## Contents

1. [How PyUI works](#1-how-pyui-works)
2. [Install and run the example](#2-install-and-run-the-example)
3. [Use PyUI in an existing Django project](#3-use-pyui-in-an-existing-django-project)
4. [Compose a page](#4-compose-a-page)
5. [Component reference](#5-component-reference)
6. [Attributes, escaping, and validation](#6-attributes-escaping-and-validation)
7. [CSS and JavaScript](#7-css-and-javascript)
8. [Add HTMX interactions](#8-add-htmx-interactions)
9. [Forms and CSRF](#9-forms-and-csrf)
10. [Testing and packaging](#10-testing-and-packaging)
11. [Limitations and troubleshooting](#11-limitations-and-troubleshooting)

## 1. How PyUI works

A view calls component functions to create a nested Python object tree. Django
renders that tree into a template. The browser receives normal HTML and CSS.
When an interaction needs server data, HTMX can request a Django URL and swap
the HTML fragment returned by the view.

```text
Python components -> Django template -> HTML/CSS in the browser
        ^                                      |
        +---------- Django + HTMX response ----+
```

This model keeps application logic on the server. PyUI does not provide
client-side state, a virtual DOM, or React-style rendering. Use ordinary
JavaScript or another frontend framework if your application needs those
features.

## 2. Install and run the example

The project requires Python 3.10 or later and Django 5.2.

### Windows PowerShell

```powershell
git clone https://github.com/iamanexcellentchild-web/Django-Ex.git
cd Django-Ex
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m django runserver --settings=examples.settings
```

### macOS or Linux

```bash
git clone https://github.com/iamanexcellentchild-web/Django-Ex.git
cd Django-Ex
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m django runserver --settings=examples.settings
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/). The example page is in
`examples/views.py`; routes are in `examples/urls.py`.

The editable install is useful while developing the toolkit: edits to the
local `django_pyui` package are immediately used by the example. For a consumer
project, install the package from a package index only after a release is
published, or install a local checkout with `python -m pip install -e
<path-to-checkout>`.

## 3. Use PyUI in an existing Django project

Install the package into the same environment as Django. From a local checkout:

```powershell
python -m pip install -e C:\path\to\Django-Ex
```

Enable Django's static files app and PyUI in `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # Django and project applications...
    "django.contrib.staticfiles",
    "django_pyui",
]
```

Use the static files template tag to include the CSS and optional JavaScript:

```html
{% load static %}
<link rel="stylesheet" href="{% static 'django_pyui/pyui.css' %}">
<script src="{% static 'django_pyui/pyui.js' %}" defer></script>
```

The JavaScript is only needed for the built-in `data-pyui-toggle` behavior.
Include HTMX separately only on pages that use `hx-*` attributes. This example
uses the CDN for convenience; for production, serve a reviewed HTMX build from
your own static assets and apply your site's content security policy.

## 4. Compose a page

Components accept child components, text, numbers, and `None`. Nest them to
express the structure of the page:

```python
from django.shortcuts import render
from django_pyui import Button, Card, Column, Heading, Text, TextField


def contact_page(request):
    page = Card(
        Column(
            Heading("Get in touch"),
            Text("Tell us a little about your project."),
            TextField("Your name", name="name", required=True),
            TextField("Email address", name="email", type="email", required=True),
            Button("Send message", type="submit", class_="pyui-button"),
        ),
    )
    return render(request, "contact.html", {"page": page})
```

In `contact.html`, render the component tree:

```html
{% load static %}
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="{% static 'django_pyui/pyui.css' %}">
    <title>Contact</title>
  </head>
  <body>
    {{ page }}
  </body>
</html>
```

`Component` objects implement Django's HTML rendering protocol. Passing
`page` into a template preserves its HTML-safe rendering; do not mark arbitrary
user input as safe.

## 5. Component reference

Import components from `django_pyui`.

| Component | Purpose | Example |
|---|---|---|
| `Element(tag, *children, **attrs)` | Any validated HTML element | `Element("section", "Intro")` |
| `Text(value)` | Escaped text node | `Text("Welcome")` |
| `Div(*children, **attrs)` | A `<div>` | `Div("Content", id="main")` |
| `Card(*children, **attrs)` | A `<div>` with `pyui-card` | `Card(Heading("Title"))` |
| `Column(*children, **attrs)` | A vertical flex `<div>` | `Column(Heading("Title"), Text("Body"))` |
| `Row(*children, **attrs)` | A horizontal flex `<div>` | `Row(Text("A"), Text("B"))` |
| `Heading(text, level=1, **attrs)` | Heading from `<h1>` to `<h6>` | `Heading("About", level=2)` |
| `Button(*children, **attrs)` | A `<button>`; defaults to `type="button"` | `Button("Save", type="submit")` |
| `Input(**attrs)` | A void `<input>` | `Input(type="email", name="email")` |
| `TextField(label, *, name, type="text", **attrs)` | Label and styled input inside a column | `TextField("Email", name="email", type="email")` |
| `Form(*children, **attrs)` | A `<form>` | `Form(Input(name="q"), method="get")` |
| `Link(*children, **attrs)` | An `<a>` | `Link("Home", href="/")` |

Use `Element` for semantic tags without a dedicated helper, such as `main`,
`section`, `nav`, `label`, `textarea`, or `footer`.

### Layout classes

`Column` and `Row` apply `pyui-column` and `pyui-row` by default. `Card`
applies `pyui-card`. `TextField` applies `pyui-field`, `pyui-label`, and
`pyui-input`. The CSS package also defines `pyui-button` and
`pyui-button--secondary` for buttons. Add the button class explicitly:

```python
Button("Continue", class_="pyui-button")
```

Supply `class_="..."` to override a helper's default class. If you want to
retain a default class and add your own, include both class names yourself:

```python
Card("Profile", class_="pyui-card profile-card")
```

### `TextField` details

`TextField` creates an associated `<label>` and `<input>`:

```python
TextField(
    "Email address",
    name="email",
    type="email",
    autocomplete="email",
    required=True,
    placeholder="you@example.com",
)
```

The `name` is used as the default `id`; pass `id="..."` to customize it. All
remaining keyword arguments are added to the input, so normal HTML and HTMX
attributes work. Use `Input` directly for unlabeled or specialized input
markup.

## 6. Attributes, escaping, and validation

Python identifiers cannot contain hyphens, so PyUI translates underscores in
attribute names:

| Python | Rendered HTML |
|---|---|
| `class_="panel"` | `class="panel"` |
| `aria_label="Search"` | `aria-label="Search"` |
| `hx_get="/search/"` | `hx-get="/search/"` |
| `data_pyui_toggle="#details"` | `data-pyui-toggle="#details"` |

Use the trailing underscore convention for Python keywords that are HTML
attributes: `class_`, `for_`. Attribute values are escaped. A `None` value
omits the attribute. Boolean HTML attributes such as `required`, `disabled`,
and `hidden` are rendered in HTML boolean form; false boolean attributes are
omitted. Other boolean values are output as `"true"` or `"false"`.

Text and component children are escaped. This is safe:

```python
Text(user_supplied_value)
```

Do not concatenate untrusted input into raw HTML or mark it safe yourself.

PyUI validates tag names and attribute names. It rejects attributes beginning
with `on` (including `onclick`) to discourage inline JavaScript event
handlers. Use a JavaScript event listener or a `data-*` attribute instead.
Void elements such as `input`, `img`, and `br` cannot have children. Heading
levels must be from 1 to 6.

These safeguards do not replace Django's input validation, authentication,
authorization, CSRF middleware, or database protections.

## 7. CSS and JavaScript

The packaged stylesheet is intentionally small. It defines flex layouts,
cards, labels, inputs, and button classes. Include it from a Django template:

```django
{% load static %}
<link rel="stylesheet" href="{% static 'django_pyui/pyui.css' %}">
```

The CSS reads theme tokens from custom properties and has fallback values. Set
them in the application's stylesheet and load that file after `pyui.css`:

```css
:root {
  --pyui-color-text: #20251f;
  --pyui-color-muted: #656b63;
  --pyui-color-border: #d5d8d0;
  --pyui-color-primary: #2357a5;
  --pyui-color-surface: #f8faff;
  --pyui-radius: 0.75rem;
  --pyui-space: 1.25rem;
}

.profile-card {
  max-width: 42rem;
  margin-inline: auto;
}
```

Add your own classes via `class_` on any component. The framework does not
restrict you to the bundled CSS.

The optional `pyui.js` listens for clicks on elements with
`data-pyui-toggle="#target"` and flips the target's `hidden` state. It updates
the trigger's `aria-expanded` value:

```python
from django_pyui import Button, Div

Button(
    "More details",
    data_pyui_toggle="#details",
    aria_controls="details",
    aria_expanded="false",
)
Div("Extra information", id="details", hidden=True)
```

Load the script with `defer`. The selector must point to an existing element.
Use your own JavaScript for behaviors beyond this small toggle.

## 8. Add HTMX interactions

HTMX attributes are ordinary HTML attributes; PyUI translates their underscores
into hyphens. Add HTMX to the page separately, and return HTML from your Django
view.

```python
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django_pyui import Column, Div, Heading, Input, Text


def search_page(request: HttpRequest) -> HttpResponse:
    page = Column(
        Heading("Find a book"),
        Input(
            type="search",
            name="q",
            hx_get=reverse("book-search"),
            hx_trigger="keyup changed delay:300ms",
            hx_target="#results",
            hx_swap="innerHTML",
        ),
        Div("Start typing to search.", id="results"),
    )
    return render(request, "catalog/search.html", {"page": page})


def book_search(request: HttpRequest) -> HttpResponse:
    query = request.GET.get("q", "").strip()
    books = Book.objects.filter(title__icontains=query)[:20] if query else []
    result = (
        Column(*(Div(book.title) for book in books))
        if books
        else Div("No matching books.")
    )
    return HttpResponse(str(result))
```

Wire these views with Django URLs:

```python
from django.urls import path
from . import views

urlpatterns = [
    path("books/", views.search_page, name="book-search-page"),
    path("books/search/", views.book_search, name="book-search"),
]
```

The page's HTMX request calls `/books/search/`; Django returns the component
HTML and HTMX swaps it into `#results`. The example caps results at 20. Apply
your own authorization, filtering, and pagination rules to real data.

## 9. Forms and CSRF

Use Django forms for server-side validation and bind rendered HTML controls to
the view's expected names. Protect every state-changing request with Django's
CSRF middleware. When an HTMX form submits, include a CSRF token as a form
control or configure the request to send Django's CSRF header.

```python
from django.middleware.csrf import get_token
from django.urls import reverse
from django_pyui import Button, Form, Input

form = Form(
    Input(
        type="hidden",
        name="csrfmiddlewaretoken",
        value=get_token(request),
    ),
    Input(type="text", name="title", required=True),
    Button("Add book", type="submit", class_="pyui-button"),
    method="post",
    action=reverse("book-create"),
    hx_post=reverse("book-create"),
    hx_target="#book-results",
    hx_swap="innerHTML",
)
```

Keep Django's `CsrfViewMiddleware` enabled. Validate submitted values in a
Django form or view, verify the user has permission to perform the operation,
and return an appropriate HTML fragment. PyUI components only render the UI;
they do not validate or authorize backend operations.

## 10. Testing and packaging

Run the unit tests from the project root:

```powershell
python -m unittest discover -s tests
```

The component tests cover HTML rendering, escaping, attribute translation,
boolean attributes, invalid event handlers, and void-element behavior. The
example view tests exercise the rendered page and search response.

Install the package in editable mode during local development:

```powershell
python -m pip install -e .
```

The package metadata is in `pyproject.toml`. Package discovery includes
`django_pyui`; the CSS, JavaScript, and Django template are declared as package
data. Before building a distributable, install the build frontend and build
from the project root:

```powershell
python -m pip install build
python -m build
```

Review the generated wheel and source archive before publishing. A package
license and release policy should be selected before redistribution.

For production Django deployments, set `STATIC_ROOT`, run
`python manage.py collectstatic`, and serve the collected assets from your
static-file host or web server.

## 11. Limitations and troubleshooting

### No style appears

- Confirm `django.contrib.staticfiles` and `django_pyui` are in
  `INSTALLED_APPS`.
- Include `{% load static %}` and the `django_pyui/pyui.css` stylesheet URL.
- In production, run `collectstatic` and check the static-file server.

### HTMX attributes do nothing

- Include HTMX on that page; PyUI does not bundle it.
- Check that the generated `hx-*` URL is correct and is included in Django's
  URL configuration.
- Make sure the endpoint returns HTML and `hx-target` matches an element.
- For POST forms, verify that the request includes a valid CSRF token.

### A toggle does nothing

- Load `django_pyui/pyui.js` with `defer`.
- Ensure the selector in `data-pyui-toggle` matches an element ID or selector
  on the page.

### Project boundaries

- PyUI is server-rendered HTML, not a React-like client runtime.
- The set of helper components is deliberately small; use `Element` for other
  HTML tags.
- HTMX, a CSS framework, and custom JavaScript are optional integrations and
  must be loaded by the application.
- The included example uses hard-coded sample data and is for development,
  not production deployment.
- The project has no chosen license yet; check with the owner before reuse or
  redistribution.
