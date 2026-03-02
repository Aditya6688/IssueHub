import client from "./client";

export const listProjects = () => client.get("/api/projects");
export const getProject = (id) => client.get(`/api/projects/${id}`);
export const createProject = (data) => client.post("/api/projects", data);
export const addMember = (projectId, data) =>
  client.post(`/api/projects/${projectId}/members`, data);
