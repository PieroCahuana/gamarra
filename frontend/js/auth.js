const loginForm = document.getElementById("loginForm");

if (loginForm) {
  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();
    const errorMsg = document.getElementById("error-message");
    const loadingText = document.getElementById("loadingText");

    errorMsg.style.display = "none";
    loadingText.style.display = "block";

    try {
      const response = await fetch("http://127.0.0.1:8000/api/v1/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ email, password })
      });

      if (!response.ok) {
        errorMsg.style.display = "block";
        loadingText.style.display = "none";
        return;
      }

      const data = await response.json();
      localStorage.setItem("gamarra_token", data.access_token);

      // IMPORTANTE: redirección segura
      window.location.replace("dashboard.html");
    } catch (error) {
      console.error("Error en login:", error);
      alert("No se pudo conectar con la API.");
    } finally {
      loadingText.style.display = "none";
    }
  });
}