import apiClient from "./client";

export const authApi = {
  login: (username, password) =>
    apiClient.post("/api/v1/auth/login", { username, password }),

  register: (data) =>
    apiClient.post("/api/v1/auth/register", data),
};
