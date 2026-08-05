async def test_create_question(client, auth_headers):
    payload_question = {"title": "Steak doneness?",
                        "body": "How do I check medium-rare?",
                        "tags": ["cooking"]}
    response_question1 = await client.post("/questions", json=payload_question, headers=auth_headers)
    assert response_question1.status_code == 201

    response_question2 = await client.post("/questions", json=payload_question)
    assert response_question2.status_code == 401

async def test_identical_tags(client, auth_headers):
    payload_question1 = {"title": "Steak doneness?",
                         "body": "How do I check medium-rare?",
                         "tags": ["cooking"]}
    payload_question2 = {"title": "How long to boil an egg?", 
                         "body": "Soft or hard?", 
                         "tags": ["cooking"]}

    response_question1 = await client.post("/questions", json=payload_question1, headers=auth_headers)
    response_question2 = await client.post("/questions", json=payload_question2, headers=auth_headers)

    assert response_question1.status_code == 201
    assert response_question2.status_code == 201    

    assert response_question1.json()["tags"][0]["id"] == response_question2.json()["tags"][0]["id"]

async def test_show_questions(client, auth_headers):
    payload_question1 = {"title": "Steak doneness?",
                         "body": "How do I check medium-rare?",
                         "tags": ["cooking"]}
    payload_question2 = {"title": "How long to boil an egg?", 
                         "body": "Soft or hard?", 
                         "tags": ["cooking"]}

    response_question1 = await client.post("/questions", json=payload_question1, headers=auth_headers)
    response_question2 = await client.post("/questions", json=payload_question2, headers=auth_headers)

    assert response_question1.status_code == 201
    assert response_question2.status_code == 201

    response_question3 = await client.get("/questions", headers=auth_headers)

    assert response_question3.status_code == 200

    data = response_question3.json()
    assert len(data) == 2
    assert data[0]["tags"]
    assert data[1]["tags"]

async def test_show_question(client, auth_headers):
    payload_question = {"title": "Steak doneness?",
                         "body": "How do I check medium-rare?",
                         "tags": ["cooking"]}

    response_question1 = await client.post("/questions", json=payload_question, headers=auth_headers)
    assert response_question1.status_code == 201

    question_id = response_question1.json()["id"]
    response_question2 = await client.get(f"/questions/{question_id}", headers=auth_headers)
    assert response_question2.status_code == 200

async def test_patch_question(client, auth_headers):
    payload_question1 = {"title": "Steak doneness?",
                         "body": "How do I check medium-rare?",
                         "tags": ["cooking"]}

    response_question1 = await client.post("/questions", json=payload_question1, headers=auth_headers)
    assert response_question1.status_code == 201

    payload_auth = {"username": "glamgo3",
                    "email": "glamgo3@gmail.com",
                    "password": "111111111",
                    "confirm_password": "111111111"}
    await client.post("/auth/register", json=payload_auth)
    payload_log = {"username":"glamgo3",
                    "password":"111111111"}
    response_log = await client.post("/auth/login", data=payload_log)
    token_data = response_log.json()
    token = token_data.get("access_token")


    payload_question2 = {"title": "How long to boil an egg?", 
                         "body": "Soft or hard?", 
                         "tags": ["cooking"]}

    response_question2 = await client.post("/questions", json=payload_question2, headers={"Authorization": f"Bearer {token}"})   
    assert response_question2.status_code == 201

    question_id = response_question1.json()["id"]
    response_question3 = await client.patch(f"/questions/{question_id}",json={"title": "Updated"}, headers=auth_headers)
    assert response_question3.status_code == 200

    question_id = response_question2.json()["id"]
    response_question3 = await client.patch(f"/questions/{question_id}",json={"title": "Updated"}, headers=auth_headers)
    assert response_question3.status_code == 403

async def test_delete_question(client, auth_headers):
    payload_question1 = {"title": "Steak doneness?",
                         "body": "How do I check medium-rare?",
                         "tags": ["cooking"]}

    response_question1 = await client.post("/questions", json=payload_question1, headers=auth_headers)
    assert response_question1.status_code == 201

    payload_auth = {"username": "glamgo3",
                    "email": "glamgo3@gmail.com",
                    "password": "111111111",
                    "confirm_password": "111111111"}
    await client.post("/auth/register", json=payload_auth)
    payload_log = {"username":"glamgo3",
                    "password":"111111111"}
    response_log = await client.post("/auth/login", data=payload_log)
    token_data = response_log.json()
    token = token_data.get("access_token")


    payload_question2 = {"title": "How long to boil an egg?", 
                         "body": "Soft or hard?", 
                         "tags": ["cooking"]}

    response_question2 = await client.post("/questions", json=payload_question2, headers={"Authorization": f"Bearer {token}"})   
    assert response_question2.status_code == 201

    question_id = response_question1.json()["id"]
    response_question3 = await client.delete(f"/questions/{question_id}", headers=auth_headers)
    assert response_question3.status_code == 204

    question_id = response_question2.json()["id"]
    response_question3 = await client.delete(f"/questions/{question_id}", headers=auth_headers)
    assert response_question3.status_code == 403

    question_id = response_question1.json()["id"]
    response_question2 = await client.get(f"/questions/{question_id}", headers=auth_headers)
    assert response_question2.status_code == 404