from src.web.core.config import settings


def signup_and_auth(client, username="string", password="password"):
    client.post("/users/signup", data={"username": username, "password": password})
    access_token = client.post(
        f"/auth/{settings.access_token_url}",
        data={"grant_type": "password", "username": username, "password": password},
    ).json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    return headers
