import shelve
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from inka_api.algorithms import ALGORITHMS
from inka_api.app import database

router = APIRouter(tags=["study"])


@router.get("/study/{deck_id}", response_class=JSONResponse)
async def get_card_to_study(deck_id: str):
    with shelve.open(database) as db:
        deck = db["decks"].get(deck_id, {})
        if not deck:
            raise HTTPException(status_code=404, detail="Deck not found")

        if not len(deck["cards"]):
            return {"card_id": None, "deck_id": deck_id}

        algorithm = ALGORITHMS[deck["algorithm"]]
        card_id, card_type, question, answer = algorithm.next_card(deck, db["schemas"])
        buttons = algorithm.buttons()

    return {
        "deck": {key: value for key, value in deck.items() if key != "cards"},
        "deck_id": deck_id,
        "card_id": str(card_id),
        "card_type": card_type,
        "question": question,
        "answer": answer,
        "buttons": buttons,
    }


@router.post(
    "/study/{deck_id}/{card_id}/{card_type}/{result}",
    response_class=JSONResponse,
)
async def create_review(
    deck_id: str, card_id: str, card_type: str, result: str, request: Request
):
    with shelve.open(database) as db:
        deck = db["decks"].get(deck_id, {})
        if not deck:
            raise HTTPException(status_code=404, detail="Deck not found")

        algorithm = ALGORITHMS[deck["algorithm"]]
        algorithm.process_result(deck, card_id, card_type, result)

    return {}
