import shelve
from hashlib import md5

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from inka_api.app import database

router = APIRouter(tags=["functions"])


@router.get("/functions", response_class=JSONResponse)
async def get_functions():
    with shelve.open(database) as db:
        functions = db["functions"]
        return functions


@router.get("/functions/{function_id}", response_class=JSONResponse)
async def get_function(function_id: str):
    with shelve.open(database) as db:
        function = dict(
            **db["functions"].get(function_id, {})
        )  # To avoid automatic creation of a new function
        if not function:
            raise HTTPException(status_code=404, detail="Function not found")
    return function


@router.post("/functions/", response_class=JSONResponse)
async def create_function(request: Request):
    function = request.json()
    function_id = md5(function["name"].encode()).hexdigest()
    with shelve.open(database) as db:
        if function_id in db["functions"]:
            raise HTTPException(status_code=409, detail="Function with this ID already exists")
        db["functions"][function_id] = function
    return {"function_id": function_id}


@router.post("/functions/{function_id}", response_class=JSONResponse)
async def update_function(request: Request, function_id: str):
    function = await request.json()
    with shelve.open(database) as db: 
        new_function_id = md5(function["name"].encode()).hexdigest()
   
        if new_function_id != function_id:
            if new_function_id in db["functions"]:
                raise HTTPException(status_code=409, detail="function with this ID already exists")
            
            # Cards need to be updated
            for deck_key in db["decks"]:
                for card_key in db["decks"][deck_key]["cards"]:
                    if db["decks"][deck_key]["cards"][card_key]["function"] == function_id:
                        db["decks"][deck_key]["cards"][card_key]["function"] = new_function_id

            db["functions"][new_function_id] = function
            del db["functions"][function_id]
        else:
            db["functions"][function_id] = function
    return {"function_id": function_id}


@router.delete("/functions/{function_id}", response_class=JSONResponse)
async def delete_function(request: Request, function_id: str):
    with shelve.open(database) as db:
        if function_id not in db["functions"]:
            raise HTTPException(status_code=404, detail="Function not found")
        del db["functions"][function_id]
    return {"function_id": function_id}
