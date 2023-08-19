import shelve
from typing import Optional

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from inka_api.app import database

router = APIRouter(tags=["cards"])


@router.get("/decks/{deck_id}/cards", response_class=JSONResponse)
async def get_cards(deck_id: str):
    with shelve.open(database) as db:
        deck = db["decks"].get(deck_id, {})
        if not deck:
            raise HTTPException(status_code=404, detail="Deck not found")
    return deck["cards"]


@router.get("/decks/{deck_id}/cards/{card_id}", response_class=JSONResponse)
async def get_card(deck_id: str, card_id: str):
    with shelve.open(database) as db:
        deck = db["decks"].get(deck_id, {})
        if not deck:
            raise HTTPException(status_code=404, detail="Deck not found")
        card = deck["cards"].get(card_id, {})
        if not card:
            raise HTTPException(status_code=404, detail="Card not found")
    return card


@router.post("/decks/{deck_id}/cards/{card_id}", response_class=JSONResponse)
async def save_card(deck_id: str, card_id: Optional[str], request: Request):
    async with request.form() as form:
        with shelve.open(database) as db:
            deck = db["decks"].get(deck_id, {})

            deck["cards"][card_id] = {
                **deck["cards"].get(card_id, {"reviews": {}}),
                **form,
            }
            if deck["cards"][card_id]["tags"]:
                deck["cards"][card_id]["tags"] = [
                    tag.strip() for tag in form["tags"].split(",") if tag.strip()
                ]

            # Create empty reviews
            for card_type in db["schemas"][deck["cards"][card_id]["schema"]]["cards"]:
                deck["cards"][card_id]["reviews"][card_type] = deck["cards"][card_id][
                    "reviews"
                ].get(card_type, None)

    return {"card_id": card_id}


@router.delete("/decks/{deck_id}/cards/{card_id}", response_class=JSONResponse)
async def delete_card(deck_id: str, card_id: str):
    with shelve.open(database) as db:
        if deck_id not in db["decks"]:
            raise HTTPException(status_code=404, detail="Deck not found")
        if card_id not in db["decks"][deck_id]["cards"]:
            raise HTTPException(status_code=404, detail="Card not found")
        del db["decks"][deck_id]["cards"][card_id]
    return {"card_id": card_id}
