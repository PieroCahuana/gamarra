protectPage();

const tbody = document.getElementById("puestosTableBody");
const modal = document.getElementById("puestoModal");

let puestosCache = [];

function abrirModal(puesto = null) {
  document.getElementById("puestoForm").reset();
  document.getElementById("puestoId").value = "";
  document.getElementById("modalTitle").textContent = "Nuevo Puesto";
  document.getElementById("estado").value = "disponible";

  if (puesto) {
    document.getElementById("modalTitle").textContent = "Editar Puesto";
    document.getElementById("puestoId").value = puesto.id || "";
    document.getElementById("codigo").value = puesto.codigo || "";
    document.getElementById("galeria").value = puesto.galeria || "";
    document.getElementById("area_m2").value = puesto.area_m2 || "";

    const coords = puesto.ubicacion_geo?.coordinates || [];
    document.getElementById("longitud").value = coords[0] ?? "";
    document.getElementById("latitud").value = coords[1] ?? "";
    document.getElementById("estado").value = puesto.estado || "disponible";
  }

  modal.classList.add("show");
}

function cerrarModal() {
  modal.classList.remove("show");
}

function badgeEstado(estado) {
  if (estado === "disponible") return `<span class="badge-status badge-success">Disponible</span>`;
  if (estado === "ocupado") return `<span class="badge-status badge-warning">Ocupado</span>`;
  return `<span class="badge-status badge-danger">Inactivo</span>`;
}

async function cargarPuestos() {
  try {
    const res = await fetch(`${API_BASE}/puestos`, {
      headers: authHeaders()
    });

    if (!res.ok) throw new Error("No se pudieron cargar los puestos");

    const data = await res.json();
    puestosCache = data;
    tbody.innerHTML = "";

    if (!data.length) {
      tbody.innerHTML = `
        <tr>
          <td colspan="7">
            <div class="empty-box">No hay puestos registrados.</div>
          </td>
        </tr>
      `;
      return;
    }

    data.forEach(p => {
      const tr = document.createElement("tr");
      const coords = p.ubicacion_geo?.coordinates || [];
      tr.innerHTML = `
        <td>${p.id ?? "-"}</td>
        <td>${p.codigo ?? "-"}</td>
        <td>${p.galeria ?? "-"}</td>
        <td>${p.area_m2 ?? "-"}</td>
        <td>${coords.length ? `${coords[0]}, ${coords[1]}` : "-"}</td>
        <td>${badgeEstado(p.estado ?? "inactivo")}</td>
        <td>
          <div class="actions">
            <button class="btn btn-sm btn-edit" onclick="editarPuesto('${p.id}')">Editar</button>
            <button class="btn btn-sm btn-delete" onclick="eliminarPuesto('${p.id}')">Eliminar</button>
          </div>
        </td>
      `;
      tbody.appendChild(tr);
    });
  } catch (error) {
    console.error(error);
    alert("Error cargando puestos.");
  }
}

function editarPuesto(id) {
  const puesto = puestosCache.find(p => p.id === id);
  if (puesto) abrirModal(puesto);
}

async function guardarPuesto() {
  const id = document.getElementById("puestoId").value;

  const payload = {
    codigo: document.getElementById("codigo").value.trim(),
    galeria: document.getElementById("galeria").value.trim(),
    area_m2: parseFloat(document.getElementById("area_m2").value),
    ubicacion_geo: {
      type: "Point",
      coordinates: [
        parseFloat(document.getElementById("longitud").value),
        parseFloat(document.getElementById("latitud").value)
      ]
    }
  };

  try {
    const url = id ? `${API_BASE}/puestos/${id}` : `${API_BASE}/puestos`;
    const method = id ? "PUT" : "POST";

    const res = await fetch(url, {
      method,
      headers: authHeaders(),
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      const err = await res.text();
      console.error(err);
      throw new Error("No se pudo guardar el puesto");
    }

    cerrarModal();
    cargarPuestos();
  } catch (error) {
    console.error(error);
    alert("Error guardando puesto.");
  }
}

async function eliminarPuesto(id) {
  if (!confirm("¿Deseas eliminar este puesto?")) return;

  try {
    const res = await fetch(`${API_BASE}/puestos/${id}`, {
      method: "DELETE",
      headers: authHeaders()
    });

    if (!res.ok) throw new Error("No se pudo eliminar");

    cargarPuestos();
  } catch (error) {
    console.error(error);
    alert("Error eliminando puesto.");
  }
}

cargarPuestos();