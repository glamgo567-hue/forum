const BASE_URL = import.meta.env.VITE_API_URL ?? "/api";

const TOKEN_KEY = "forum_token";

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

export class ApiError extends Error {
  constructor(status, detail) {
    super(detail);
    this.status = status;
    this.detail = detail;
  }
}

async function request(path, { method = "GET", body, form, auth = true } = {}) {
  const headers = {};
  const token = getToken();
  if (auth && token) headers.Authorization = `Bearer ${token}`;

  let payload;
  if (form) {
    payload = new URLSearchParams(form);
  } else if (body !== undefined) {
    headers["Content-Type"] = "application/json";
    payload = JSON.stringify(body);
  }

  const res = await fetch(`${BASE_URL}${path}`, { method, headers, body: payload });

  if (res.status === 204) return null;

  let data = null;
  const text = await res.text();
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = null;
    }
  }

  if (!res.ok) {
    throw new ApiError(res.status, extractDetail(data, res.status));
  }
  return data;
}

function extractDetail(data, status) {
  const detail = data?.detail;
  if (typeof detail === "string") return detail;
  // FastAPI validation errors arrive as a list of objects
  if (Array.isArray(detail) && detail.length > 0) {
    return detail.map((e) => e.msg).join(". ");
  }
  return `Request failed with status ${status}`;
}

export const api = {
  register: (payload) =>
    request("/auth/register", { method: "POST", body: payload, auth: false }),

  login: (username, password) =>
    request("/auth/login", { method: "POST", form: { username, password }, auth: false }),

  me: () => request("/auth/me"),

  listQuestions: ({ skip = 0, limit = 10, tag = null } = {}) => {
    const params = new URLSearchParams({ skip, limit });
    if (tag) params.set("tag", tag);
    return request(`/questions?${params}`);
  },

  getQuestion: (id) => request(`/questions/${id}`),

  createQuestion: (payload) => request("/questions", { method: "POST", body: payload }),

  updateQuestion: (id, payload) =>
    request(`/questions/${id}`, { method: "PATCH", body: payload }),

  deleteQuestion: (id) => request(`/questions/${id}`, { method: "DELETE" }),

  listAnswers: (questionId, { skip = 0, limit = 50 } = {}) =>
    request(`/questions/${questionId}/answers?${new URLSearchParams({ skip, limit })}`),

  createAnswer: (questionId, payload) =>
    request(`/questions/${questionId}/answers`, { method: "POST", body: payload }),

  updateAnswer: (id, payload) => request(`/answers/${id}`, { method: "PATCH", body: payload }),

  deleteAnswer: (id) => request(`/answers/${id}`, { method: "DELETE" }),

  acceptAnswer: (id) => request(`/answers/${id}/accept`, { method: "PATCH" }),

  voteQuestion: (id, method, value) =>
    request(`/questions/${id}/vote`, {
      method,
      body: method === "DELETE" ? undefined : { value },
    }),

  voteAnswer: (id, method, value) =>
    request(`/answers/${id}/vote`, {
      method,
      body: method === "DELETE" ? undefined : { value },
    }),
};
