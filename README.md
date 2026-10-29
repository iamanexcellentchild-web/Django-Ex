# Django PyUI

Django PyUI is a small Python-first UI toolkit for Django. Compose ordinary
HTML pages from reusable Python components, keep your backend in Django, and
add browser updates with HTMX when you need them.

It is intended to make common interface code less repetitive. It is not a
replacement for Django, and it does not run a React-style client-side component
tree or state system.

## What it provides

- Python helpers for common HTML elements and layouts.
- Safe HTML escaping for text and attribute values.
- A small CSS layer for cards, inputs, buttons, and flexbox layouts.
- A tiny optional JavaScript toggle hook.
- Ordinary HTML output that works with Django templates, forms, and HTMX.

## Quick start

Requires Python 3.10+ and Django 5.2.

```powershell
git clone https://github.com/iamanexcellentchild-web/Django-Ex.git
cd Django-Ex
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m django runserver --settings=examples.settings
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/). The example shows Python
components, an HTMX search endpoint, and the optional visibility toggle.

## First component page

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

In the Django template, render the result with `{{ page }}`. Add
`django_pyui/pyui.css` to use the bundled styles, and give components your own
`class_` values when an app needs custom styling.

## Documentation

See the [Django PyUI guide](docs/django-pyui-guide.md) for installation,
component and attribute references, CSS customization, Django and HTMX
integration, accessibility and security notes, testing, packaging, and known
limitations.

## Run tests

```powershell
python -m unittest discover -s tests
```

## License

No license has been selected for this project yet. Ask the repository owner
before reusing or redistributing it.
