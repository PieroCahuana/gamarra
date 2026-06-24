protectPage();

const tbodyLic = document.getElementById("licenciasTableBody");
const modalLic = document.getElementById("licenciaModal");

let licenciasCache = [];

function abrirModal(licencia = null) {
  document.getElementById("licenciaForm").reset();
  document.getElementById("licenciaId").value = "";
  document.getElementById("modalTitle").textContent = "Nueva Licencia";

  if (licencia) {
    document.getElementById("modalTitle").textContent = "Editar Licencia";
    document.getElementById("licenciaId").value = licencia.id || "";
    document.getElementById("ambulante_id").value = licencia.ambulante_id || "";
    document.getElementById("tipo").value = licencia.tipo || "temporal";
    document.getElementById("fecha_inicio").value = licencia.fecha_inicio || "";
    document.getElementById("fecha_vencimiento").value = licencia.fecha_vencimiento || "";
    document.getElementById("documentos_urls").value = (licencia.documentos_urls || []).join(", ");
  }

  modalLic.classList.add("show");
}

function cerrarModal() {
  modalLic.classList.remove("show");
}

function badgeEstado(estado) {
  if (estado === "aprobada") return `<span class="badge-status badge-success">Aprobada</span>`;
  if (estado === "en_revision") return `<span class="badge-status badge-warning">En revisión</span>`;
  if (estado === "rechazada") return `<span class="badge-status badge-danger">Rechazada</span>`;
  return `<span class="badge-status badge-warning">Pendiente</span>`;
}

async function cargarLicencias() {
  try {
    const res = await fetch(`${API_BASE}/licencias`, {
      headers: authHeaders()
    });

    if (!res.ok) throw new Error("No se pudieron cargar licencias");

    const data = await res.json();
    licenciasCache = data;
    tbodyLic.innerHTML = "";

    if (!data.length) {
      tbodyLic.innerHTML = `
        <tr>
          <td colspan="8">
            <div class="empty-box">No hay licencias registradas.</div>
          </td>
        </tr>
      `;
      return;
    }

    data.forEach(l => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${l.id ?? "-"}</td>
        <td>${l.ambulante_id ?? "-"}</td>
        <td>${l.tipo ?? "-"}</td>
        <td>${l.fecha_inicio ?? "-"}</td>
        <td>${l.fecha_vencimiento ?? "-"}</td>
        <td>${badgeEstado(l.estado)}</td>
        <td>${l.puesto_id ?? "-"}</td>
        <td>
          <div class="actions">
            <button class="btn btn-sm btn-edit" onclick="editarLicencia('${l.id}')">Editar</button>
            <button class="btn btn-sm btn-delete" onclick="eliminarLicencia('${l.id}')">Eliminar</button>
          </div>
        </td>
      `;
      tbodyLic.appendChild(tr);
    });
  } catch (error) {
    console.error(error);
    alert("Error cargando licencias.");
  }
}

function editarLicencia(id) {
  const licencia = licenciasCache.find(l => l.id === id);
  if (licencia) abrirModal(licencia);
}

async function guardarLicencia() {
  const id = document.getElementById("licenciaId").value;

  const documentosInput = document.getElementById("documentos_urls").value.trim();
  const documentos_urls = documentosInput
    ? documentosInput.split(",").map(x => x.trim()).filter(Boolean)
    : [];

  const payload = {
    ambulante_id: document.getElementById("ambulante_id").value.trim(),
    tipo: document.getElementById("tipo").value,
    fecha_inicio: document.getElementById("fecha_inicio").value,
    fecha_vencimiento: document.getElementById("fecha_vencimiento").value,
    documentos_urls
  };

  try {
    const url = id ? `${API_BASE}/licencias/${id}` : `${API_BASE}/licencias`;
    const method = id ? "PUT" : "POST";

    const res = await fetch(url, {
      method,
      headers: authHeaders(),
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      const err = await res.text();
      console.error(err);
      throw new Error("No se pudo guardar la licencia");
    }

    cerrarModal();
    cargarLicencias();
  } catch (error) {
    console.error(error);
    alert("Error guardando licencia.");
  }
}

async function eliminarLicencia(id) {
  if (!confirm("¿Deseas eliminar esta licencia?")) return;

  try {
    const res = await fetch(`${API_BASE}/licencias/${id}`, {
      method: "DELETE",
      headers: authHeaders()
    });

    if (!res.ok) throw new Error("No se pudo eliminar");

    cargarLicencias();
  } catch (error) {
    console.error(error);
    alert("Error eliminando licencia.");
  }
}

cargarLicencias();