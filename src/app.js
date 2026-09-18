import { hydrateIcons, icon, formatNumber, escapeHtml, toast, animateNumber } from './ui.js';
import { drawEnergyChart, drawInputProfile } from './charts.js';

const state = { scenario: null, response: null, selectedHour: 12, view: 'command', messages: [], busy: false };
const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
const hourLabel = (hour) => `${String(hour).padStart(2, '0')}:00`;

const defaultScenario = () => ({
  scenario_id: 'CAMPUS-TODAY', operator_notes: [],
  hours: Array.from({ length: 24 }, (_, hour) => ({
    hour,
    demand_kwh: Math.max(70, Math.round(105 + 45 * Math.sin((hour - 7) / 24 * Math.PI * 2) + (hour >= 18 && hour <= 21 ? 55 : 0))),
    solar_kwh: hour >= 6 && hour <= 18 ? Math.max(0, Math.round(160 * Math.sin((hour - 6) / 12 * Math.PI))) : 0,
    tariff_bdt_per_kwh: hour < 6 ? 6 : hour < 16 ? 13 : hour < 21 ? 26 : 10
  })),
  battery: { capacity_kwh: 240, initial_energy_kwh: 120, minimum_energy_kwh: 40, max_charge_kwh_per_hour: 55, max_discharge_kwh_per_hour: 55 }
});

const directiveNames = {
  solar_reduction: 'Reduced solar availability', minimum_battery_reserve: 'Battery reserve protected',
  no_charge_window: 'Charging paused', no_discharge_window: 'Discharging paused',
  max_grid_window: 'Grid import limited', no_op: 'No schedule impact'
};

function assistantWelcome() {
  return { role: 'assistant', html: '<p><strong>Hi, I’m your GridWise energy assistant.</strong></p><p>Tell me what changed today or describe an operating constraint. I’ll understand the instruction and build the lowest-cost safe plan for the next 24 hours.</p>' };
}

function now() { return new Intl.DateTimeFormat('en', { hour: '2-digit', minute: '2-digit' }).format(new Date()); }
function inputHour(hour) { return state.scenario.hours.find(row => row.hour === hour); }
function planHour(hour) { return state.response?.hourly_plan?.find(row => row.hour === hour); }
function directivesAt(hour) { return state.response?.directive_interpretation?.filter(item => item.applies && item.structured_adjustment?.hours?.includes(hour)) || []; }

function navigate(view) {
  if (!['command', 'schedule', 'settings'].includes(view) || view === state.view) return;
  $(`.view[data-page="${state.view}"]`)?.classList.remove('active');
  $(`.view[data-page="${view}"]`)?.classList.add('active');
  state.view = view;
  $('#pageTitle').textContent = view === 'command' ? 'Command center' : view === 'schedule' ? '24-hour plan' : 'Campus profile';
  $$('.nav-item').forEach(item => item.classList.toggle('active', item.dataset.view === view));
  $('#appShell').classList.remove('mobile-open');
  if (view === 'schedule') renderSchedule();
  if (view === 'settings') renderSettings();
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function renderMessages() {
  const container = $('#conversation');
  container.innerHTML = state.messages.map((message) => {
    const avatar = message.role === 'assistant' ? icon('spark') : '<span>OP</span>';
    const content = message.html || `<p>${escapeHtml(message.text)}</p>`;
    return `<div class="message ${message.role}"><span class="message-avatar">${avatar}</span><div class="bubble ${message.result ? 'assistant-result' : ''}">${content}<small class="message-time">${message.time || now()}</small></div></div>`;
  }).join('');
  container.scrollTop = container.scrollHeight;
  $('#noteCount').textContent = `${state.scenario.operator_notes.length} of 3 instructions`;
  const hasDraft = Boolean($('#chatInput').value.trim());
  $('#sendCommand').disabled = state.busy
    || (!hasDraft && state.scenario.operator_notes.length === 0)
    || (hasDraft && state.scenario.operator_notes.length >= 3);
}

function directiveSummary(item) {
  const adjustment = item.structured_adjustment;
  if (!item.applies) return 'This note does not change today’s energy plan.';
  const hours = adjustment.hours?.length ? `${hourLabel(adjustment.hours[0])}–${hourLabel(adjustment.hours.at(-1) + 1)}` : '';
  if (item.directive_type === 'solar_reduction') return `${hours} · ${Math.round(adjustment.factor * 100)}% solar remains`;
  if (item.directive_type === 'minimum_battery_reserve') return `${hours} · keep at least ${formatNumber(adjustment.minimum_energy_kwh, 1)} kWh`;
  if (item.directive_type === 'max_grid_window') return `${hours} · maximum ${formatNumber(adjustment.max_grid_kwh, 1)} kWh`;
  return hours;
}

function resultMessage(response) {
  const items = response.directive_interpretation.map(item => `<div class="understood-item"><span>${icon(item.applies ? 'check' : 'info')}</span><div><b>${directiveNames[item.directive_type]}</b><small>${escapeHtml(directiveSummary(item))}</small></div></div>`).join('');
  return `<p><strong>I’ve built the 24-hour plan.</strong> Here’s what I understood from your instructions:</p><div class="understood-list">${items}</div><p>The plan costs <strong>${formatNumber(response.total_cost_bdt, 0)} BDT</strong>, keeps peak grid draw at <strong>${formatNumber(response.peak_grid_kwh, 1)} kWh</strong>, and finishes with the battery restored to its starting level.</p><button class="result-link" data-chat-schedule>${icon('calendar')} Open full schedule</button>`;
}

function setTyping(active) {
  state.busy = active;
  state.messages = state.messages.filter(message => !message.typing);
  if (active) state.messages.push({ role: 'assistant', typing: true, html: '<div class="typing"><i></i><i></i><i></i></div><p>Understanding your instructions and building the best plan…</p>' });
  renderMessages();
}

function validateScenario() {
  if (!state.scenario.operator_notes.length) return 'Add at least one instruction for GridWise.';
  if (state.scenario.operator_notes.length > 3) return 'GridWise accepts up to three instructions at once.';
  if (state.scenario.hours.length !== 24) return 'The scenario needs all 24 hourly records.';
  return null;
}

async function optimize(newInstruction = '') {
  syncSettings();
  const instruction = newInstruction.trim();
  if (instruction) {
    if (state.scenario.operator_notes.length >= 3) return toast('Three-instruction limit reached', 'Clear an instruction or start a new plan.', 'error');
    state.scenario.operator_notes.push(instruction);
    state.messages.push({ role: 'user', text: instruction });
    $('#chatInput').value = '';
  }
  const issue = validateScenario();
  if (issue) return toast('Plan needs more information', issue, 'error');
  setTyping(true);
  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 30000);
    const response = await fetch('/optimize-energy', { method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'application/json' }, body: JSON.stringify(state.scenario), signal: controller.signal });
    clearTimeout(timeout);
    const data = await response.json().catch(() => null);
    if (!response.ok || !data?.hourly_plan || !data?.directive_interpretation) throw Object.assign(new Error('Optimization failed'), { status: response.status });
    state.response = data;
    setTyping(false);
    state.messages.push({ role: 'assistant', html: resultMessage(data), result: true });
    renderMessages(); renderResults(); renderSchedule();
    toast('Plan ready', 'GridWise optimized all 24 hours.', 'success');
  } catch (error) {
    setTyping(false);
    const message = error.name === 'AbortError' ? 'The plan took too long to complete.' : error.status === 400 ? 'The campus data needs attention.' : error.status === 422 ? 'One instruction could not be applied safely.' : 'GridWise could not complete the plan right now.';
    state.messages.push({ role: 'assistant', html: `<p><strong>I couldn’t finish this plan.</strong></p><p>${escapeHtml(message)} Your instructions are still here, so you can adjust them and try again.</p>` });
    renderMessages(); toast('Plan not completed', message, 'error');
  }
}

function renderContext() {
  $('#scenarioLabel').textContent = state.scenario.scenario_id;
  const demand = state.scenario.hours.reduce((sum, row) => sum + row.demand_kwh, 0);
  const solar = state.scenario.hours.reduce((sum, row) => sum + row.solar_kwh, 0);
  $('#dayDemand').textContent = `${formatNumber(demand, 0)} kWh`;
  $('#daySolar').textContent = `${formatNumber(solar, 0)} kWh`;
  $('#dayBattery').textContent = `${formatNumber(state.scenario.battery.capacity_kwh, 0)} kWh`;
  drawInputProfile($('#miniProfile'), state.scenario.hours);
}

function chartTooltip(hour, event) {
  const tooltip = $('#chartTooltip');
  if (hour == null) return tooltip.classList.add('hidden');
  const input = inputHour(hour), row = planHour(hour);
  tooltip.innerHTML = `<strong>${hourLabel(hour)}</strong><div class="tooltip-row"><span>Demand</span><b>${formatNumber(input.demand_kwh,1)}</b></div><div class="tooltip-row"><span>Solar</span><b>${formatNumber(row.solar_used_kwh,1)}</b></div><div class="tooltip-row"><span>Grid</span><b>${formatNumber(row.grid_kwh,1)}</b></div>`;
  const rect = $('#energyChart').getBoundingClientRect(); tooltip.style.left = `${Math.min(rect.width - 155, Math.max(10, (event?.clientX || rect.left + 40) - rect.left + 8))}px`; tooltip.style.top = '65px'; tooltip.classList.remove('hidden');
}

function renderBattery() {
  const row = planHour(state.selectedHour), battery = state.scenario.battery;
  if (!row) return;
  const percent = Math.max(0, Math.min(100, row.battery_energy_after_kwh / battery.capacity_kwh * 100));
  $('#batteryFill').style.height = `${percent}%`; $('#socPercent').textContent = `${Math.round(percent)}%`;
  $('#storedEnergy').textContent = `${formatNumber(row.battery_energy_after_kwh,1)} kWh`; $('#batteryCapacity').textContent = `of ${formatNumber(battery.capacity_kwh,1)} kWh`;
  $('#selectedHour').textContent = hourLabel(state.selectedHour); $('#batteryAction').textContent = row.battery_action; $('#batteryAction').className = `action-pill ${row.battery_action}`;
}

function renderResults() {
  const response = state.response;
  $('#resultSection').classList.toggle('hidden', !response);
  if (!response) return;
  animateNumber($('#kpiCost'), response.total_cost_bdt, value => formatNumber(value,0));
  animateNumber($('#kpiGrid'), response.total_grid_kwh, value => formatNumber(value,1));
  animateNumber($('#kpiPeak'), response.peak_grid_kwh, value => formatNumber(value,1));
  animateNumber($('#kpiBattery'), response.hourly_plan.at(-1).battery_energy_after_kwh, value => formatNumber(value,1));
  drawEnergyChart($('#energyChart'), response.hourly_plan, state.scenario.hours, { demand:true, solar:true, grid:true }, chartTooltip);
  renderBattery();
}

function renderTimeline() {
  $('#hourTimeline').innerHTML = state.response.hourly_plan.map(row => {
    const mode = row.battery_action === 'charge' ? 'var(--green)' : row.battery_action === 'discharge' ? 'var(--violet)' : 'var(--muted)';
    const activity = Math.max(6, Math.min(25, row.grid_kwh / Math.max(1, inputHour(row.hour).demand_kwh) * 20));
    return `<button class="hour-node ${state.selectedHour === row.hour ? 'selected' : ''} ${directivesAt(row.hour).length ? 'directive' : ''}" style="--mode:${mode};--activity:${activity}px" data-hour="${row.hour}"><span>${String(row.hour).padStart(2,'0')}</span></button>`;
  }).join('');
  const input = inputHour(state.selectedHour), row = planHour(state.selectedHour), directive = directivesAt(state.selectedHour);
  const details = [['Hour',hourLabel(row.hour)],['Demand',`${formatNumber(input.demand_kwh,1)} kWh`],['Solar used',`${formatNumber(row.solar_used_kwh,1)} kWh`],['Grid',`${formatNumber(row.grid_kwh,1)} kWh`],['Battery',`${row.battery_action} ${formatNumber(row.battery_kwh,1)} kWh`],['Instruction',directive.length ? directiveNames[directive[0].directive_type] : 'None']];
  $('#hourDetail').innerHTML = `<div class="detail-grid">${details.map(([label,value])=>`<div><span>${label}</span><strong>${escapeHtml(value)}</strong></div>`).join('')}</div>`;
}

function renderSchedule() {
  const available = Boolean(state.response);
  $('#emptyPlan').classList.toggle('hidden', available); $('#scheduleContent').classList.toggle('hidden', !available);
  if (!available) return;
  renderTimeline();
  $('#scheduleBody').innerHTML = state.response.hourly_plan.map(row => { const input = inputHour(row.hour); return `<tr><td><strong>${hourLabel(row.hour)}</strong></td><td>${formatNumber(input.demand_kwh,1)}</td><td>${formatNumber(row.solar_used_kwh,1)}</td><td><strong>${formatNumber(row.grid_kwh,1)}</strong></td><td>${formatNumber(input.tariff_bdt_per_kwh,1)}</td><td><span class="action-tag ${row.battery_action}">${row.battery_action}</span></td><td>${formatNumber(row.battery_kwh,1)}</td><td>${formatNumber(row.battery_energy_after_kwh,1)}</td></tr>`; }).join('');
}

function renderSettings() {
  $('#scenarioId').value = state.scenario.scenario_id;
  const fields = [['capacity_kwh','Battery capacity'],['initial_energy_kwh','Starting energy'],['minimum_energy_kwh','Minimum reserve'],['max_charge_kwh_per_hour','Maximum charge / hour'],['max_discharge_kwh_per_hour','Maximum discharge / hour']];
  $('#batteryForm').innerHTML = fields.map(([key,label])=>`<label>${label}<input type="number" min="0" step="0.1" data-battery="${key}" value="${state.scenario.battery[key]}"></label>`).join('');
  $('#hoursInputBody').innerHTML = state.scenario.hours.map(row=>`<tr><td><strong>${hourLabel(row.hour)}</strong></td><td><input type="number" min="0" data-hour="${row.hour}" data-field="demand_kwh" value="${row.demand_kwh}"></td><td><input type="number" min="0" data-hour="${row.hour}" data-field="solar_kwh" value="${row.solar_kwh}"></td><td><input type="number" min="0" data-hour="${row.hour}" data-field="tariff_bdt_per_kwh" value="${row.tariff_bdt_per_kwh}"></td></tr>`).join('');
}

function syncSettings() {
  if ($('#scenarioId')) state.scenario.scenario_id = $('#scenarioId').value.trim() || state.scenario.scenario_id;
  $$('[data-battery]').forEach(input => state.scenario.battery[input.dataset.battery] = Number(input.value));
  $$('[data-hour][data-field]').forEach(input => { const row = inputHour(Number(input.dataset.hour)); if (row) row[input.dataset.field] = Number(input.value); });
}

function newConversation() {
  state.scenario.operator_notes = []; state.response = null; state.messages = [assistantWelcome()]; state.selectedHour = 12;
  $('#chatInput').value = ''; renderMessages(); renderResults(); renderSchedule();
}

async function checkHealth() {
  const status = $('#systemStatus');
  try { const response = await fetch('/health'); const data = await response.json(); if (!response.ok || data.status !== 'ok') throw new Error(); status.className='system-status online'; status.querySelector('span').textContent='System online'; }
  catch { status.className='system-status offline'; status.querySelector('span').textContent='System offline'; }
}

function setupEvents() {
  $$('.nav-item').forEach(button=>button.addEventListener('click',()=>navigate(button.dataset.view)));
  $$('[data-navigate]').forEach(button=>button.addEventListener('click',()=>navigate(button.dataset.navigate)));
  $('#mobileMenu').addEventListener('click',()=>$('#appShell').classList.add('mobile-open')); $('#mobileOverlay').addEventListener('click',()=>$('#appShell').classList.remove('mobile-open'));
  $('#themeToggle').addEventListener('click',()=>{ const theme=document.documentElement.dataset.theme==='dark'?'light':'dark'; document.documentElement.dataset.theme=theme; localStorage.setItem('gridwise-theme',theme); $('#themeToggle span').dataset.icon=theme==='dark'?'moon':'sun'; hydrateIcons($('#themeToggle')); renderContext(); if(state.response) renderResults(); });
  $('#sendCommand').addEventListener('click',()=>optimize($('#chatInput').value));
  $('#chatInput').addEventListener('keydown',event=>{ if(event.key==='Enter'&&!event.shiftKey){event.preventDefault();optimize(event.currentTarget.value);} });
  $('#chatInput').addEventListener('input',event=>{ event.currentTarget.style.height='auto'; event.currentTarget.style.height=`${Math.min(100,event.currentTarget.scrollHeight)}px`; renderMessages(); });
  $('#quickPrompts').addEventListener('click',event=>{ const button=event.target.closest('button'); if(!button)return; $('#chatInput').value=button.textContent; $('#chatInput').focus(); renderMessages(); });
  $('#newConversation').addEventListener('click',newConversation); $('#clearNotes').addEventListener('click',()=>{state.scenario.operator_notes=[];state.messages=[assistantWelcome()];renderMessages();});
  $('#conversation').addEventListener('click',event=>{if(event.target.closest('[data-chat-schedule]'))navigate('schedule');});
  $$('[data-hour-step]').forEach(button=>button.addEventListener('click',()=>{state.selectedHour=(state.selectedHour+Number(button.dataset.hourStep)+24)%24;renderBattery();if(state.view==='schedule')renderTimeline();}));
  $('#hourTimeline').addEventListener('click',event=>{const button=event.target.closest('[data-hour]');if(!button)return;state.selectedHour=Number(button.dataset.hour);renderTimeline();renderBattery();});
  $('#scenarioId').addEventListener('change',()=>{syncSettings();renderContext();}); $('#batteryForm').addEventListener('change',()=>{syncSettings();renderContext();}); $('#hoursInputBody').addEventListener('change',()=>{syncSettings();renderContext();});
  document.addEventListener('keydown',event=>{if(event.key==='Escape')$('#appShell').classList.remove('mobile-open');});
}

async function init() {
  document.documentElement.dataset.theme=localStorage.getItem('gridwise-theme')||'dark'; state.scenario=defaultScenario();state.messages=[assistantWelcome()];
  hydrateIcons();renderMessages();renderContext();renderResults();renderSchedule();renderSettings();setupEvents();await checkHealth();
}

init();
