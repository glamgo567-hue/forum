async def test_successful_registration(client):
    payload = {"username": "glamgo2",
               "email": "glamgo@gmail.com",
               "password": "1",
               "confirm_password": "1"}
    response = await client.post("/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "password" not in data
    assert data["username"] == payload["username"]
    assert data["email"] == payload["email"]
    assert data["reputation"] == 0
    response = await client.post("/auth/register", json=payload)
    assert response.status_code == 409

async def test_successful_login(client):
    payload_auth = {"username": "glamgo2",
                    "email": "glamgo@gmail.com",
                    "password": "1",
                    "confirm_password": "1"}
    response_auth = await client.post("/auth/register", json=payload_auth)
    assert response_auth.status_code == 201

    payload_log1 = {"username":"glamgo2",
                    "password":"1"}
    response_log1 = await client.post("/auth/login", data=payload_log1)
    assert response_log1.status_code == 200

    payload_log2 = {"username":"glamgo2",
                    "password":"2"}
    response_log2 = await client.post("/auth/login", data=payload_log2)
    assert response_log2.status_code == 401

    payload_log3 = {"username":"glamgo3",
                    "password":"1"}
    response_log3 = await client.post("/auth/login", data=payload_log3)
    assert response_log3.status_code == 401

async def test_successful_me(client):
    payload_auth = {"username": "glamgo2",
                    "email": "glamgo@gmail.com",
                    "password": "1",
                    "confirm_password": "1"}
    response_auth = await client.post("/auth/register", json=payload_auth)
    assert response_auth.status_code == 201

    payload_log1 = {"username":"glamgo2",
                    "password":"1"}
    response_log1 = await client.post("/auth/login", data=payload_log1)
    assert response_log1.status_code == 200

    response_tok1 = await client.get("/auth/me")
    assert response_tok1.status_code == 401

    token_data = response_log1.json()
    assert token_data.get("access_token")
    token = token_data.get("access_token")
    response_tok2 = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response_tok2.status_code == 200
