import importlib.metadata
from datetime import datetime
from pathlib import Path
from typing import Any
import base64


import requests
from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import HTTPException, StarletteHTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, pass_context
from jinja2.loaders import PackageLoader

__version__ = importlib.metadata.version("inka_frontend")


def get_jinja2():
    """Get Jinja2 dependency function. you can define more functions, filters or global vars here"""

    @pass_context
    def url_for(context: dict, name: str, **path_params: Any) -> str:
        request = context["request"]
        return request.url_for(name, **path_params)

    env = Environment(loader=PackageLoader("inka_frontend"), autoescape=True)
    env.globals["url_for"] = url_for
    env.globals["this_year"] = datetime.utcnow().year  # noqa: DTZ003
    env.globals['b64encode'] = lambda string: base64.b64encode(string.encode()).decode()
    env.globals['b64decode'] = lambda string:  base64.b64decode(string).decode()
    env.globals["audio_player"] = lambda url, elem_id="audio": f"""
    <audio id='{elem_id}' src='{url}'></audio>
    <i onclick="document.getElementById('{elem_id}').play()" class="fas fa-volume-up" style='margin-left:1rem;'></i>
    """

    return env


def template(tpl: str):
    """Get view render function using Jinja2 environment injected above"""

    def func_view(request: Request, env: Environment = Depends(get_jinja2)):
        template = env.get_template(tpl)

        def render(*args, **kwargs):
            return template.render(*args, request=request, **kwargs)

        return render

    return func_view


# Create the FastAPI app
app = FastAPI(
    version=__version__,
)
app.mount(
    "/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static"
)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    template = get_jinja2().get_template("public/http_error.html")
    response = template.render(
        request=request, code=exc.status_code, message=exc.detail
    )
    return HTMLResponse(response, status_code=exc.status_code)


@app.exception_handler(requests.HTTPError)
async def requests_http_error_handler(request: Request, exc: requests.HTTPError):
    template = get_jinja2().get_template("public/http_error.html")
    response = template.render(
        request=request, code=exc.response.status_code, message=exc
    )
    return HTMLResponse(response, status_code=exc.response.status_code)


from inka_frontend.api.cards import router as cards_router  # noqa: E402
from inka_frontend.api.decks import router as decks_router  # noqa: E402
from inka_frontend.api.private import router as private_router  # noqa: E402
from inka_frontend.api.public import router as public_router  # noqa: E402
from inka_frontend.api.schemas import router as schemas_router  # noqa: E402
from inka_frontend.api.study import router as study_router  # noqa: E402

app.include_router(public_router)  # type: ignore
app.include_router(private_router)  # type: ignore
app.include_router(study_router)  # type: ignore
app.include_router(decks_router)  # type: ignore
app.include_router(cards_router)  # type: ignore
app.include_router(schemas_router)  # type: ignore
