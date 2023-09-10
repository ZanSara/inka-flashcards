import importlib.metadata
import shelve
from functools import partial
from pathlib import Path
from textwrap import dedent
from hashlib import md5
from contextlib import asynccontextmanager
from textwrap import dedent
import base64

from fastapi import FastAPI

__version__ = importlib.metadata.version("inka_api")


database = str(Path(__name__).parent / "inka.db")
shelve.open = partial(shelve.open, writeback=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    with shelve.open(database) as db:
        db.setdefault("decks", {})
        db.setdefault(
            "schemas",
            {
                md5(b"Question & Answer").hexdigest(): {
                    "name": "Question & Answer",
                    "description": "Simple schema with a question and an answer.",
                    "form": dedent(
                        """
                        <label for='question'>Question</label>
                        <input type='text' name='question' value='{{ question }}'>

                        <label for='answer'>Answer</label>
                        <input type='text' name='answer' value='{{ answer }}'>
                    """
                    ),
                    "preview": "{{ question }} -> {{ answer }}",
                    "cards": {
                        "card": {
                            "question": "{{ question }}",
                            "answer": "{{ answer }}",
                        }
                    },
                },
                md5(b"Question & Answer with reverse").hexdigest(): {
                    "name": "Question & Answer with reverse",
                    "description": "Generates two cards: question -> answer and answer -> question.",
                    "form": dedent(
                        """
                        <label for='question'>Question:</label>
                        <input type='text' name='question' value='{{ question }}'>

                        <label for='answer'>Answer:</label>
                        <input type='text' name='answer'  value='{{ answer }}'>
                    """
                    ),
                    "preview": "{{ question }} <-> {{ answer }}",
                    "cards": {
                        "direct": {
                            "question": "{{ question }}",
                            "answer": "{{ answer }}",
                        },
                        "reverse": {
                            "question": "{{ answer }}",
                            "answer": "{{ question }}",
                        },
                    },
                },
            },
        )
    yield


# Create the FastAPI app
app = FastAPI(
    title="Inka Flashcards API server",
    description="API Docs for Inka Flashcards",
    version=__version__,
    lifespan=lifespan,
)


from inka_api.api.study import router as study_router  # noqa: E402
from inka_api.api.decks import router as decks_router  # noqa: E402
from inka_api.api.cards import router as cards_router  # noqa: E402
from inka_api.api.algorithms import router as algorithms_router  # noqa: E402
from inka_api.api.schemas import router as schemas_router  # noqa: E402

app.include_router(study_router)
app.include_router(decks_router)
app.include_router(cards_router)
app.include_router(algorithms_router)
app.include_router(schemas_router)
