from src.web.app import app


@app.get("/posts")
async def hello():
    return "Hello"
