class TestAuth:
    username = "string"
    password = "12345678"

    @property
    def data(self):
        return {"username": TestAuth.username, "password": TestAuth.password}

    @property
    def access_token_data(self):
        d = self.data
        d["grant_type"] = "password"
        return d

    def test_access_token(self, client):
        response = client.post("/auth/access-token", data=self.access_token_data)
        assert response.status_code == 401, response.text

        client.post("/users/signup", data=self.data)
        response = client.post("/auth/access-token", data=self.access_token_data)
        assert response.status_code == 200, response.text

        data = response.json()
        access_token, token_type = data["access_token"], data["token_type"]
        assert access_token
        assert token_type.lower() == "bearer"

        response = client.post(
            "/auth/access-token",
            data={
                "username": "hello",
                "grant_type": "password",
                "password": "12345678",
            },
        )
        assert response.status_code == 401, response.text
