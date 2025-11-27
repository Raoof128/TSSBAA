const graphElement = document.getElementById('graph');
const alertList = document.getElementById('alert-list');
const posturePanel = document.getElementById('posture-panel');

const demoNfs = [
  { id: 'nrf-1', type: 'NRF', status: 'healthy' },
  { id: 'amf-1', type: 'AMF', status: 'healthy' },
  { id: 'smf-1', type: 'SMF', status: 'healthy' },
  { id: 'rogue-smf-1', type: 'SMF', status: 'blocked' },
];

const demoLinks = [
  ['amf-1', 'nrf-1'],
  ['smf-1', 'nrf-1'],
  ['rogue-smf-1', 'nrf-1'],
];

function renderGraph() {
  graphElement.innerHTML = '';
  demoLinks.forEach(([source, target]) => {
    const link = document.createElement('div');
    link.className = 'link';
    link.innerText = `${source} → ${target}`;
    graphElement.appendChild(link);
  });

  demoNfs.forEach((nf) => {
    const card = document.createElement('div');
    card.className = `nf ${nf.status}`;
    card.innerHTML = `<strong>${nf.id}</strong><span>${nf.type}</span>`;
    graphElement.appendChild(card);
  });
}

function renderAlerts() {
  const alerts = [
    { ts: 'now', text: 'Rogue SMF blocked by JWT enforcement' },
    { ts: 'now', text: 'AMF registration validated (mTLS simulated)' },
  ];
  alerts.forEach((alert) => {
    const item = document.createElement('li');
    item.innerText = `[${alert.ts}] ${alert.text}`;
    alertList.appendChild(item);
  });
}

function renderPosture() {
  const posture = [
    ['JWT enforcement', 'enabled'],
    ['mTLS simulation', 'enabled'],
    ['Rate limiting', '60/min'],
    ['Slice isolation', 'per-slice policies configured'],
  ];
  posture.forEach(([k, v]) => {
    const row = document.createElement('div');
    row.className = 'posture-row';
    row.innerHTML = `<span>${k}</span><span class="value">${v}</span>`;
    posturePanel.appendChild(row);
  });
}

renderGraph();
renderAlerts();
renderPosture();
