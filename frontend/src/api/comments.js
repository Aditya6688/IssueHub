import client from "./client";

export const listComments = (issueId) =>
  client.get(`/api/issues/${issueId}/comments`);

export const createComment = (issueId, data) =>
  client.post(`/api/issues/${issueId}/comments`, data);
