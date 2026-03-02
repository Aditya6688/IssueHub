import pytest


@pytest.fixture
def issue_id(client, auth_headers):
    resp = client.post("/api/projects", json={"name": "P1", "key": "P1"}, headers=auth_headers)
    pid = resp.json()["id"]
    resp = client.post(f"/api/projects/{pid}/issues", json={"title": "Bug"}, headers=auth_headers)
    return resp.json()["id"]


def test_create_comment(client, auth_headers, issue_id):
    resp = client.post(f"/api/issues/{issue_id}/comments", json={"body": "I can reproduce this."}, headers=auth_headers)
    assert resp.status_code == 201
    assert resp.json()["body"] == "I can reproduce this."


def test_list_comments(client, auth_headers, issue_id):
    client.post(f"/api/issues/{issue_id}/comments", json={"body": "Comment 1"}, headers=auth_headers)
    client.post(f"/api/issues/{issue_id}/comments", json={"body": "Comment 2"}, headers=auth_headers)
    resp = client.get(f"/api/issues/{issue_id}/comments", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_comment_requires_auth(client, issue_id):
    resp = client.post(f"/api/issues/{issue_id}/comments", json={"body": "Anon comment"})
    assert resp.status_code == 401
