from fastapi import FastAPI

app = FastAPI(debug=True)

from src.web.api import api  # noqa: E402, F401
