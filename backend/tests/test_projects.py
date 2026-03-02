def test_create_project(client, auth_headers):
    resp = client.post("/api/projects", json={
        "name": "My Project", "key": "MP", "description": "A test project"
    }, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "My Project"
    assert data["key"] == "MP"


def test_list_projects_only_member(client, auth_headers, second_auth_headers):
    client.post("/api/projects", json={"name": "P1", "key": "P1"}, headers=auth_headers)
    client.post("/api/projects", json={"name": "P2", "key": "P2"}, headers=second_auth_headers)
    resp = client.get("/api/projects", headers=auth_headers)
    assert resp.status_code == 200
    projects = resp.json()
    assert len(projects) == 1
    assert projects[0]["key"] == "P1"


def test_get_project_detail(client, auth_headers):
    resp = client.post("/api/projects", json={"name": "P1", "key": "P1"}, headers=auth_headers)
    pid = resp.json()["id"]
    resp = client.get(f"/api/projects/{pid}", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["members"]) == 1
    assert data["members"][0]["role"] == "maintainer"


def test_add_member(client, auth_headers, second_auth_headers):
    resp = client.post("/api/projects", json={"name": "P1", "key": "P1"}, headers=auth_headers)
    pid = resp.json()["id"]
    resp = client.post(f"/api/projects/{pid}/members", json={
        "email": "second@example.com", "role": "member"
    }, headers=auth_headers)
    assert resp.status_code == 201
    assert resp.json()["role"] == "member"


def test_non_maintainer_cannot_add_member(client, auth_headers, second_auth_headers):
    resp = client.post("/api/projects", json={"name": "P1", "key": "P1"}, headers=auth_headers)
    pid = resp.json()["id"]
    # Add second as member
    client.post(f"/api/projects/{pid}/members", json={
        "email": "second@example.com", "role": "member"
    }, headers=auth_headers)
    # Second tries to add someone -> should fail
    client.post("/api/auth/signup", json={"name": "Third", "email": "third@example.com", "password": "secret123"})
    resp = client.post(f"/api/projects/{pid}/members", json={
        "email": "third@example.com", "role": "member"
    }, headers=second_auth_headers)
    assert resp.status_code == 403
