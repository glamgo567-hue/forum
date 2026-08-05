async def test_create_vote_question(client, auth_headers, question, dop_auth_headers):
    payload_vote = {"value": 1}

    response_vote = await client.post(f"/questions/{question["id"]}/vote", json=payload_vote, headers=dop_auth_headers)
    assert response_vote.status_code == 201

    response_me = await client.get("/auth/me", headers=auth_headers)
    assert response_me.json()["reputation"] == 5

async def test_patch_vote_question(client, auth_headers, question, dop_auth_headers):
    payload_vote1 = {"value": 1}

    response_vote = await client.post(f"/questions/{question["id"]}/vote", json=payload_vote1, headers=dop_auth_headers)
    assert response_vote.status_code == 201

    response_me = await client.get("/auth/me", headers=auth_headers)
    assert response_me.json()["reputation"] == 5

    payload_vote2 = {"value": -1}

    response_vote = await client.patch(f"/questions/{question["id"]}/vote", json=payload_vote2, headers=dop_auth_headers)
    assert response_vote.status_code == 200

    response_me = await client.get("/auth/me", headers=auth_headers)
    assert response_me.json()["reputation"] == -5

async def test_delete_vote_question(client, auth_headers, question, dop_auth_headers):
    payload_vote1 = {"value": 1}

    response_vote = await client.post(f"/questions/{question["id"]}/vote", json=payload_vote1, headers=dop_auth_headers)
    assert response_vote.status_code == 201

    response_me = await client.get("/auth/me", headers=auth_headers)
    assert response_me.json()["reputation"] == 5

    response_vote = await client.delete(f"/questions/{question["id"]}/vote", headers=dop_auth_headers)
    assert response_vote.status_code == 204

    response_me = await client.get("/auth/me", headers=auth_headers)
    assert response_me.json()["reputation"] == 0

async def test_create_vote_answer(client, auth_headers, question, answer, dop_auth_headers):
    payload_vote = {"value": 1}

    response_vote = await client.post(f"/answers/{answer["id"]}/vote", json=payload_vote, headers=dop_auth_headers)
    assert response_vote.status_code == 201

    response_me = await client.get("/auth/me", headers=auth_headers)
    assert response_me.json()["reputation"] == 10

async def test_patch_vote_answer(client, auth_headers, question, answer, dop_auth_headers):
    payload_vote1 = {"value": 1}

    response_vote = await client.post(f"/answers/{answer["id"]}/vote", json=payload_vote1, headers=dop_auth_headers)
    assert response_vote.status_code == 201

    response_me = await client.get("/auth/me", headers=auth_headers)
    assert response_me.json()["reputation"] == 10

    payload_vote2 = {"value": -1}

    response_vote = await client.patch(f"/answers/{answer["id"]}/vote", json=payload_vote2, headers=dop_auth_headers)
    assert response_vote.status_code == 200

    response_me = await client.get("/auth/me", headers=auth_headers)
    assert response_me.json()["reputation"] == -5

async def test_delete_vote_answer(client, auth_headers, question, answer, dop_auth_headers):
    payload_vote1 = {"value": 1}

    response_vote = await client.post(f"/answers/{answer["id"]}/vote", json=payload_vote1, headers=dop_auth_headers)
    assert response_vote.status_code == 201

    response_me = await client.get("/auth/me", headers=auth_headers)
    assert response_me.json()["reputation"] == 10

    response_vote = await client.delete(f"/answers/{answer["id"]}/vote", headers=dop_auth_headers)
    assert response_vote.status_code == 204

    response_me = await client.get("/auth/me", headers=auth_headers)
    assert response_me.json()["reputation"] == 0
