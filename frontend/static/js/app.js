/* ═══════════════════════════════════════════════════════════════════
   MermaZero — Sistema de Control de Mermas Makro Chincha 2026
   ═══════════════════════════════════════════════════════════════════ */

let TOKEN      = localStorage.getItem('token') || null;
let LOTES_DATA = [];
let PAG_ACTUAL = 1;
const POR_PAG  = 12;
let ORDEN      = { campo: 'dias_para_vencer', asc: true };
let CHART_DONUT = null;
let CHART_BAR   = null;
let SECCION_ACTUAL = 'dashboard';
let LOGIN_BUSY = false;

const TOPBAR_TITLES = {
  'dashboard':   ['Centro de Mando',       'Resumen operativo del almacén'],
  'lotes':       ['Control de Inventario', 'Inventario completo de productos perecibles'],
  'alertas':     ['Centro de Alertas',     'Productos que requieren atención inmediata'],
  'nuevo-lote':  ['Ingreso de Producto',   'Registro de nuevo lote al inventario'],
  'reportes':    ['Análisis y Reportes',   'Exportación y estadísticas de trazabilidad'],
};

// ── Init ──────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('fecha-actual').textContent =
    new Date().toLocaleDateString('es-PE', { weekday:'short', day:'numeric', month:'short', year:'numeric' });
  document.getElementById('f-ingreso').value = isoHoy();
  document.getElementById('f-vencimiento').addEventListener('input', actualizarPreviewAlerta);
  if (TOKEN) mostrarApp();
});

function isoHoy() {
  return new Date().toISOString().split('T')[0];
}

// ── AUTH ──────────────────────────────────────────────────────────
async function iniciarSesion(e) {
  if (LOGIN_BUSY) return;
  LOGIN_BUSY = true;

  const email    = document.getElementById('login-email').value.trim();
  const password = document.getElementById('login-password').value;
  const errEl    = document.getElementById('login-error');
  const btn      = document.getElementById('btn-login');
  const wf       = document.getElementById('water-fill');
  const gb       = document.getElementById('gold-burst');
  const spin     = document.getElementById('btn-spin');
  const chk      = document.getElementById('btn-check');
  const txt      = document.getElementById('btn-text');

  errEl.textContent = '';

  // Ripple
  if (e) {
    const rect = btn.getBoundingClientRect();
    const r = document.createElement('div');
    r.className = 'ripple';
    const size = Math.max(rect.width, rect.height);
    r.style.cssText = `width:${size}px;height:${size}px;left:${(e.clientX||rect.left+rect.width/2)-rect.left-size/2}px;top:${(e.clientY||rect.top+rect.height/2)-rect.top-size/2}px`;
    btn.appendChild(r);
    setTimeout(() => r.remove(), 500);
  }

  // Efecto agua sube
  btn.disabled = true;
  spin.style.display = 'block';
  txt.textContent = 'Ingresando...';
  btn.classList.add('loading');

  const form = new FormData();
  form.append('username', email);
  form.append('password', password);

  try {
    const res  = await fetch('/api/auth/login', { method: 'POST', body: form });
    const data = await res.json();

    await new Promise(r => setTimeout(r, 2000)); // esperar animación agua

    if (!res.ok) {
      // Error — reset botón
      btn.classList.remove('loading');
      wf.style.animation = 'none'; wf.offsetHeight;
      spin.style.display = 'none';
      txt.textContent = 'Ingresar al Sistema';
      txt.style.color = '#fff';
      btn.disabled = false;
      LOGIN_BUSY = false;
      errEl.textContent = data.detail || 'Credenciales incorrectas.';
      return;
    }

    // Explosión dorada — acceso concedido
    TOKEN = data.access_token;
    localStorage.setItem('token', TOKEN);
    try {
      const payload = JSON.parse(atob(TOKEN.split('.')[1]));
      localStorage.setItem('user_email', payload.sub || email);
      localStorage.setItem('user_rol',   payload.rol  || 'OPERADOR');
    } catch {}

    btn.classList.remove('loading');
    btn.classList.add('burst');
    spin.style.display = 'none';
    chk.classList.add('show');
    txt.textContent = 'Acceso concedido';
    txt.style.color = '#0a1628';

    setTimeout(() => mostrarApp(), 1200);

  } catch {
    btn.classList.remove('loading');
    wf.style.animation = 'none'; wf.offsetHeight;
    spin.style.display = 'none';
    txt.textContent = 'Ingresar al Sistema';
    btn.disabled = false;
    LOGIN_BUSY = false;
    errEl.textContent = 'Error de conexión con el servidor.';
  }
}

function cerrarSesion() {
  TOKEN = null;
  localStorage.removeItem('token');
  document.getElementById('app').classList.add('hidden');
  document.getElementById('login-screen').classList.remove('hidden');
  // Reset botón login
  const btn = document.getElementById('btn-login');
  const wf  = document.getElementById('water-fill');
  const gb  = document.getElementById('gold-burst');
  const chk = document.getElementById('btn-check');
  const txt = document.getElementById('btn-text');
  btn.classList.remove('loading','burst');
  wf.style.animation = 'none'; wf.offsetHeight;
  gb.style.animation = 'none'; gb.style.opacity = '0'; gb.style.transform = 'scale(0)'; gb.offsetHeight;
  chk.classList.remove('show');
  txt.textContent = 'Ingresar al Sistema';
  txt.style.color = '#fff';
  btn.disabled = false;
  LOGIN_BUSY = false;
  if (CHART_DONUT) { CHART_DONUT.destroy(); CHART_DONUT = null; }
  if (CHART_BAR)   { CHART_BAR.destroy();   CHART_BAR   = null; }
}

function mostrarApp() {
  document.getElementById('login-screen').classList.add('hidden');
  document.getElementById('app').classList.remove('hidden');
  const email = localStorage.getItem('user_email') || 'Operador';
  const rol   = localStorage.getItem('user_rol')   || 'OPERADOR';
  document.getElementById('usuario-nombre').textContent = email.split('@')[0];
  document.getElementById('usuario-rol').textContent    = rol;
  ir('dashboard');
}

// ── NAVEGACIÓN ────────────────────────────────────────────────────
function ir(seccion) {
  SECCION_ACTUAL = seccion;
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  const sec = document.getElementById(`sec-${seccion}`);
  if (sec) sec.classList.add('active');
  const nav = document.querySelector(`.nav-item[onclick="ir('${seccion}')"]`);
  if (nav) nav.classList.add('active');
  const [title, sub] = TOPBAR_TITLES[seccion] || [seccion,''];
  document.getElementById('topbar-title').textContent    = title;
  document.getElementById('topbar-subtitle').textContent = sub;
  if (seccion === 'dashboard')  cargarDashboard();
  if (seccion === 'lotes')      cargarLotes();
  if (seccion === 'alertas')    cargarAlertas();
  if (seccion === 'reportes')   cargarReportes();
  if (seccion === 'nuevo-lote') limpiarFormulario();
}

function refrescarSeccion() {
  const btn = document.getElementById('btn-refresh');
  btn.classList.add('spinning');
  ir(SECCION_ACTUAL);
  setTimeout(() => btn.classList.remove('spinning'), 700);
}

// ── API ───────────────────────────────────────────────────────────
async function apiFetch(url, opts = {}) {
  const headers = { 'Authorization': `Bearer ${TOKEN}`, 'Content-Type': 'application/json', ...(opts.headers||{}) };
  try {
    const res = await fetch(url, { ...opts, headers });
    if (res.status === 401) { cerrarSesion(); return null; }
    return res;
  } catch {
    toast('Error de conexión con el servidor', 'error');
    return null;
  }
}

// ── DASHBOARD ─────────────────────────────────────────────────────
async function cargarDashboard() {
  const [resDash, resLotes] = await Promise.all([apiFetch('/api/dashboard'), apiFetch('/api/lotes')]);
  if (!resDash || !resLotes) return;
  const dash  = await resDash.json();
  const lotes = await resLotes.json();
  LOTES_DATA  = lotes;

  animarNumero('d-total',     dash.total_lotes);
  animarNumero('d-stock',     dash.lotes_en_stock);
  animarNumero('d-rojas',     dash.alertas_rojas);
  animarNumero('d-amarillas', dash.alertas_amarillas);
  animarNumero('d-vencidos',  dash.lotes_vencidos);
  document.getElementById('d-merma').textContent = `S/. ${dash.merma_valorizada.toFixed(2)}`;

  const trendEl = document.getElementById('d-trend-rojas');
  if (dash.alertas_rojas > 0) {
    trendEl.textContent = `⚠ ${dash.alertas_rojas} requieren atención inmediata`;
    trendEl.className = 'kpi-trend danger';
  } else {
    trendEl.textContent = '✓ Sin urgencias';
    trendEl.className = 'kpi-trend ok';
  }

  const total = dash.alertas_rojas + dash.alertas_amarillas;
  const badge = document.getElementById('badge-alertas');
  badge.textContent = total;
  badge.classList.toggle('hidden', total === 0);

  renderDonut(dash.lotes_en_stock - dash.alertas_rojas - dash.alertas_amarillas, dash.alertas_amarillas, dash.alertas_rojas, dash.lotes_vencidos);
  renderBarCategorias(lotes);
  renderTablaUrgentes(lotes);

  actualizarHero(dash, lotes);
}

function actualizarHero(dash, lotes) {
  const hero    = document.getElementById('dash-hero');
  const title   = document.getElementById('hero-title');
  const sub     = document.getElementById('hero-sub');
  const merma   = document.getElementById('hero-merma');
  const fecha   = document.getElementById('hero-fecha');
  if (!hero) return;

  const enRiesgo = lotes
    .filter(l => l.nivel_alerta === 'ALERTA_ROJA')
    .reduce((s, l) => s + (l.cantidad || 0) * (l.costo_unitario || 0), 0);

  if (fecha) fecha.textContent = new Date().toLocaleDateString('es-PE',
    { weekday: 'long', day: 'numeric', month: 'long' });

  if (dash.alertas_rojas > 0) {
    title.textContent = `${dash.alertas_rojas} lote${dash.alertas_rojas > 1 ? 's' : ''} requieren atención inmediata`;
    sub.textContent   = `${dash.alertas_amarillas} en alerta amarilla · ${dash.lotes_en_stock} en stock · revísalos hoy antes del vencimiento`;
    hero.classList.add('alert');
  } else if (dash.alertas_amarillas > 0) {
    title.textContent = `${dash.alertas_amarillas} lote${dash.alertas_amarillas > 1 ? 's' : ''} por vencer pronto`;
    sub.textContent   = `Sin alertas rojas · ${dash.lotes_en_stock} lotes en stock bajo control`;
    hero.classList.remove('alert');
  } else {
    title.textContent = 'Inventario bajo control';
    sub.textContent   = `${dash.lotes_en_stock} lotes en stock · sin alertas activas`;
    hero.classList.remove('alert');
  }
  if (merma) merma.textContent = `S/. ${enRiesgo.toFixed(2)}`;
}

function animarNumero(id, target) {
  const el = document.getElementById(id);
  let curr = 0;
  const step = Math.ceil(target / 20);
  const timer = setInterval(() => {
    curr = Math.min(curr + step, target);
    el.textContent = curr;
    if (curr >= target) clearInterval(timer);
  }, 30);
}

function renderDonut(normales, amarillas, rojas, vencidos) {
  const ctx = document.getElementById('chart-donut').getContext('2d');
  if (CHART_DONUT) CHART_DONUT.destroy();

  const data     = [normales, amarillas, rojas, vencidos];
  const total    = data.reduce((a, b) => a + b, 0);
  const enAlerta = amarillas + rojas;
  const pct      = total ? Math.round((enAlerta / total) * 100) : 0;

  const textoCentral = {
    id: 'textoCentral',
    afterDraw(chart) {
      const { ctx, chartArea: { left, right, top, bottom } } = chart;
      const cx = (left + right) / 2, cy = (top + bottom) / 2;
      ctx.save();
      ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
      ctx.fillStyle = pct >= 50 ? '#dc2626' : '#0f172a';
      ctx.font = '700 30px "Space Grotesk", sans-serif';
      ctx.fillText(pct + '%', cx, cy - 9);
      ctx.fillStyle = '#94a3b8';
      ctx.font = '600 11px Inter, sans-serif';
      ctx.fillText('EN ALERTA', cx, cy + 15);
      ctx.restore();
    }
  };

  CHART_DONUT = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Sin alerta', 'Alerta Amarilla', 'Alerta Roja', 'Vencidos/Baja'],
      datasets: [{
        data,
        backgroundColor: ['#059669', '#f5a800', '#dc2626', '#94a3b8'],
        borderColor: '#fff', borderWidth: 3, borderRadius: 6,
        hoverOffset: 10, spacing: 2
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false, cutout: '70%',
      plugins: {
        legend: { position: 'bottom', labels: { font: { size: 11 }, padding: 14, boxWidth: 10, usePointStyle: true, pointStyle: 'circle' } },
        tooltip: {
          padding: 10, boxPadding: 4,
          callbacks: { label: (c) => { const p = total ? Math.round(c.parsed / total * 100) : 0; return ` ${c.label}: ${c.parsed} (${p}%)`; } }
        }
      }
    },
    plugins: [textoCentral]
  });
}

function renderBarCategorias(lotes) {
  const ctx = document.getElementById('chart-categorias').getContext('2d');
  if (CHART_BAR) CHART_BAR.destroy();
  const cats = {};
  lotes.forEach(l => {
    if (!cats[l.categoria]) cats[l.categoria] = { stock: 0, alerta: 0 };
    if (l.nivel_alerta === 'ALERTA_ROJA' || l.nivel_alerta === 'ALERTA_AMARILLA') cats[l.categoria].alerta++;
    else cats[l.categoria].stock++;
  });
  const labels = Object.keys(cats)
    .sort((a, b) => (cats[b].stock + cats[b].alerta) - (cats[a].stock + cats[a].alerta));
  CHART_BAR = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [
        { label: 'En stock',   data: labels.map(k => cats[k].stock),  backgroundColor: '#0052cc', borderRadius: 5, borderSkipped: false, maxBarThickness: 20 },
        { label: 'Con alerta', data: labels.map(k => cats[k].alerta), backgroundColor: '#f5a800', borderRadius: 5, borderSkipped: false, maxBarThickness: 20 },
      ]
    },
    options: {
      indexAxis: 'y',
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { position: 'bottom', labels: { font: { size: 11 }, boxWidth: 10, usePointStyle: true, pointStyle: 'circle', padding: 14 } } },
      scales: {
        x: { stacked: true, beginAtZero: true, grid: { color: '#f1f5f9' }, ticks: { font: { size: 11 }, precision: 0 } },
        y: { stacked: true, grid: { display: false }, ticks: { font: { size: 11 } } }
      }
    }
  });
}

function renderTablaUrgentes(lotes) {
  const urgentes = lotes.filter(l => l.nivel_alerta !== 'SIN_ALERTA' && l.estado === 'EN_STOCK')
    .sort((a,b) => (a.dias_para_vencer??999) - (b.dias_para_vencer??999)).slice(0,6);
  const tbody = document.getElementById('tabla-urgentes');
  if (!urgentes.length) {
    tbody.innerHTML = `<tr><td colspan="6" class="text-center text-muted" style="padding:2rem">✅ No hay lotes urgentes.</td></tr>`;
    return;
  }
  tbody.innerHTML = urgentes.map(l => `
    <tr>
      <td><span class="codigo-chip">${l.codigo}</span></td>
      <td><div class="producto-cell"><strong>${l.producto}</strong></div></td>
      <td><span class="tag tag-gris">${l.categoria}</span></td>
      <td>${buildDiasCell(l.dias_para_vencer)}</td>
      <td>${buildTagAlerta(l.nivel_alerta)}</td>
      <td class="text-muted">${l.proveedor}</td>
    </tr>`).join('');
}

// ── LOTES ─────────────────────────────────────────────────────────
async function cargarLotes() {
  const res = await apiFetch('/api/lotes');
  if (!res) return;
  LOTES_DATA = await res.json();
  PAG_ACTUAL = 1;
  renderTablaLotes();
}

function filtrarTabla() { PAG_ACTUAL = 1; renderTablaLotes(); }

function ordenarPor(campo) {
  if (ORDEN.campo === campo) ORDEN.asc = !ORDEN.asc;
  else { ORDEN.campo = campo; ORDEN.asc = true; }
  renderTablaLotes();
}

function renderTablaLotes() {
  const buscar = (document.getElementById('buscar-lote')?.value||'').toLowerCase();
  const estado = document.getElementById('filtro-estado')?.value||'';
  const alerta = document.getElementById('filtro-alerta')?.value||'';

  let data = LOTES_DATA.filter(l => {
    const mb = !buscar || l.producto.toLowerCase().includes(buscar) || l.codigo.toLowerCase().includes(buscar) || l.proveedor.toLowerCase().includes(buscar);
    return mb && (!estado||l.estado===estado) && (!alerta||l.nivel_alerta===alerta);
  });

  data.sort((a,b) => {
    let va = a[ORDEN.campo]??'', vb = b[ORDEN.campo]??'';
    if (typeof va==='string') va=va.toLowerCase();
    if (typeof vb==='string') vb=vb.toLowerCase();
    if (va<vb) return ORDEN.asc?-1:1;
    if (va>vb) return ORDEN.asc?1:-1;
    return 0;
  });

  document.getElementById('lotes-count').textContent = `${data.length} lote${data.length!==1?'s':''} encontrado${data.length!==1?'s':''}`;

  const total = data.length;
  const pages = Math.ceil(total / POR_PAG);
  const inicio = (PAG_ACTUAL-1)*POR_PAG;
  const slice  = data.slice(inicio, inicio+POR_PAG);

  const tbody = document.getElementById('tabla-lotes');
  if (!slice.length) {
    tbody.innerHTML = `<tr><td colspan="10"><div class="empty-state"><div class="empty-icon">🔍</div><h3>Sin resultados</h3><p>Ajusta los filtros de búsqueda.</p></div></td></tr>`;
  } else {
    tbody.innerHTML = slice.map(l => `
      <tr>
        <td><span class="codigo-chip">${l.codigo}</span></td>
        <td><div class="producto-cell"><strong>${l.producto}</strong><small>${l.categoria}</small></div></td>
        <td><span class="tag tag-gris">${l.categoria}</span></td>
        <td>${l.cantidad} <small class="text-muted">${l.unidad}</small></td>
        <td class="text-muted" style="font-size:.8rem">${l.proveedor}</td>
        <td class="text-muted">${l.fecha_vencimiento}</td>
        <td>${buildDiasCell(l.dias_para_vencer)}</td>
        <td>${buildTagEstado(l.estado)}</td>
        <td>${buildTagAlerta(l.nivel_alerta)}</td>
        <td>
          <div class="actions-cell">
            <button class="btn-icon edit"   onclick="abrirEditar(${l.id})" title="Editar">✏️</button>
            <button class="btn-icon danger" onclick="darDeBaja(${l.id},'${l.codigo}')" title="Dar de baja">🗑️</button>
          </div>
        </td>
      </tr>`).join('');
  }

  document.getElementById('lotes-info-pag').textContent = `Mostrando ${inicio+1}–${Math.min(inicio+POR_PAG,total)} de ${total}`;
  renderPaginacion(pages);
}

function renderPaginacion(pages) {
  const cont = document.getElementById('paginacion');
  if (pages<=1) { cont.innerHTML=''; return; }
  let html = `<button class="page-btn" onclick="cambiarPag(${PAG_ACTUAL-1})" ${PAG_ACTUAL===1?'disabled':''}>‹</button>`;
  for (let i=1;i<=pages;i++) {
    if (pages>7 && i>2 && i<pages-1 && Math.abs(i-PAG_ACTUAL)>1) {
      if (i===3||i===pages-2) html+=`<button class="page-btn" disabled>…</button>`;
      continue;
    }
    html+=`<button class="page-btn ${i===PAG_ACTUAL?'active':''}" onclick="cambiarPag(${i})">${i}</button>`;
  }
  html+=`<button class="page-btn" onclick="cambiarPag(${PAG_ACTUAL+1})" ${PAG_ACTUAL===pages?'disabled':''}>›</button>`;
  cont.innerHTML=html;
}

function cambiarPag(p) {
  const pages = Math.ceil(LOTES_DATA.length/POR_PAG);
  if (p<1||p>pages) return;
  PAG_ACTUAL=p; renderTablaLotes();
}

// ── HELPERS ───────────────────────────────────────────────────────
function buildDiasCell(dias) {
  if (dias===null||dias===undefined) return '<span class="text-muted">–</span>';
  let cls = dias<=0?'vencido':dias<=3?'critico':dias<=7?'advertencia':'normal';
  return `<span class="dias-cell ${cls}">${dias<=0?'Vencido':dias+'d'}</span>`;
}
function buildTagAlerta(nivel) {
  return { ALERTA_ROJA:'<span class="tag tag-roja">🔴 Roja</span>', ALERTA_AMARILLA:'<span class="tag tag-amarilla">🟡 Amarilla</span>', SIN_ALERTA:'<span class="tag tag-verde">✅ Normal</span>' }[nivel] || `<span class="tag tag-gris">${nivel}</span>`;
}
function buildTagEstado(estado) {
  return { EN_STOCK:'<span class="tag tag-azul">En Stock</span>', POR_VENCER:'<span class="tag tag-amarilla">Por Vencer</span>', VENCIDO:'<span class="tag tag-roja">Vencido</span>', DADO_DE_BAJA:'<span class="tag tag-gris">Baja</span>' }[estado] || estado;
}

// ── MODAL EDITAR ──────────────────────────────────────────────────
function abrirEditar(id) {
  const lote = LOTES_DATA.find(l=>l.id===id);
  if (!lote) return;
  document.getElementById('edit-id').value        = id;
  document.getElementById('edit-cantidad').value  = lote.cantidad;
  document.getElementById('edit-ubicacion').value = lote.ubicacion;
  document.getElementById('edit-estado').value    = lote.estado;
  document.getElementById('modal-editar').classList.add('open');
}
function cerrarModal() { document.getElementById('modal-editar').classList.remove('open'); }

async function guardarEdicion() {
  const id = document.getElementById('edit-id').value;
  const payload = {
    cantidad:  parseFloat(document.getElementById('edit-cantidad').value)||null,
    ubicacion: document.getElementById('edit-ubicacion').value.trim()||null,
    estado:    document.getElementById('edit-estado').value||null,
  };
  const res = await apiFetch(`/api/lotes/${id}`, { method:'PUT', body:JSON.stringify(payload) });
  if (!res) return;
  if (res.ok) { toast('Lote actualizado correctamente','success'); cerrarModal(); await cargarLotes(); }
  else { const err=await res.json(); toast(`Error: ${err.detail||'No se pudo actualizar'}`,'error'); }
}

async function darDeBaja(id, codigo) {
  if (!confirm(`¿Confirmas dar de baja el lote ${codigo}?`)) return;
  const res = await apiFetch(`/api/lotes/${id}`, { method:'DELETE' });
  if (res && (res.ok||res.status===204)) { toast(`Lote ${codigo} dado de baja`,'warn'); await cargarLotes(); }
  else toast('No se pudo dar de baja','error');
}

// ── ALERTAS ───────────────────────────────────────────────────────
let ALERTAS_DATA = [];
let FILTRO_ALERTA_ACTIVO = 'all';

async function cargarAlertas() {
  const res = await apiFetch('/api/alertas');
  if (!res) return;
  ALERTAS_DATA = await res.json();
  renderAlertas(FILTRO_ALERTA_ACTIVO);
}

function filtrarAlertas(filtro, btn) {
  FILTRO_ALERTA_ACTIVO = filtro;
  document.querySelectorAll('.filter-pill').forEach(p=>p.classList.remove('active'));
  if (btn) btn.classList.add('active');
  renderAlertas(filtro);
}

function renderAlertas(filtro) {
  const cont  = document.getElementById('alertas-grid');
  const empty = document.getElementById('alertas-empty');
  let data = ALERTAS_DATA;
  if (filtro==='roja')     data=data.filter(a=>a.nivel==='ALERTA_ROJA');
  if (filtro==='amarilla') data=data.filter(a=>a.nivel==='ALERTA_AMARILLA');
  if (!data.length) { cont.innerHTML=''; empty.classList.remove('hidden'); return; }
  empty.classList.add('hidden');
  cont.innerHTML = data.map(a => {
    const esRoja = a.nivel==='ALERTA_ROJA';
    const diasTxt = a.dias_restantes<=0?'Vencido':a.dias_restantes;
    return `
    <div class="alerta-card ${esRoja?'roja':'amarilla'}">
      <div class="alerta-nivel-icon">${esRoja?'🔴':'🟡'}</div>
      <div class="alerta-body" style="flex:1">
        <div class="alerta-producto">${a.producto||'Producto'}</div>
        <div class="alerta-mensaje">${a.mensaje}</div>
        <div class="alerta-meta">
          <span class="alerta-meta-item">📋 Lote #${a.lote_id}</span>
          <span class="alerta-meta-item">${buildTagAlerta(a.nivel)}</span>
        </div>
      </div>
      <div class="alerta-dias-badge">
        <div class="dias-big ${esRoja?'critico':'warn'}">${diasTxt}</div>
        <div class="dias-label">${a.dias_restantes<=0?'':'días'}</div>
      </div>
    </div>`;
  }).join('');
}

// ── REGISTRAR LOTE ────────────────────────────────────────────────
function actualizarPreviewAlerta() {
  const venc = document.getElementById('f-vencimiento').value;
  const prev = document.getElementById('preview-alerta');
  if (!venc) { prev.classList.add('hidden'); return; }
  const hoy  = new Date(); hoy.setHours(0,0,0,0);
  const fv   = new Date(venc+'T00:00:00');
  const dias = Math.round((fv-hoy)/86400000);
  let msg, color, border;
  if (dias<=0)      { msg=`⛔ Este producto ya está vencido.`; color='#fef2f2'; border='#dc2626'; }
  else if (dias<=3) { msg=`🔴 ALERTA ROJA: vence en ${dias} día(s). Acción inmediata.`; color='#fef2f2'; border='#dc2626'; }
  else if (dias<=7) { msg=`🟡 ALERTA AMARILLA: vence en ${dias} día(s). Monitorear.`; color='#fffbeb'; border='#f5a800'; }
  else              { msg=`✅ Sin alerta: vence en ${dias} día(s). Dentro del rango seguro.`; color='#ecfdf5'; border='#059669'; }
  prev.style.background=color; prev.style.borderColor=border; prev.style.color='#1e293b';
  prev.textContent=msg; prev.classList.remove('hidden');
}

function limpiarFormulario() {
  ['f-codigo','f-producto','f-proveedor','f-ubicacion'].forEach(id=>{const el=document.getElementById(id);if(el)el.value='';});
  document.getElementById('f-categoria').value='';
  document.getElementById('f-unidad').value='kg';
  document.getElementById('f-cantidad').value='';
  document.getElementById('f-costo').value='';
  document.getElementById('f-ingreso').value=isoHoy();
  document.getElementById('f-vencimiento').value='';
  document.getElementById('preview-alerta').classList.add('hidden');
  document.getElementById('form-result').innerHTML='';
  document.querySelectorAll('.field-error').forEach(e=>e.textContent='');
}

async function registrarLote() {
  const btn = document.getElementById('btn-registrar');
  const res_el = document.getElementById('form-result');
  res_el.innerHTML='';
  const payload = {
    codigo:            document.getElementById('f-codigo').value.trim(),
    producto:          document.getElementById('f-producto').value.trim(),
    categoria:         document.getElementById('f-categoria').value,
    cantidad:          parseFloat(document.getElementById('f-cantidad').value),
    unidad:            document.getElementById('f-unidad').value,
    proveedor:         document.getElementById('f-proveedor').value.trim(),
    fecha_ingreso:     document.getElementById('f-ingreso').value,
    fecha_vencimiento: document.getElementById('f-vencimiento').value,
    ubicacion:         document.getElementById('f-ubicacion').value.trim(),
    costo_unitario:    parseFloat(document.getElementById('f-costo').value)||0,
  };
  let ok=true;
  const check=(id,errId,cond,msg)=>{const e=document.getElementById(errId),i=document.getElementById(id);if(!cond){if(e)e.textContent=msg;if(i)i.classList.add('error');ok=false;}else{if(e)e.textContent='';if(i)i.classList.remove('error');}};
  check('f-codigo','err-codigo',payload.codigo.length>=3,'Código demasiado corto');
  if(!payload.producto)         {ok=false;toast('El producto es obligatorio','error');}
  if(!payload.categoria)        {ok=false;toast('Selecciona una categoría','error');}
  if(isNaN(payload.cantidad)||payload.cantidad<=0){ok=false;toast('La cantidad debe ser mayor a 0','error');}
  if(!payload.proveedor)        {ok=false;toast('El proveedor es obligatorio','error');}
  if(!payload.fecha_vencimiento){ok=false;toast('La fecha de vencimiento es obligatoria','error');}
  if(!payload.ubicacion)        {ok=false;toast('La ubicación es obligatoria','error');}
  if(!ok) return;
  btn.textContent='⏳ Registrando…'; btn.disabled=true;
  const res = await apiFetch('/api/lotes/', {method:'POST',body:JSON.stringify(payload)});
  btn.textContent='✓ Registrar Lote'; btn.disabled=false;
  if(!res) return;
  const data = await res.json();
  if(!res.ok){res_el.innerHTML=`<div class="form-result error">⚠ ${data.detail||'Error al registrar.'}</div>`;return;}
  res_el.innerHTML=`<div class="form-result ok">✅ Lote <strong>${data.codigo}</strong> registrado — nivel: <strong>${(data.nivel_alerta||'').replace('_',' ')}</strong></div>`;
  toast(`Lote ${data.codigo} registrado exitosamente`,'success');
  setTimeout(()=>ir('lotes'),1800);
}

// ── REPORTES ──────────────────────────────────────────────────────
async function cargarReportes() {
  if (!LOTES_DATA.length) { const res=await apiFetch('/api/lotes');if(!res)return;LOTES_DATA=await res.json(); }
  const cats={};
  LOTES_DATA.forEach(l=>{
    if(!cats[l.categoria])cats[l.categoria]={total:0,stock:0,rojas:0,amarillas:0,merma:0};
    const c=cats[l.categoria];c.total++;
    if(l.estado==='EN_STOCK')c.stock++;
    if(l.nivel_alerta==='ALERTA_ROJA')c.rojas++;
    if(l.nivel_alerta==='ALERTA_AMARILLA')c.amarillas++;
    if(l.estado==='VENCIDO'||l.estado==='DADO_DE_BAJA')c.merma+=(l.cantidad||0)*(l.costo_unitario||0);
  });
  const tbody=document.getElementById('tabla-resumen-categoria');
  tbody.innerHTML=Object.entries(cats).sort((a,b)=>b[1].total-a[1].total).map(([cat,c])=>`
    <tr>
      <td><strong>${cat}</strong></td><td>${c.total}</td><td>${c.stock}</td>
      <td>${c.rojas>0?`<span class="tag tag-roja">🔴 ${c.rojas}</span>`:'–'}</td>
      <td>${c.amarillas>0?`<span class="tag tag-amarilla">🟡 ${c.amarillas}</span>`:'–'}</td>
      <td>${c.merma>0?`<strong style="color:#7c3aed">S/. ${c.merma.toFixed(2)}</strong>`:'–'}</td>
    </tr>`).join('')||`<tr><td colspan="6" class="text-center text-muted" style="padding:2rem">Sin datos</td></tr>`;
}

// ── EXPORTAR EXCEL (reportes reales desde el backend) ─────────────
async function exportarCSV() {
  toast('⏳ Generando Excel de inventario...', 'info');
  await descargarExcel('/api/reportes/inventario', `MermaZero_Inventario_${isoHoy()}.xlsx`);
}
async function exportarMermasCSV() {
  toast('⏳ Generando reporte de mermas...', 'info');
  await descargarExcel('/api/reportes/mermas', `MermaZero_Mermas_${isoHoy()}.xlsx`);
}
async function exportarAlertasCSV() {
  toast('⏳ Generando reporte de alertas...', 'info');
  await descargarExcel('/api/reportes/alertas', `MermaZero_Alertas_${isoHoy()}.xlsx`);
}

async function descargarExcel(url, nombre) {
  try {
    const res = await fetch(url, {
      headers: { 'Authorization': `Bearer ${TOKEN}` }
    });
    if (!res.ok) { toast('Error al generar el reporte', 'error'); return; }
    const blob = await res.blob();
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = nombre;
    link.click();
    URL.revokeObjectURL(link.href);
    toast('✅ Excel descargado correctamente', 'success');
  } catch {
    toast('Error de conexión al generar reporte', 'error');
  }
}

// ── TOAST ─────────────────────────────────────────────────────────
function toast(msg, tipo='success') {
  const iconos={success:'✅',error:'❌',warn:'⚠️',info:'ℹ️'};
  const cont=document.getElementById('toast-container');
  const el=document.createElement('div');
  el.className=`toast ${tipo}`;
  el.innerHTML=`<span class="toast-icon">${iconos[tipo]||'💬'}</span><span>${msg}</span><button class="toast-close" onclick="this.parentElement.remove()">✕</button>`;
  cont.appendChild(el);
  requestAnimationFrame(()=>el.classList.add('show'));
  setTimeout(()=>{el.classList.remove('show');setTimeout(()=>el.remove(),350);},3500);
}

// ── CERRAR MODAL CON ESC ──────────────────────────────────────────
document.addEventListener('keydown', e => { if(e.key==='Escape') cerrarModal(); });
document.getElementById('modal-editar')?.addEventListener('click', e => { if(e.target===e.currentTarget) cerrarModal(); });
