from fastapi import FastAPI

app = FastAPI()

from src.web.api import api  # noqa: E402, F401
