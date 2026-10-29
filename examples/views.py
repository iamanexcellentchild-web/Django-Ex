from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from django_pyui import Button, Column, Div, Heading, Input, Text

ITEMS = ["Django", "HTMX", "Python components", "JavaScript hooks"]


def home(request: HttpRequest) -> HttpResponse:
    page = Column(
        Heading("Build pages with Python"),
        Text("Compose safe HTML in Python and add interactivity only where you need it."),
        Heading("A little JavaScript", level=2),
        Button(
            "Toggle details",
            data_pyui_toggle="#details",
            aria_controls="details",
            aria_expanded="false",
        ),
        Div(
            "This section is toggled by the small PyUI JavaScript helper.",
            id="details",
            hidden=True,
        ),
        Heading("A little HTMX", level=2),
        Input(
            type="search",
            name="q",
            placeholder="Search the example...",
            aria_label="Search the example",
            hx_get="/search/",
            hx_trigger="keyup changed delay:300ms",
            hx_target="#search-results",
            hx_swap="innerHTML",
        ),
        Div(Text("Matching items will appear here."), id="search-results"),
    )
    return render(request, "django_pyui/index.html", {"page": page})


def search(request: HttpRequest) -> HttpResponse:
    query = request.GET.get("q", "").strip().casefold()
    matches = [item for item in ITEMS if query in item.casefold()] if query else []
    result = (
        Column(*(Div(item, class_="result") for item in matches))
        if matches
        else Div("No matching items.", class_="result")
    )
    return HttpResponse(str(result))
