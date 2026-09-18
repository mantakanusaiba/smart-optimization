const paths = {
  grid: '<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>',
  sliders: '<path d="M4 6h6M14 6h6M4 18h10M18 18h2M4 12h2M10 12h10"/><circle cx="12" cy="6" r="2"/><circle cx="8" cy="12" r="2"/><circle cx="16" cy="18" r="2"/>',
  brain: '<path d="M9.5 4.5A3 3 0 0 0 5 7a3 3 0 0 0 0 6 3 3 0 0 0 4.5 2.5V4.5ZM14.5 4.5A3 3 0 0 1 19 7a3 3 0 0 1 0 6 3 3 0 0 1-4.5 2.5V4.5Z"/><path d="M5.5 10H9M15 10h3.5M8 15v3M16 15v3"/>',
  calendar: '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M16 3v4M8 3v4M3 10h18M8 14h.01M12 14h.01M16 14h.01M8 18h.01M12 18h.01"/>',
  code: '<path d="m8 9-3 3 3 3M16 9l3 3-3 3M14 5l-4 14"/>',
  shield: '<path d="M12 3 4.5 6v5.5c0 4.7 3.1 7.9 7.5 9.5 4.4-1.6 7.5-4.8 7.5-9.5V6L12 3Z"/><path d="m8.5 12 2.2 2.2 4.8-5"/>',
  menu: '<path d="M4 7h16M4 12h16M4 17h16"/>',
  moon: '<path d="M20 15.2A8.2 8.2 0 0 1 8.8 4a8.2 8.2 0 1 0 11.2 11.2Z"/>',
  sun: '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.42 1.42M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.42-1.42M17.66 6.34l1.41-1.41"/>',
  spark: '<path d="m12 3-1.4 4.1L6.5 8.5l4.1 1.4L12 14l1.4-4.1 4.1-1.4-4.1-1.4L12 3Z"/><path d="m5 14-.9 2.6-2.6.9 2.6.9L5 21l.9-2.6 2.6-.9-2.6-.9L5 14ZM19 14l-.7 2.1-2.1.7 2.1.7L19 20l.7-2.1 2.1-.7-2.1-.7L19 14Z"/>',
  edit: '<path d="M12 20h9M16.5 3.5a2.1 2.1 0 0 1 3 3L8 18l-4 1 1-4L16.5 3.5Z"/>',
  info: '<circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8h.01"/>',
  wallet: '<path d="M4 6.5h14a2 2 0 0 1 2 2V18a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V6.5A2.5 2.5 0 0 1 4.5 4H17v2.5"/><path d="M15 12h5v4h-5a2 2 0 0 1 0-4Z"/>',
  gauge: '<path d="M5 19a9 9 0 1 1 14 0"/><path d="m12 13 4-4M7.5 16.5h.01M16.5 16.5h.01M12 7h.01"/>',
  battery: '<rect x="3" y="6" width="17" height="12" rx="2"/><path d="M20 10h2v4h-2M7 10v4M11 10v4M15 10v4"/>',
  chart: '<path d="M4 19V5M4 19h17"/><path d="m7 15 4-5 3 3 6-7"/>',
  download: '<path d="M12 3v12M7 10l5 5 5-5M5 21h14"/>',
  plus: '<path d="M12 5v14M5 12h14"/>',
  lock: '<rect x="4" y="10" width="16" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/>',
  copy: '<rect x="8" y="8" width="12" height="12" rx="2"/><path d="M16 8V6a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h2"/>',
  refresh: '<path d="M20 6v5h-5M4 18v-5h5"/><path d="M6.1 9a7 7 0 0 1 11.5-2.5L20 11M4 13l2.4 4.5A7 7 0 0 0 18 15"/>',
  check: '<path d="m5 12 4 4L19 6"/>',
  alert: '<path d="M10.3 3.6 2.4 18a2 2 0 0 0 1.8 3h15.6a2 2 0 0 0 1.8-3L13.7 3.6a2 2 0 0 0-3.4 0Z"/><path d="M12 9v4M12 17h.01"/>',
  notes: '<path d="M5 3h14a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H9l-5 3v-4.5A2 2 0 0 1 3 15V5a2 2 0 0 1 2-2Z"/><path d="M8 8h8M8 12h5"/>',
  filter: '<path d="M4 5h16l-6 7v6l-4 2v-8L4 5Z"/>',
  optimize: '<circle cx="12" cy="12" r="8"/><path d="m12 12 4-3M12 7v1M7 12h1M16 16l.5.5"/>',
  validate: '<path d="M4 12.5 9 17l11-11"/>',
  ready: '<path d="M12 2v4M12 18v4M4.9 4.9l2.8 2.8M16.3 16.3l2.8 2.8M2 12h4M18 12h4M4.9 19.1l2.8-2.8M16.3 7.7l2.8-2.8"/><circle cx="12" cy="12" r="3"/>',
  server: '<rect x="3" y="4" width="18" height="6" rx="2"/><rect x="3" y="14" width="18" height="6" rx="2"/><path d="M7 7h.01M7 17h.01"/>'
};

export const icon = (name) => `<svg viewBox="0 0 24 24" aria-hidden="true">${paths[name] || paths.grid}</svg>`;

export function hydrateIcons(root = document) {
  root.querySelectorAll('[data-icon]').forEach((element) => {
    element.innerHTML = icon(element.dataset.icon);
  });
}

export function formatNumber(value, digits = 0) {
  if (value == null || !Number.isFinite(Number(value))) return '—';
  return new Intl.NumberFormat('en-US', { maximumFractionDigits: digits }).format(Number(value));
}

export function escapeHtml(value = '') {
  return String(value).replace(/[&<>'"]/g, (character) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
  })[character]);
}

export function syntaxHighlight(value) {
  const json = escapeHtml(JSON.stringify(value ?? null, null, 2));
  return json.replace(/(&quot;.*?&quot;)(\s*:)?|\b(true|false)\b|\b(null)\b|-?\d+(?:\.\d+)?/g, (match, string, colon, bool, nil) => {
    if (string) return `<span class="json-${colon ? 'key' : 'string'}">${string}</span>${colon || ''}`;
    if (bool) return `<span class="json-boolean">${bool}</span>`;
    if (nil) return `<span class="json-null">${nil}</span>`;
    return `<span class="json-number">${match}</span>`;
  });
}

export function toast(message, detail = '', type = 'info') {
  const stack = document.getElementById('toastStack');
  const node = document.createElement('div');
  node.className = `toast ${type}`;
  node.innerHTML = `<span>${icon(type === 'error' ? 'alert' : type === 'success' ? 'check' : 'info')}</span><p>${escapeHtml(message)}${detail ? `<small>${escapeHtml(detail)}</small>` : ''}</p>`;
  stack.append(node);
  window.setTimeout(() => node.remove(), 4300);
}

export function animateNumber(element, target, formatter = (value) => formatNumber(value, 0)) {
  if (!Number.isFinite(Number(target))) { element.textContent = '—'; return; }
  const start = Number(element.dataset.value || 0);
  const finish = Number(target);
  const startTime = performance.now();
  const duration = 620;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const update = (time) => {
    const progress = reduced ? 1 : Math.min(1, (time - startTime) / duration);
    const eased = 1 - Math.pow(1 - progress, 3);
    element.textContent = formatter(start + (finish - start) * eased);
    if (progress < 1) requestAnimationFrame(update);
    else element.dataset.value = String(finish);
  };
  requestAnimationFrame(update);
}
