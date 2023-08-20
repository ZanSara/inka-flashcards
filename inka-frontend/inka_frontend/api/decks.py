import json

from pathlib import Path
from typing import Optional

import requests
from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette import status

from inka_frontend.constants import API_SERVER_URL
from inka_frontend.app import template


templates = Jinja2Templates(directory=Path(__file__).parent / "templates")
router = APIRouter()


@router.get("/home", response_class=HTMLResponse)
async def home_page(request: Request, render=Depends(template("private/home.html"))):
    return render(
        navbar_title="Home",
        searchable=True,
        new_item_endpoint=request.url_for("create_deck_page"),
        upload_item_endpoint=request.url_for("import_deck_page"),
        new_item_text="New Deck...",
    )


@router.get("/htmx/components/decks", response_class=HTMLResponse)
async def decks_component(render=Depends(template("responses/decks.html"))):
    response = requests.get(f"{API_SERVER_URL}/decks")
    response.raise_for_status()
    decks = response.json()
    return render(decks=decks)


@router.get("/htmx/components/decks/search_filters", response_class=HTMLResponse)
async def decks_search_component(
    render=Depends(template("components/filter-modal.html")),
):
    return render(
        title="decks", content="Content here", positive="Search", negative="Cancel"
    )


@router.get("/decks/new", response_class=HTMLResponse)
async def create_deck_page(render=Depends(template("private/deck.html"))):
    response = requests.get(f"{API_SERVER_URL}/algorithms")
    response.raise_for_status()
    algorithms = response.json()["algorithms"]
    return render(
        navbar_title="New Deck",
        deck={"name": "", "description": ""},
        algorithms=algorithms,
    )


@router.get("/decks/import", response_class=HTMLResponse)
async def import_deck_page(render=Depends(template("private/import.html"))):
    return render(navbar_title="Import Deck")


@router.post("/decks/import", response_class=RedirectResponse)
async def import_deck_endpoint(file: UploadFile):
    try:
        contents = await file.read()
        deck = json.loads(contents)
        response = requests.post(f"{API_SERVER_URL}/decks/import", json=deck)
        response.raise_for_status()

    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="There was an error importing the deck",
        ) from err
    finally:
        await file.close()
    return RedirectResponse(
        router.url_path_for("home_page"), status_code=status.HTTP_302_FOUND
    )


@router.get("/decks/{deck_id}/export", response_class=FileResponse)
async def export_deck_endpoint(request: Request):
    return requests.get(
        f"{API_SERVER_URL}/decks/export/{request.path_params['deck_id']}"
    )


@router.get("/decks/{deck_id}", response_class=HTMLResponse)
async def edit_deck_page(deck_id: str, render=Depends(template("private/deck.html"))):
    response = requests.get(f"{API_SERVER_URL}/algorithms")
    response.raise_for_status()
    algorithms = response.json()["algorithms"]

    response = requests.get(f"{API_SERVER_URL}/decks/{deck_id}")
    response.raise_for_status()
    deck = response.json()

    return render(
        navbar_title=deck["name"], deck=deck, deck_id=deck_id, algorithms=algorithms
    )


@router.post("/decks/new", response_class=RedirectResponse)
async def create_deck_endpoint(request: Request, deck_id: Optional[str] = None):
    async with request.form() as form:
        response = requests.post(
            f"{API_SERVER_URL}/decks/new",
            json=dict(form),
        )
        response.raise_for_status()
    return RedirectResponse(
        request.url_for("home_page"), status_code=status.HTTP_302_FOUND
    )


@router.post("/decks/{deck_id}", response_class=RedirectResponse)
async def save_deck_endpoint(request: Request, deck_id: str):
    async with request.form() as form:
        response = requests.post(
            f"{API_SERVER_URL}/decks/{deck_id}",
            json=dict(form),
        )
        response.raise_for_status()
    return RedirectResponse(
        request.url_for("home_page"), status_code=status.HTTP_302_FOUND
    )


@router.get(
    "/htmx/components/decks/{deck_id}/confirm-delete", response_class=HTMLResponse
)
async def deck_confirm_delete_component(
    deck_id: str, render=Depends(template("components/message-modal.html"))
):
    response = requests.get(f"{API_SERVER_URL}/decks/{deck_id}")
    response.raise_for_status()
    deck = response.json()
    return render(
        title="Deleting deck",
        content=f"Are you really sure you wanna delete the deck '{deck['name']}'? It contains {len(deck['cards'])} cards.",
        positive=f"Yes, delete {deck['name']}",
        negative="No, don't delete",
        delete_endpoint="delete_deck_endpoint",
        endpoint_params={"deck_id": deck_id},
    )


@router.get("/decks/{deck_id}/delete", response_class=RedirectResponse)
async def delete_deck_endpoint(request: Request, deck_id: str):
    response = requests.delete(f"{API_SERVER_URL}/decks/{deck_id}")
    response.raise_for_status()
    return RedirectResponse(
        request.url_for("home_page"), status_code=status.HTTP_302_FOUND
    )
