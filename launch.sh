source venv/bin/activate
uvicorn inka_api.app:app --reload --app-dir=inka-api --host=0.0.0.0 --port=8001 & uvicorn inka_frontend.app:app --reload --app-dir=inka-frontend --host=0.0.0.0 --port=8000
