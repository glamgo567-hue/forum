async def test_successful_accept(client, auth_headers, question, dop_auth_headers):
    payload_answer = {"body": "Rest it 5 minutes, internal temp ~135°F.",
                      "question_id": question["id"]}
    response_answer = await client.post(f"/questions/{question['id']}/answers", json=payload_answer, headers=dop_auth_headers)
    assert response_answer.status_code == 201
    answer_id = response_answer.json()["id"]

    response_accept = await client.patch(f"/answers/{answer_id}/accept", headers=auth_headers)
    assert response_accept.status_code == 200
    assert response_accept.json()["is_accepted"] == True

    response_me = await client.get("/auth/me", headers=dop_auth_headers)
    assert response_me.json()["reputation"] == 20

    response_accept = await client.patch(f"/answers/{answer_id}/accept", headers=dop_auth_headers)
    assert response_accept.status_code == 403

async def test_switching_accept(client, auth_headers, question, dop_auth_headers):
    payload_auth3 = {"username": "glamgo4",
                 "email": "glamgo4@gmail.com",
                 "password": "111111111",
                 "confirm_password": "111111111"}
    await client.post("/auth/register", json=payload_auth3)

    payload_log3 = {"username": "glamgo4", "password": "111111111"}
    response_log3 = await client.post("/auth/login", data=payload_log3)
    token3 = response_log3.json().get("access_token")
    tret_auth_headers = {"Authorization": f"Bearer {token3}"}

    payload_answer1 = {"body": "Rest it 5 minutes, internal temp ~135°F.",
                      "question_id": question["id"]}
    response_answer1 = await client.post(f"/questions/{question['id']}/answers", json=payload_answer1, headers=dop_auth_headers)
    assert response_answer1.status_code == 201
    answer1_id = response_answer1.json()["id"]

    response_accept1 = await client.patch(f"/answers/{answer1_id}/accept", headers=auth_headers)
    assert response_accept1.status_code == 200
    assert response_accept1.json()["is_accepted"] == True

    payload_answer2 = {"body": "Rest it 30 minutes, internal temp ~100°F.",
                      "question_id": question["id"]}
    response_answer2 = await client.post(f"/questions/{question['id']}/answers", json=payload_answer2, headers=tret_auth_headers)
    assert response_answer2.status_code == 201
    answer2_id = response_answer2.json()["id"]

    response_accept2 = await client.patch(f"/answers/{answer2_id}/accept", headers=auth_headers)
    assert response_accept2.status_code == 200
    assert response_accept2.json()["is_accepted"] == True

    response_list = await client.get(f"/questions/{question['id']}/answers")
    answers_data = {a["id"]: a for a in response_list.json()}
    assert answers_data[answer1_id]["is_accepted"] == False

    response_me_dop = await client.get("/auth/me", headers=dop_auth_headers)
    assert response_me_dop.json()["reputation"] == 20

    response_me_tret = await client.get("/auth/me", headers=tret_auth_headers)
    assert response_me_tret.json()["reputation"] == 20

async def test_idempotency_accept(client, auth_headers, question, dop_auth_headers):
    payload_answer = {"body": "Rest it 5 minutes, internal temp ~135°F.",
                      "question_id": question["id"]}
    response_answer = await client.post(f"/questions/{question['id']}/answers", json=payload_answer, headers=dop_auth_headers)
    assert response_answer.status_code == 201
    answer_id = response_answer.json()["id"]

    response_accept = await client.patch(f"/answers/{answer_id}/accept", headers=auth_headers)
    assert response_accept.status_code == 200
    assert response_accept.json()["is_accepted"] == True

    response_me = await client.get("/auth/me", headers=dop_auth_headers)
    assert response_me.json()["reputation"] == 20

    response_accept = await client.patch(f"/answers/{answer_id}/accept", headers=auth_headers)
    assert response_accept.status_code == 200
