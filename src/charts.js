const NS = 'http://www.w3.org/2000/svg';
const css = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
const make = (tag, attributes = {}) => {
  const element = document.createElementNS(NS, tag);
  Object.entries(attributes).forEach(([key, value]) => element.setAttribute(key, value));
  return element;
};
const points = (values, width, height, max, pad) => values.map((value, index) => ({
  x: pad.left + index * ((width - pad.left - pad.right) / Math.max(1, values.length - 1)),
  y: pad.top + (height - pad.top - pad.bottom) * (1 - Number(value || 0) / Math.max(1, max))
}));
const pathFor = (items) => items.map((point, index) => `${index ? 'L' : 'M'}${point.x.toFixed(1)},${point.y.toFixed(1)}`).join(' ');

export function drawEnergyChart(container, rows, inputHours, visibility = {}, onHover = () => {}) {
  if (!rows?.length || !inputHours?.length) return;
  container.innerHTML = '';
  const width = Math.max(680, container.clientWidth - 20), height = 275;
  const pad = { top: 15, right: 20, bottom: 30, left: 39 };
  const svg = make('svg', { viewBox: `0 0 ${width} ${height}`, role: 'img', 'aria-label': '24-hour demand, solar and grid energy chart', preserveAspectRatio: 'none' });
  const series = [
    { id: 'demand', values: inputHours.map(h => h.demand_kwh), color: css('--violet') },
    { id: 'solar', values: rows.map(h => h.solar_used_kwh), color: css('--amber') },
    { id: 'grid', values: rows.map(h => h.grid_kwh), color: css('--cyan') }
  ];
  const max = Math.max(...series.flatMap(s => s.values), 1) * 1.12;
  for (let i = 0; i <= 4; i += 1) {
    const y = pad.top + i * ((height - pad.top - pad.bottom) / 4);
    svg.append(make('line', { x1: pad.left, y1: y, x2: width - pad.right, y2: y, class: 'chart-grid' }));
    const label = make('text', { x: 2, y: y + 3, class: 'chart-axis' }); label.textContent = Math.round(max * (1 - i / 4)); svg.append(label);
  }
  [0, 4, 8, 12, 16, 20, 23].forEach(hour => { const x = pad.left + hour * ((width - pad.left - pad.right) / 23); const label = make('text', { x, y: height - 5, class: 'chart-axis', 'text-anchor': hour === 0 ? 'start' : hour === 23 ? 'end' : 'middle' }); label.textContent = `${String(hour).padStart(2,'0')}:00`; svg.append(label); });
  const defs = make('defs');
  series.forEach((item) => { const gradient = make('linearGradient', { id: `area-${item.id}`, x1: 0, y1: 0, x2: 0, y2: 1 }); gradient.append(make('stop', { offset: 0, 'stop-color': item.color, 'stop-opacity': .32 })); gradient.append(make('stop', { offset: 1, 'stop-color': item.color, 'stop-opacity': 0 })); defs.append(gradient); }); svg.append(defs);
  series.forEach((item) => {
    if (visibility[item.id] === false) return;
    const itemPoints = points(item.values, width, height, max, pad);
    const areaPath = `${pathFor(itemPoints)} L${itemPoints.at(-1).x},${height - pad.bottom} L${itemPoints[0].x},${height - pad.bottom} Z`;
    svg.append(make('path', { d: areaPath, fill: `url(#area-${item.id})`, class: 'chart-area' }));
    const path = make('path', { d: pathFor(itemPoints), stroke: item.color, class: 'chart-line', 'vector-effect': 'non-scaling-stroke' });
    path.style.strokeDasharray = '1000'; path.style.strokeDashoffset = '1000'; path.style.animation = 'drawLine .8s var(--ease) forwards'; svg.append(path);
  });
  const cursor = make('line', { y1: pad.top, y2: height - pad.bottom, class: 'chart-cursor', visibility: 'hidden' }); svg.append(cursor);
  rows.forEach((row, hour) => {
    const x = pad.left + hour * ((width - pad.left - pad.right) / 23);
    const hit = make('rect', { x: x - ((width - pad.left - pad.right) / 46), y: pad.top, width: (width - pad.left - pad.right) / 23, height: height - pad.top - pad.bottom, class: 'chart-hit', tabindex: 0, 'aria-label': `Hour ${hour}` });
    const emit = (event) => { cursor.setAttribute('x1', x); cursor.setAttribute('x2', x); cursor.setAttribute('visibility', 'visible'); onHover(hour, event); };
    hit.addEventListener('pointerenter', emit); hit.addEventListener('pointermove', emit); hit.addEventListener('focus', emit); hit.addEventListener('pointerleave', () => { cursor.setAttribute('visibility', 'hidden'); onHover(null); }); svg.append(hit);
  });
  container.append(svg);
}

export function drawSocChart(container, rows, capacity, reserve) {
  container.innerHTML = '';
  if (!rows?.length) { container.innerHTML = '<div class="empty-inline"><p>Battery trajectory will appear after optimization.</p></div>'; return; }
  const width = Math.max(720, container.clientWidth - 20), height = 180, pad = { top: 15, right: 20, bottom: 25, left: 39 };
  const svg = make('svg', { viewBox: `0 0 ${width} ${height}`, role: 'img', 'aria-label': 'Battery state of charge over 24 hours', preserveAspectRatio: 'none' });
  [0, .25, .5, .75, 1].forEach((fraction) => { const y = pad.top + (1 - fraction) * (height - pad.top - pad.bottom); svg.append(make('line', { x1: pad.left, y1: y, x2: width - pad.right, y2: y, class: 'chart-grid' })); const t = make('text', { x: 2, y: y + 3, class: 'chart-axis' }); t.textContent = `${Math.round(fraction * 100)}%`; svg.append(t); });
  const reserveY = pad.top + (1 - reserve / capacity) * (height - pad.top - pad.bottom); svg.append(make('line', { x1: pad.left, y1: reserveY, x2: width - pad.right, y2: reserveY, stroke: css('--amber'), 'stroke-dasharray': '4 5', opacity: .7 }));
  const itemPoints = points(rows.map(r => r.battery_energy_after_kwh), width, height, capacity, pad);
  const areaPath = `${pathFor(itemPoints)} L${itemPoints.at(-1).x},${height-pad.bottom} L${itemPoints[0].x},${height-pad.bottom} Z`;
  const defs = make('defs'), gradient = make('linearGradient', { id: 'soc-area', x1: 0, y1: 0, x2: 0, y2: 1 }); gradient.append(make('stop', { offset: 0, 'stop-color': css('--green'), 'stop-opacity': .28 })); gradient.append(make('stop', { offset: 1, 'stop-color': css('--green'), 'stop-opacity': 0 })); defs.append(gradient); svg.append(defs);
  svg.append(make('path', { d: areaPath, fill: 'url(#soc-area)' })); svg.append(make('path', { d: pathFor(itemPoints), stroke: css('--green'), class: 'chart-line', 'vector-effect': 'non-scaling-stroke' }));
  [0, 4, 8, 12, 16, 20, 23].forEach(hour => { const x = itemPoints[hour].x; const label = make('text', { x, y: height - 3, class: 'chart-axis', 'text-anchor': hour === 0 ? 'start' : hour === 23 ? 'end' : 'middle' }); label.textContent = `${String(hour).padStart(2,'0')}:00`; svg.append(label); });
  container.append(svg);
}

export function drawInputProfile(container, hours) {
  if (!hours?.length) return;
  container.innerHTML = '';
  const width = Math.max(600, container.clientWidth), height = 140, pad = { top: 8, right: 8, bottom: 12, left: 8 };
  const svg = make('svg', { viewBox: `0 0 ${width} ${height}`, preserveAspectRatio: 'none', role: 'img', 'aria-label': 'Scenario demand and solar preview' });
  const max = Math.max(...hours.flatMap(h => [h.demand_kwh, h.solar_kwh]), 1) * 1.1;
  const demand = points(hours.map(h => h.demand_kwh), width, height, max, pad), solar = points(hours.map(h => h.solar_kwh), width, height, max, pad);
  svg.append(make('path', { d: `${pathFor(demand)} L${demand.at(-1).x},${height-pad.bottom} L${demand[0].x},${height-pad.bottom} Z`, fill: css('--violet'), opacity: .1 }));
  svg.append(make('path', { d: pathFor(demand), stroke: css('--violet'), class: 'chart-line', 'vector-effect': 'non-scaling-stroke' })); svg.append(make('path', { d: pathFor(solar), stroke: css('--amber'), class: 'chart-line', 'vector-effect': 'non-scaling-stroke' })); container.append(svg);
}

export function drawSparkline(container, values, color = '--cyan') {
  container.innerHTML = '';
  if (!values?.length) return;
  const width = 200, height = 35, max = Math.max(...values, 1), min = Math.min(...values, 0), span = Math.max(1, max-min);
  const list = values.map((value, index) => ({ x: index * (width / (values.length - 1)), y: height - ((value-min)/span) * 28 }));
  const svg = make('svg', { viewBox: `0 0 ${width} ${height}`, preserveAspectRatio: 'none' }); svg.append(make('path', { d: `${pathFor(list)} L${width},${height} L0,${height} Z`, fill: css(color), opacity: .15 })); svg.append(make('path', { d: pathFor(list), stroke: css(color), fill: 'none', 'stroke-width': 1.5 })); container.append(svg);
}
