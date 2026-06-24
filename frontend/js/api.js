const API_BASE = "http://127.0.0.1:8000/api/v1";

function getToken() {
  return localStorage.getItem("gamarra_token");
}

function authHeaders() {
  return {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${getToken()}`
  };
}

function logout() {
  localStorage.removeItem("gamarra_token");
  window.location.href = "index.html";
}

function protectPage() {
  const token = getToken();
  if (!token) {
    window.location.replace("index.html");
  }
}