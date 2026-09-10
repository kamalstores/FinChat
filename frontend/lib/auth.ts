export function getToken() {
  if (typeof window === "undefined") return null;

  return localStorage.getItem("access_token");
}

export function setToken(token: string) {
  localStorage.setItem("access_token", token);
}

export function logout() {
  localStorage.removeItem("access_token");
}

export function isAuthenticated() {
  return !!getToken();
}