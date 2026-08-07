// Historial de búsquedas — funcionalidad agregada durante la reingeniería.
// Consulta /api/history y la pinta en la pantalla principal, refrescándola
// cada vez que el usuario hace una búsqueda nueva.

async function loadSearchHistory() {
    const list = document.getElementById('searchHistoryList');
    if (!list) return;

    try {
        const response = await fetch('/api/history?limit=8');
        const history = await response.json();

        if (!history.length) {
            list.innerHTML = '<li class="empty">No searches yet — try one above.</li>';
            return;
        }

        list.innerHTML = history.map(item => {
            const label = item.type === 'title' ? 'Title' : 'Genre';
            const when = new Date(item.searched_at + 'Z').toLocaleString();
            return `<li>
                <span class="history-type">${label}</span>
                <span class="history-query">"${item.query}"</span>
                <span class="history-count">${item.results_count} results</span>
                <span class="history-time">${when}</span>
            </li>`;
        }).join('');
    } catch (err) {
        console.error('No se pudo cargar el historial de busquedas', err);
    }
}

document.addEventListener('DOMContentLoaded', loadSearchHistory);

// El formulario principal (definido en main.js) dispara la busqueda real.
// Aqui solo escuchamos ese mismo submit para refrescar el historial poco
// despues de que la busqueda se haya registrado en el servidor.
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('recommendationForm');
    if (form) {
        form.addEventListener('submit', () => {
            setTimeout(loadSearchHistory, 1200);
        });
    }
});
