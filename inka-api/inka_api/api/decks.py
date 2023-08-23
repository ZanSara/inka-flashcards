import json
import shelve
from copy import deepcopy
from hashlib import md5
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from inka_api.app import database
from starlette import status

router = APIRouter(tags=["decks"])


@router.get("/decks", response_class=JSONResponse)
async def get_decks():
    with shelve.open(database) as db:
        return {key: value for key, value in db["decks"].items() if key != "cards"}


@router.get("/decks/{deck_id}", response_class=JSONResponse)
async def get_deck(deck_id: str):
    with shelve.open(database) as db:
        if deck_id not in db["decks"]:
            raise HTTPException(status_code=404, detail="Deck not found")
        deck = db["decks"][deck_id]
    return {key: value for key, value in deck.items() if key != "cards"}


@router.post("/decks/import", response_class=JSONResponse)
async def import_deck(file: UploadFile):
    try:
        contents = await file.read()
        deck = json.loads(contents)
        with shelve.open(database) as db:
            deck_id = md5(deck["name"].encode()).hexdigest()
            if deck_id in db["decks"]:
                raise HTTPException(
                    status_code=409, detail="Deck with this name already exists"
                )
            db["decks"][deck_id] = deck
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="There was an error importing the deck",
        ) from err
    finally:
        await file.close()
    return {"deck_id": deck_id}


@router.get("/decks/{deck_id}/export", response_class=FileResponse)
async def export_deck(request: Request, deck_id: str):
    with shelve.open(database) as db:
        decks = db["decks"]
        deck = deepcopy(decks.get(deck_id, {}))
        if not deck:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        deck["cards"] = {
            card_id: dict(card.items()) for card_id, card in deck["cards"].items()
        }
        path = Path(__file__).parent.parent / f"tmp/{deck['name']}.json"
        with open(path, "w") as file:
            json.dump(deck, file, indent=4)
    return FileResponse(
        path, media_type="application/octet-stream", filename=f"{deck['name']}.json"
    )


@router.post("/decks/new", response_class=JSONResponse)
async def create_deck(request: Request):
    form = await request.json()
    with shelve.open(database) as db:
        deck_id = md5(form["name"].encode()).hexdigest()
        if deck_id in db["decks"]:
            raise HTTPException(
                status_code=409, detail="Deck with this name already exists"
            )
        db["decks"][deck_id] = {
            **db["decks"].get(deck_id, {"cards": {}}),
            "name": form["name"],
            "description": form["description"],
            "tags": [tag.strip() for tag in form["tags"].split(",") if tag.strip()],
            "algorithm": form["algorithm"],
        }
    return {"deck_id": deck_id}


@router.post("/decks/{deck_id}", response_class=JSONResponse)
async def save_deck(request: Request, deck_id: str):
    form = await request.json()
    with shelve.open(database) as db:
        db["decks"][deck_id] = {
            **db["decks"].get(deck_id, {"cards": {}}),
            "name": form["name"],
            "description": form["description"],
            "tags": [tag.strip() for tag in form["tags"].split(",") if tag.strip()],
            "algorithm": form["algorithm"],
        }
    return {"deck_id": deck_id}


@router.delete("/decks/{deck_id}", response_class=JSONResponse)
async def delete_deck(deck_id: str):
    with shelve.open(database) as db:
        if deck_id not in db["decks"]:
            raise HTTPException(status_code=404, detail="Deck not found")
        del db["decks"][deck_id]
    return {"deck_id": deck_id}
