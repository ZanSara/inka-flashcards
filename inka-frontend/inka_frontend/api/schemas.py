from hashlib import md5
from pathlib import Path
from textwrap import dedent

import requests
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette import status

from inka_frontend.app import template
from inka_frontend.constants import API_SERVER_URL

templates = Jinja2Templates(directory=Path(__file__).parent / "templates")
router = APIRouter()


@router.get("/schemas", response_class=HTMLResponse)
async def schemas_page(
    request: Request, render=Depends(template("private/schemas.html"))
):
    return render(
        navbar_title="Schemas",
        searchable=True,
        new_item_endpoint=request.url_for("create_schema_page"),
        new_item_text="New Schema...",
    )


@router.get("/htmx/components/schemas", response_class=HTMLResponse)
async def schemas_component(render=Depends(template("responses/schemas.html"))):
    response = requests.get(f"{API_SERVER_URL}/schemas")
    response.raise_for_status()
    schemas = response.json()
    return render(schemas=schemas)


@router.get("/schemas/new", response_class=HTMLResponse)
async def create_schema_page(render=Depends(template("private/schema-code.html"))):
    return render(
        navbar_title="New Schema",
        schema_id=None,
        schema={
            "name": "New Schema",
            "description": "The schema's description.",
            "form": dedent(
                """
                <label for='question'>Question</label>
                <input type='text' name='question' value={{ question }}>

                <label for='answer'>Answer</label>
                <input type='text' name='answer'  value={{ answer }}>
            """
            ),
            "cards": {
                "card": {
                    "sides": {
                        "Question": "{{ question }}",
                        "Answer": "{{ answer }}",
                    },
                    "preview": "{{ question }} -> {{ answer }}",
                    "flip_order": "['Question', 'Answer']",
                },
            },
        },
    )


@router.get("/schemas/view/{schema_id}", response_class=HTMLResponse)
async def view_schema_page(
    schema_id: str, render=Depends(template("private/schema-readonly.html"))
):
    response = requests.get(f"{API_SERVER_URL}/schemas/{schema_id}")
    response.raise_for_status()
    schema = response.json()
    return render(
        navbar_title=schema["name"],
        schema_id=schema_id,
        schema=schema,
    )


@router.get("/schemas/edit/{schema_id}", response_class=HTMLResponse)
async def edit_schema_page(
    schema_id: str, render=Depends(template("private/schema-code.html"))
):
    response = requests.get(f"{API_SERVER_URL}/schemas/{schema_id}")
    response.raise_for_status()
    schema = response.json()
    return render(
        navbar_title=schema["name"],
        schema_id=schema_id,
        old_schema_id=schema_id,
        schema=schema,
        editing_existing=True
    )


@router.get("/schemas/clone/{schema_id}", response_class=HTMLResponse)
async def clone_schema_page(
    schema_id: str, render=Depends(template("private/schema-code.html"))
):
    response = requests.get(f"{API_SERVER_URL}/schemas/{schema_id}")
    response.raise_for_status()
    schema = response.json()
    schema["name"] = "Clone of " + schema["name"]
    new_schema_id = md5(schema["name"].encode()).hexdigest()
    return render(
        navbar_title=schema["name"],
        schema_id=new_schema_id,
        old_schema_id=schema_id,
        schema=schema,
    )


@router.post("/schemas/", response_class=RedirectResponse)
async def create_schema_endpoint(request: Request):
    async with request.form() as form:
        schema = eval(form["code"])  # noqa: S307
        schema_id = md5(schema["name"].encode()).hexdigest()
        response = requests.post(f"{API_SERVER_URL}/schemas/{schema_id}", json=schema)
        response.raise_for_status()
    return RedirectResponse(
        request.url_for("schemas_page"), status_code=status.HTTP_302_FOUND
    )


@router.post("/schemas/{schema_id}", response_class=RedirectResponse)
async def update_schema_endpoint(request: Request, schema_id: str):
    async with request.form() as form:
        try:
            schema = eval(form["code"])  # noqa: S307
        except Exception as exc:
            raise HTTPException(500, f"Syntax error in schema code: {exc}") from exc
        response = requests.post(f"{API_SERVER_URL}/schemas/{schema_id}", json=schema)
        response.raise_for_status()
    return RedirectResponse(
        request.url_for("schemas_page"), status_code=status.HTTP_302_FOUND
    )


@router.get(
    "/htmx/components/schemas/{schema_id}/confirm-delete", response_class=HTMLResponse
)
async def schema_confirm_delete_component(
    schema_id: str, render=Depends(template("components/message-modal.html"))
):
    response = requests.get(f"{API_SERVER_URL}/schemas/{schema_id}")
    response.raise_for_status()
    schema = response.json()
    return render(
        title="Deleting schema",
        content=f"Are you really sure you wanna delete the schema '{schema['name']}'?",
        positive=f"Yes, delete {schema['name']}",
        negative="No, don't delete",
        delete_endpoint="delete_schema_endpoint",
        endpoint_params={"schema_id": schema_id},
    )


@router.get("/schemas/{schema_id}/delete", response_class=RedirectResponse)
async def delete_schema_endpoint(request: Request, schema_id: str):
    response = requests.delete(f"{API_SERVER_URL}/schemas/{schema_id}")
    response.raise_for_status()
    return RedirectResponse(
        request.url_for("schemas_page"), status_code=status.HTTP_302_FOUND
    )
