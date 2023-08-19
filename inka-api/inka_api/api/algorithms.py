import shelve
from hashlib import md5

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from inka_api.app import database
from inka_api.algorithms import ALGORITHMS

router = APIRouter(tags=["algorithm"])


@router.get("/algorithms", response_class=JSONResponse)
async def get_algorithms():
    return {"algorithms": list(ALGORITHMS.keys())}
