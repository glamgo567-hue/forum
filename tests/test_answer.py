async def test_create_answer(client, auth_headers, question):
    payload_answer = {"body": "Rest it 5 minutes, internal temp ~135°F.",
                      "question_id": question["id"]}

    response_answer1 = await client.post(f"/questions/{question["id"]}/answers", json=payload_answer, headers=auth_headers)
    assert response_answer1.status_code == 201

    response_answer2 = await client.post(f"/questions/{question["id"]}/answers", json=payload_answer)
    assert response_answer2.status_code == 401

async def test_show_answers(client, auth_headers, question):
    payload_answer1 = {"body": "Rest it 5 minutes, internal temp ~135°F.",
                       "question_id": question["id"]}

    payload_answer2 = {"body": "Rest it 30 minutes, internal temp ~100°F.",
                       "question_id": question["id"]}

    response_answer1 = await client.post(f"/questions/{question["id"]}/answers", json=payload_answer1, headers=auth_headers)
    assert response_answer1.status_code == 201

    response_answer2 = await client.post(f"/questions/{question["id"]}/answers", json=payload_answer2, headers=auth_headers)
    assert response_answer2.status_code == 201

    response_answer3 = await client.get(f"/questions/{question["id"]}/answers", headers=auth_headers)

    assert response_answer3.status_code == 200

    data = response_answer3.json()
    assert len(data) == 2
    assert data[0]["body"]
    assert data[1]["body"]

async def test_patch_answer(client, auth_headers, question):
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

    payload_answer1 = {"body": "Rest it 5 minutes, internal temp ~135°F.",
                       "question_id": question["id"]}

    payload_answer2 = {"body": "Rest it 30 minutes, internal temp ~100°F.",
                       "question_id": question["id"]}

    response_answer1 = await client.post(f"/questions/{question["id"]}/answers", json=payload_answer1, headers=auth_headers)
    assert response_answer1.status_code == 201

    response_answer2 = await client.post(f"/questions/{question["id"]}/answers", json=payload_answer2, headers={"Authorization": f"Bearer {token}"})
    assert response_answer2.status_code == 201

    answer_id = response_answer1.json()["id"]
    response_answer3 = await client.patch(f"/answers/{answer_id}",json={"body": "Updated"}, headers=auth_headers)
    assert response_answer3.status_code == 200

    answer_id = response_answer2.json()["id"]
    response_answer4 = await client.patch(f"/answers/{answer_id}",json={"body": "Updated"}, headers=auth_headers)
    assert response_answer4.status_code == 403

async def test_delete_answer(client, auth_headers, question):
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

    payload_answer1 = {"body": "Rest it 5 minutes, internal temp ~135°F.",
                       "question_id": question["id"]}

    payload_answer2 = {"body": "Rest it 30 minutes, internal temp ~100°F.",
                       "question_id": question["id"]}

    response_answer1 = await client.post(f"/questions/{question["id"]}/answers", json=payload_answer1, headers=auth_headers)
    assert response_answer1.status_code == 201

    response_answer2 = await client.post(f"/questions/{question["id"]}/answers", json=payload_answer2, headers={"Authorization": f"Bearer {token}"})
    assert response_answer2.status_code == 201

    answer_id = response_answer1.json()["id"]
    response_answer3 = await client.delete(f"/answers/{answer_id}", headers=auth_headers)
    assert response_answer3.status_code == 204

    answer_id = response_answer2.json()["id"]
    response_answer4 = await client.delete(f"/answers/{answer_id}", headers=auth_headers)
    assert response_answer4.status_code == 403

    response_list = await client.get(f"/questions/{question['id']}/answers")
    answer_ids = [a["id"] for a in response_list.json()]
    assert response_answer1.json()["id"] not in answer_ids