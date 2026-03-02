import client from "./client";

export const listIssues = (projectId, params) =>
  client.get(`/api/projects/${projectId}/issues`, { params });

export const getIssue = (issueId) => client.get(`/api/issues/${issueId}`);

export const createIssue = (projectId, data) =>
  client.post(`/api/projects/${projectId}/issues`, data);

export const updateIssue = (issueId, data) =>
  client.patch(`/api/issues/${issueId}`, data);

export const deleteIssue = (issueId) => client.delete(`/api/issues/${issueId}`);
