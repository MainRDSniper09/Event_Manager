document.addEventListener("DOMContentLoaded", () => {
    cargarEventos();
});

// 🔥 Función para obtener eventos desde la API
async function cargarEventos() {
    try {
        const response = await fetch("http://127.0.0.1:8000/eventos");
        if (!response.ok) throw new Error("Error al cargar eventos");

        const eventos = await response.json();
        mostrarEventos(eventos);
    } catch (error) {
        console.error("Error:", error);
    }
}

// 🔥 Función para mostrar eventos en la página
function mostrarEventos(eventos) {
    const eventosContainer = document.getElementById("eventos-container");
    eventosContainer.innerHTML = ""; // Limpiar contenido

    eventos.forEach(evento => {
        const eventoCard = document.createElement("div");
        eventoCard.classList.add("evento-card");

        eventoCard.innerHTML = `
            <h2>${evento.nombre}</h2>
            <p><strong>Descripción:</strong> ${evento.descripcion}</p>
            <p><strong>Fecha:</strong> ${evento.fecha}</p>
            <p><strong>Lugar:</strong> ${evento.lugar}</p>
            <p><strong>Organizador:</strong> ${evento.organizador.nombre}</p>
        `;

        eventosContainer.appendChild(eventoCard);
    });
}
