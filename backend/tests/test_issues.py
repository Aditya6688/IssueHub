import pytest


@pytest.fixture
def project_id(client, auth_headers):
    resp = client.post("/api/projects", json={"name": "P1", "key": "P1"}, headers=auth_headers)
    return resp.json()["id"]


def test_create_issue(client, auth_headers, project_id):
    resp = client.post(f"/api/projects/{project_id}/issues", json={
        "title": "Bug report", "description": "Something is broken", "priority": "high"
    }, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Bug report"
    assert data["status"] == "open"
    assert data["priority"] == "high"


def test_list_issues_with_pagination(client, auth_headers, project_id):
    for i in range(5):
        client.post(f"/api/projects/{project_id}/issues", json={
            "title": f"Issue {i}"
        }, headers=auth_headers)
    resp = client.get(f"/api/projects/{project_id}/issues?page=1&page_size=2", headers=auth_headers)
    data = resp.json()
    assert data["total"] == 5
    assert len(data["items"]) == 2
    assert data["page"] == 1


def test_filter_issues_by_status(client, auth_headers, project_id):
    client.post(f"/api/projects/{project_id}/issues", json={"title": "Open bug"}, headers=auth_headers)
    resp = client.post(f"/api/projects/{project_id}/issues", json={"title": "WIP bug"}, headers=auth_headers)
    issue_id = resp.json()["id"]
    client.patch(f"/api/issues/{issue_id}", json={"status": "in_progress"}, headers=auth_headers)
    resp = client.get(f"/api/projects/{project_id}/issues?status=open", headers=auth_headers)
    assert resp.json()["total"] == 1


def test_search_issues(client, auth_headers, project_id):
    client.post(f"/api/projects/{project_id}/issues", json={"title": "Login error"}, headers=auth_headers)
    client.post(f"/api/projects/{project_id}/issues", json={"title": "Signup crash"}, headers=auth_headers)
    resp = client.get(f"/api/projects/{project_id}/issues?q=Login", headers=auth_headers)
    assert resp.json()["total"] == 1


def test_update_issue(client, auth_headers, project_id):
    resp = client.post(f"/api/projects/{project_id}/issues", json={"title": "Bug"}, headers=auth_headers)
    issue_id = resp.json()["id"]
    resp = client.patch(f"/api/issues/{issue_id}", json={"title": "Updated Bug", "status": "in_progress"}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["title"] == "Updated Bug"
    assert resp.json()["status"] == "in_progress"


def test_delete_issue(client, auth_headers, project_id):
    resp = client.post(f"/api/projects/{project_id}/issues", json={"title": "To delete"}, headers=auth_headers)
    issue_id = resp.json()["id"]
    resp = client.delete(f"/api/issues/{issue_id}", headers=auth_headers)
    assert resp.status_code == 204


def test_non_member_cannot_access_issues(client, auth_headers, second_auth_headers, project_id):
    resp = client.get(f"/api/projects/{project_id}/issues", headers=second_auth_headers)
    assert resp.status_code == 403


def test_member_cannot_change_status(client, auth_headers, second_auth_headers, project_id):
    # Add second user as member
    client.post(f"/api/projects/{project_id}/members", json={
        "email": "second@example.com", "role": "member"
    }, headers=auth_headers)
    # Second user creates an issue
    resp = client.post(f"/api/projects/{project_id}/issues", json={"title": "My bug"}, headers=second_auth_headers)
    issue_id = resp.json()["id"]
    # Second user (member) tries to change status -> should fail
    resp = client.patch(f"/api/issues/{issue_id}", json={"status": "closed"}, headers=second_auth_headers)
    assert resp.status_code == 403
