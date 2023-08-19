import shelve
from hashlib import md5

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from inka_api.app import database

router = APIRouter(tags=["schemas"])


@router.get("/schemas", response_class=JSONResponse)
async def get_schemas():
    """
    Get all schemas from the database
    """
    with shelve.open(database) as db:
        schemas = db["schemas"]
        for schema in schemas.values():
            schema["usage"] = 0

        # Get all the cards that uses this schema across all decks
        for deck in db["decks"].values():
            for card in deck["cards"].values():
                if card["schema"] in schemas:
                    schemas[card["schema"]]["usage"] += 1

        return JSONResponse(schemas=schemas)


@router.get("/schemas/{schema_id}", response_class=JSONResponse)
async def get_schema(schema_id: str):
    """
    Get a schema from the database
    """
    with shelve.open(database) as db:
        schema = dict(
            **db["schemas"].get(schema_id, {})
        )  # To avoid automatic creation of a new schema
        del schema["usage"]
        if not schema:
            raise HTTPException(status_code=404, detail="Schema not found")
    return JSONResponse(schema_id=schema_id, schema=schema)


@router.post("/schema/", response_class=JSONResponse)
async def create_schema(request: Request):
    """
    Save a new schema to the database
    """
    async with request.form() as form:
        schema = eval(form["code"])  # noqa: S307
        schema_id = md5(schema["name"].encode()).hexdigest()
        with shelve.open(database) as db:
            if schema_id in db["schemas"]:
                raise HTTPException(
                    status_code=409, detail="Schema with this ID already exists"
                )
            db["schemas"][schema_id] = schema
    return JSONResponse(schema_id=schema_id)


@router.delete("/schemas/{schema_id}", response_class=JSONResponse)
async def delete_schema(request: Request, schema_id: str):
    with shelve.open(database) as db:
        if schema_id not in db["schemas"]:
            raise HTTPException(status_code=404, detail="Schema not found")
        del db["schemas"][schema_id]
    return JSONResponse(schema_id=schema_id)
