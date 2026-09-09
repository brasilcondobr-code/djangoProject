(function () {
  'use strict';

  const config = window.connectedUsersConfig;
  const form = document.getElementById('connected-users-filters');
  const tableBody = document.querySelector('#connected-users-table tbody');
  const updated = document.getElementById('connected-users-updated');
  let requestInFlight = false;

  function text(value) {
    return document.createTextNode(value || '-');
  }

  function renderRows(results) {
    tableBody.replaceChildren();
    if (!results.length) {
      const row = document.createElement('tr');
      const cell = document.createElement('td');
      cell.colSpan = 6;
      cell.className = 'text-center';
      cell.appendChild(text('Nenhum usuário conectado.'));
      row.appendChild(cell);
      tableBody.appendChild(row);
      return;
    }
    results.forEach(function (item) {
      const row = document.createElement('tr');
      [item.username, item.email, item.groups.join(', ') || '-', item.is_active ? 'Sim' : 'Não', item.is_staff ? 'Sim' : 'Não', item.last_login || '-'].forEach(function (value) {
        const cell = document.createElement('td');
        cell.appendChild(text(value));
        row.appendChild(cell);
      });
      tableBody.appendChild(row);
    });
  }

  function update() {
    if (requestInFlight || document.hidden) return;
    requestInFlight = true;
    const params = new URLSearchParams(new FormData(form));
    fetch(config.dataUrl + '?' + params.toString(), {headers: {'X-Requested-With': 'XMLHttpRequest'}})
      .then(function (response) {
        if (!response.ok) throw new Error('http_' + response.status);
        return response.json();
      })
      .then(function (payload) {
        if (!Array.isArray(payload.results)) throw new Error('invalid_response');
        renderRows(payload.results);
        updated.textContent = new Date().toLocaleString();
      })
      .catch(function () {
        const status = document.getElementById('connected-users-status');
        status.textContent = 'Não foi possível atualizar os usuários conectados.';
        status.className = 'alert alert-warning';
      })
      .finally(function () { requestInFlight = false; });
  }

  setInterval(update, config.pollInterval);
  document.addEventListener('visibilitychange', update);
}());