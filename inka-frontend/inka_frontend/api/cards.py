from pathlib import Path
from typing import Optional
from uuid import uuid4

import requests
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from jinja2 import Template
from starlette import status

from inka_frontend.app import template
from inka_frontend.constants import API_SERVER_URL

templates = Jinja2Templates(directory=Path(__file__).parent / "templates")
router = APIRouter()


@router.get("/decks/{deck_id}/cards", response_class=HTMLResponse)
async def cards_page(
    deck_id: str, request: Request, render=Depends(template("private/cards.html"))
):
    response = requests.get(f"{API_SERVER_URL}/decks/{deck_id}")
    response.raise_for_status()
    deck = response.json()
    return render(
        navbar_title=deck["name"],
        deck=deck,
        deck_id=deck_id,
        searchable=True,
        new_item_endpoint=request.url_for("create_card_page", deck_id=deck_id),
        new_item_text="New Card...",
    )


@router.get("/htmx/components/decks/{deck_id}/cards", response_class=HTMLResponse)
async def cards_component(
    deck_id: str, render=Depends(template("responses/cards.html"))
):
    response = requests.get(f"{API_SERVER_URL}/decks/{deck_id}/cards")
    response.raise_for_status()
    cards = response.json()

    response = requests.get(f"{API_SERVER_URL}/schemas")
    response.raise_for_status()
    schemas = response.json()

    response = requests.get(f"{API_SERVER_URL}/functions")
    response.raise_for_status()
    functions = response.json()

    for card in cards.values():
        card["schema_name"] = schemas[card["schema"]]["name"]
        card["preview"] = Template(schemas[card["schema"]]["preview"]).render(**card, **{name: eval(func) for name, func in functions.items()})

    return render(cards=cards, deck_id=deck_id)


@router.get("/decks/{deck_id}/cards/new", response_class=HTMLResponse)
async def create_card_page(deck_id: str, render=Depends(template("private/card.html"))):
    response = requests.get(f"{API_SERVER_URL}/decks/{deck_id}")
    response.raise_for_status()
    deck = response.json()

    response = requests.get(f"{API_SERVER_URL}/schemas")
    response.raise_for_status()
    schemas = response.json()

    for schema in schemas.values():
        schema["rendered_form"] = Template(schema["form"]).render()
    return render(
        navbar_title=deck["name"],
        deck=deck,
        deck_id=deck_id,
        card={
            "schema": "",
            "tags": [],
        },
        card_id=str(uuid4()),
        card_schemas=schemas,
    )


@router.get("/decks/{deck_id}/cards/{card_id}", response_class=HTMLResponse)
async def edit_card_page(
    deck_id: str, card_id: str, render=Depends(template("private/card.html"))
):
    response = requests.get(f"{API_SERVER_URL}/decks/{deck_id}")
    response.raise_for_status()
    deck = response.json()

    response = requests.get(f"{API_SERVER_URL}/decks/{deck_id}/cards/{card_id}")
    response.raise_for_status()
    card = response.json()

    response = requests.get(f"{API_SERVER_URL}/schemas")
    response.raise_for_status()
    schemas = response.json()

    for schema in schemas.values():
        schema["rendered_form"] = Template(schema["form"]).render(**card)

    return render(
        navbar_title=deck["name"],
        deck_id=deck_id,
        card=card,
        card_id=card_id,
        card_schemas=schemas,
    )


@router.post("/decks/{deck_id}/cards/{card_id}", response_class=RedirectResponse)
async def save_card_endpoint(deck_id: str, card_id: Optional[str], request: Request):
    async with request.form() as form:
        response = requests.post(
            f"{API_SERVER_URL}/decks/{deck_id}/cards/{card_id if card_id else ''}",
            json=dict(form),
        )
        response.raise_for_status()

    return RedirectResponse(
        request.url_for("cards_page", deck_id=deck_id),
        status_code=status.HTTP_302_FOUND,
    )


@router.get(
    "/htmx/components/decks/{deck_id}/cards/{card_id}/confirm-delete",
    response_class=HTMLResponse,
)
async def card_confirm_delete_component(
    deck_id: str,
    card_id: str,
    render=Depends(template("components/message-modal.html")),
):
    response = requests.get(f"{API_SERVER_URL}/decks/{deck_id}/cards/{card_id}")
    response.raise_for_status()
    card = response.json()

    response = requests.get(f"{API_SERVER_URL}/schemas")
    response.raise_for_status()
    card_schemas = response.json()

    return render(
        title="Deleting card",
        content="<p>Are you really sure you wanna delete this card?</p><br>"
        + Template(card_schemas[card["schema"]]["preview"]).render(**card),
        positive="Yes, delete it",
        negative="No, don't delete",
        delete_endpoint="delete_card_endpoint",
        endpoint_params={"deck_id": deck_id, "card_id": card_id},
    )


@router.get("/decks/{deck_id}/cards/{card_id}/delete", response_class=RedirectResponse)
async def delete_card_endpoint(
    request: Request,
    deck_id: str,
    card_id: str,
):
    response = requests.delete(f"{API_SERVER_URL}/decks/{deck_id}/cards/{card_id}")
    response.raise_for_status()

    return RedirectResponse(
        request.url_for("cards_page", deck_id=deck_id),
        status_code=status.HTTP_302_FOUND,
    )
