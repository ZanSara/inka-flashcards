import os

#: The domain name where this app is deployed
DOMAIN = os.environ.get("FLASHCARDS_DOMAIN", "localhost")

#: API server address
API_SERVER_URL = os.environ.get("FLASHCARDS_API_SERVER", "http://localhost:8001")
