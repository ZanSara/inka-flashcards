# Inka Flashcards - API - WIP

[![License: AGPL v3](https://img.shields.io/badge/License-AGPLv3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)   [![Code on: GitHub](https://img.shields.io/badge/Code%20on-GitHub-blueviolet)](https://github.com/ZanSara/inka-frontend)    [![Code style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Inka Flashcards' API backend. Made with FastAPI.

**NOTE**: This is a work-in-progress, not running application.
Do not expect it to just download it and be able to run it if you're not
familiar with Python and HTMX.


# Contribute

```bash
> python3 -m venv venv
> source venv/bin/activate
> pip install -e .
> pre-commit install
> uvicorn inka_api.app:app --reload   # or python inka_api/main.py
INFO:     Started server process [XXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     127.0.0.1:60494 - "GET / HTTP/1.1" 200 OK

... do some changes ...

> pytest
```
The pre-commit hook runs Black and Ruff with fairly standard setups.
Do not send a PR if these checks, or the tests, are failing.
