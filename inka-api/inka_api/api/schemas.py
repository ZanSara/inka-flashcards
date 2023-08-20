import shelve
from hashlib import md5

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from inka_api.app import database

router = APIRouter(tags=["schemas"])


@router.get("/schemas", response_class=JSONResponse)
async def get_schemas():
    with shelve.open(database) as db:
        schemas = db["schemas"]
        for schema in schemas.values():
            schema["usage"] = 0

        # Get all the cards that uses this schema across all decks
        for deck in db["decks"].values():
            for card in deck["cards"].values():
                if card["schema"] in schemas:
                    schemas[card["schema"]]["usage"] += 1

        return schemas


@router.get("/schemas/{schema_id}", response_class=JSONResponse)
async def get_schema(schema_id: str):
    with shelve.open(database) as db:
        schema = dict(
            **db["schemas"].get(schema_id, {})
        )  # To avoid automatic creation of a new schema
        if not schema:
            raise HTTPException(status_code=404, detail="Schema not found")
        if "usage" in schema:
            del schema["usage"]
    return schema


@router.post("/schemas/", response_class=JSONResponse)
async def create_schema(request: Request):
    schema = request.json()
    schema_id = md5(schema["name"].encode()).hexdigest()
    with shelve.open(database) as db:
        if schema_id in db["schemas"]:
            raise HTTPException(status_code=409, detail="Schema with this ID already exists")
        db["schemas"][schema_id] = schema
    return {"schema_id": schema_id}


@router.post("/schemas/{schema_id}", response_class=JSONResponse)
async def update_schema(request: Request, schema_id: str):
    schema = await request.json()
    with shelve.open(database) as db: 
        new_schema_id = md5(schema["name"].encode()).hexdigest()
   
        if new_schema_id != schema_id:
            if new_schema_id in db["schemas"]:
                raise HTTPException(status_code=409, detail="Schema with this ID already exists")
            
            # Cards need to be updated
            for deck_key in db["decks"]:
                for card_key in db["decks"][deck_key]["cards"]:
                    if db["decks"][deck_key]["cards"][card_key]["schema"] == schema_id:
                        db["decks"][deck_key]["cards"][card_key]["schema"] = new_schema_id

            db["schemas"][new_schema_id] = schema
            del db["schemas"][schema_id]
        else:
            db["schemas"][schema_id] = schema
    return {"schema_id": schema_id}


@router.delete("/schemas/{schema_id}", response_class=JSONResponse)
async def delete_schema(request: Request, schema_id: str):
    with shelve.open(database) as db:
        if schema_id not in db["schemas"]:
            raise HTTPException(status_code=404, detail="Schema not found")
        del db["schemas"][schema_id]
    return {"schema_id": schema_id}
