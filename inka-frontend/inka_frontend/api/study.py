from pathlib import Path

import requests
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from inka_frontend.constants import API_SERVER_URL
from inka_frontend.app import template
from starlette import status

templates = Jinja2Templates(directory=Path(__file__).parent / "templates")
router = APIRouter()


@router.get("/study/{deck_id}", response_class=HTMLResponse)
async def study_page(deck_id: str, render=Depends(template("private/study.html"))):
    response = requests.get(f"{API_SERVER_URL}/decks/{deck_id}")
    response.raise_for_status()
    deck = response.json()
    return render(navbar_title=deck["name"], deck_id=deck_id)


@router.get("/htmx/components/decks/{deck_id}/study", response_class=HTMLResponse)
async def study_component(
    deck_id: str, render=Depends(template("responses/study.html"))
):
    response = requests.get(f"{API_SERVER_URL}/study/{deck_id}")
    response.raise_for_status()
    return render(**response.json())


@router.post(
    "/htmx/components/decks/{deck_id}/study/{card_id}/{card_type}/{result}",
    response_class=RedirectResponse,
)
async def save_review_component(
    deck_id: str, card_id: str, card_type: str, result: str, request: Request
):
    response = requests.post(
        f"{API_SERVER_URL}/study/{deck_id}/{card_id}/{card_type}/{result}"
    )
    response.raise_for_status()
    return RedirectResponse(
        request.url_for("study_component", deck_id=deck_id),
        status_code=status.HTTP_302_FOUND,
    )
