protectPage();

const tbodyAmb = document.getElementById("ambulantesTableBody");
const modalAmb = document.getElementById("ambulanteModal");

let ambulantesCache = [];

function abrirModal(ambulante = null) {
  document.getElementById("ambulanteForm").reset();
  document.getElementById("ambulanteId").value = "";
  document.getElementById("modalTitle").textContent = "Nuevo Ambulante";

  if (ambulante) {
    document.getElementById("modalTitle").textContent = "Editar Ambulante";
    document.getElementById("ambulanteId").value = ambulante.id || "";
    document.getElementById("nombre_completo").value = ambulante.nombre_completo || "";
    document.getElementById("dni").value = ambulante.dni || "";
    document.getElementById("telefono").value = ambulante.telefono || "";
    document.getElementById("direccion").value = ambulante.direccion || "";
  }

  modalAmb.classList.add("show");
}

function cerrarModal() {
  modalAmb.classList.remove("show");
}

function badgeEstado(estado) {
  if (estado === "activo") return `<span class="badge-status badge-success">Activo</span>`;
  return `<span class="badge-status badge-danger">${estado || "Sin estado"}</span>`;
}

async function cargarAmbulantes() {
  try {
    const res = await fetch(`${API_BASE}/ambulantes`, {
      headers: authHeaders()
    });

    if (!res.ok) throw new Error("No se pudieron cargar ambulantes");

    const data = await res.json();
    ambulantesCache = data;
    tbodyAmb.innerHTML = "";

    if (!data.length) {
      tbodyAmb.innerHTML = `
        <tr>
          <td colspan="7">
            <div class="empty-box">No hay ambulantes registrados.</div>
          </td>
        </tr>
      `;
      return;
    }

    data.forEach(a => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${a.id ?? "-"}</td>
        <td>${a.nombre_completo ?? "-"}</td>
        <td>${a.dni ?? "-"}</td>
        <td>${a.telefono ?? "-"}</td>
        <td>${a.direccion ?? "-"}</td>
        <td>${badgeEstado(a.estado)}</td>
        <td>
          <div class="actions">
            <button class="btn btn-sm btn-edit" onclick="editarAmbulante('${a.id}')">Editar</button>
            <button class="btn btn-sm btn-delete" onclick="eliminarAmbulante('${a.id}')">Eliminar</button>
          </div>
        </td>
      `;
      tbodyAmb.appendChild(tr);
    });
  } catch (error) {
    console.error(error);
    alert("Error cargando ambulantes.");
  }
}

function editarAmbulante(id) {
  const ambulante = ambulantesCache.find(a => a.id === id);
  if (ambulante) abrirModal(ambulante);
}

async function guardarAmbulante() {
  const id = document.getElementById("ambulanteId").value;

  const payload = {
    nombre_completo: document.getElementById("nombre_completo").value.trim(),
    dni: document.getElementById("dni").value.trim(),
    telefono: document.getElementById("telefono").value.trim(),
    direccion: document.getElementById("direccion").value.trim()
  };

  try {
    const url = id ? `${API_BASE}/ambulantes/${id}` : `${API_BASE}/ambulantes`;
    const method = id ? "PUT" : "POST";

    const res = await fetch(url, {
      method,
      headers: authHeaders(),
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      const err = await res.text();
      console.error(err);
      throw new Error("No se pudo guardar el ambulante");
    }

    cerrarModal();
    cargarAmbulantes();
  } catch (error) {
    console.error(error);
    alert("Error guardando ambulante.");
  }
}

async function eliminarAmbulante(id) {
  if (!confirm("¿Deseas eliminar este ambulante?")) return;

  try {
    const res = await fetch(`${API_BASE}/ambulantes/${id}`, {
      method: "DELETE",
      headers: authHeaders()
    });

    if (!res.ok) throw new Error("No se pudo eliminar");

    cargarAmbulantes();
  } catch (error) {
    console.error(error);
    alert("Error eliminando ambulante.");
  }
}

cargarAmbulantes();