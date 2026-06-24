requireAuth();
setTopbarInfo("Dashboard", "Resumen general del sistema");

async function cargarDashboard() {
    try {
        const [ambulantesRes, puestosRes, licenciasRes] = await Promise.all([
            fetch(`${API_BASE}/ambulantes/`, { headers: authHeaders() }),
            fetch(`${API_BASE}/puestos/`),
            fetch(`${API_BASE}/licencias/`, { headers: authHeaders() })
        ]);

        const ambulantes = ambulantesRes.ok ? await ambulantesRes.json() : [];
        const puestos = puestosRes.ok ? await puestosRes.json() : [];
        const licencias = licenciasRes.ok ? await licenciasRes.json() : [];

        const pendientes = licencias.filter(l => normalizeText(l.estado) === "pendiente").length;
        const aprobadas = licencias.filter(l => normalizeText(l.estado) === "aprobada").length;
        const rechazadas = licencias.filter(l => normalizeText(l.estado) === "rechazada").length;

        document.getElementById("totalAmbulantes").textContent = ambulantes.length;
        document.getElementById("totalPuestos").textContent = puestos.length;
        document.getElementById("totalLicencias").textContent = licencias.length;
        document.getElementById("totalPendientes").textContent = pendientes;

        document.getElementById("totalAprobadas").textContent = aprobadas;
        document.getElementById("totalRechazadas").textContent = rechazadas;
        document.getElementById("totalPendientesResumen").textContent = pendientes;
        document.getElementById("dashboardRole").textContent = getRole() || "sin rol";
    } catch (error) {
        console.error("Error cargando dashboard:", error);
    }
}

cargarDashboard();