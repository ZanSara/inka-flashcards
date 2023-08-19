source venv/bin/activate
uvicorn inka_api.app:app --reload --app-dir=inka-api --port=8001 & uvicorn inka_frontend.app:app --reload --app-dir=inka-frontend --port=8000
