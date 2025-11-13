<template>
  <div class="ensayo-resultados">
    <div class="header-row">
      <h2 class="titulo">Resultados — {{ resumen.titulo || ('Ensayo ' + ensayoId) }}</h2>
      <div class="meta-right">
        <div class="participantes" v-if="resumen.total_participantes !== undefined">
          Participantes: <strong>{{ resumen.total_participantes }}</strong>
        </div>
      </div>
    </div>

    <div v-if="loadingSummary" class="loading">Cargando resumen...</div>

    <section class="seccion">
      <h3 class="seccion-titulo">Por etiquetas</h3>
      <div v-if="!resumen.by_tag || resumen.by_tag.length === 0" class="no-data">No hay datos por etiquetas.</div>

      <div v-if="resumen.by_tag && resumen.by_tag.length > 0" class="tags-grid">
        <div v-for="(t, idx) in resumen.by_tag" :key="t.tag || idx" class="tag-card">
          <div class="tag-header">
            <strong class="tag-name">{{ t.tag || 'Sin etiqueta' }}</strong>
            <div class="tag-meta">Respondidas: {{ t.respondidas ?? 0 }}</div>
          </div>

          <div class="tag-canvas-wrap">
            <canvas :ref="el => setTagCanvas(el, idx)" class="tag-chart-canvas"></canvas>
          </div>

          <div class="tag-footer">
            <div>Correctas: <strong>{{ (t.porcentaje_correctas ?? 0) }}%</strong></div>
            <div>Incorrectas: <strong>{{ (100 - (t.porcentaje_correctas ?? 0)).toFixed(1) }}%</strong></div>
          </div>
        </div>
      </div>
    </section>

    <section class="seccion">
      <h3 class="seccion-titulo">Preguntas</h3>
      <div v-if="preguntasList.length === 0" class="no-data">No hay datos por pregunta.</div>

      <ul class="preg-list">
        <li v-for="(p, idx) in preguntasList" :key="p.id" class="preg-item">
          <div class="preg-meta">
            <button class="preg-link nav-btn-small" @click="fetchAndShowBreakdown(p.id)">
              {{ idx+1 }}. {{ trim(p.texto || p.enunciado || 'Pregunta') }}
            </button>
            <span class="porc">{{ (p.porcentaje_correctos ?? 0) }}% correctas</span>
          </div>
        </li>
      </ul>
    </section>

    <div v-if="loadingBreakdown" class="loading">Cargando desglose...</div>

    <div v-if="breakdownData" class="breakdown-area">
      <h4 class="seccion-titulo">Desglose pregunta</h4>
      <p class="break-text">{{ breakdownData.texto }}</p>

      <div class="canvas-wrap">
        <canvas ref="breakCanvas" class="break-canvas"></canvas>
      </div>

      <div class="break-stats">
        <div v-for="(op, i) in breakdownData.opciones" :key="i" class="op-row">
          • <strong>{{ op.texto || ('Opción ' + op.id) }}</strong> — {{ op.porcentaje }} %
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { getResultsSummary, getQuestionBreakdown, fetchEnsayo } from '@/api/ensayos';
import { Chart, registerables } from 'chart.js';
Chart.register(...registerables);

const route = useRoute();
const router = useRouter();
const ensayoId = Number(route.params.id || route.props?.id || route.params?.ensayoId);

const resumen = ref({});
const preguntasList = ref([]);
const loadingSummary = ref(true);
const loadingBreakdown = ref(false);

const breakCanvas = ref(null);
const tagCanvases = ref([]);
const tagCharts = ref([]);

let breakChart = null;

const breakdownData = ref(null);

const MAX_CANVAS_DIM = 32767;
const maxCanvasWidthPx = 900;

function setTagCanvas(el, idx) {
  tagCanvases.value[idx] = el;
}

function safeDestroyChartOnCanvas(canvas) {
  if (!canvas) return;
  try {
    const existing = Chart.getChart(canvas);
    if (existing) existing.destroy();
  } catch (e) {
    console.warn('safeDestroyChartOnCanvas: error destroying chart', e);
  }
}

function replaceCanvasNodeAndUpdateRef(canvasRefArray, idx) {
  const old = canvasRefArray.value[idx];
  if (!old || !old.parentNode) return null;

  const parent = old.parentNode;
  const newCanvas = old.cloneNode(false);
  newCanvas.className = old.className;
  newCanvas.style.cssText = old.style.cssText;

  try {
    
    if (typeof old.replaceWith === 'function') {
      old.replaceWith(newCanvas);
    } else {
      
      old.replaceWith(newCanvas)
    }
  } catch (e) {
    console.warn('replace canvas fallback failed', e);
    return null;
  }

  canvasRefArray.value[idx] = newCanvas;
  return newCanvas;
}


function computeSafeDevicePixelRatioForCanvas(canvas) {
  const cw = Math.max(1, canvas.clientWidth || 1);
  const windowDpr = window.devicePixelRatio || 1;
  const maxDprAllowed = Math.floor(MAX_CANVAS_DIM / cw) || 1;
  return Math.max(1, Math.min(windowDpr, maxDprAllowed, 2));
}

function ensureCanvasHealthyForIndex(canvasRefArray, idx) {
  let canvas = canvasRefArray.value[idx];
  if (!canvas) return null;
  if (canvas.clientWidth === 0) return canvas;
  try {
    const boundedWidth = Math.min(canvas.clientWidth, maxCanvasWidthPx);
    canvas.style.width = boundedWidth + 'px';
    canvas.style.height = '220px';
  } catch (e) {}
  try {
    const existing = Chart.getChart(canvas);
    if (existing) {
      try { existing.destroy(); }
      catch (errDestroy) {
        console.warn('destroy failed, replacing canvas node', errDestroy);
        canvas = replaceCanvasNodeAndUpdateRef(canvasRefArray, idx);
      }
    }
  } catch (ex) {
    console.warn('safe get/destroy failed, replacing canvas', ex);
    canvas = replaceCanvasNodeAndUpdateRef(canvasRefArray, idx);
  }
  return canvasRefArray.value[idx];
}

onMounted(async () => {
  const rol = (localStorage.getItem('rol') || '').toLowerCase();
  if (rol !== 'docente' && !JSON.parse(localStorage.getItem('is_staff') || 'false')) {
    router.push('/acceso-restringido');
    return;
  }
  await loadSummary();
});

onBeforeUnmount(() => {
  try { if (breakChart) breakChart.destroy(); } catch(_) {}
  (tagCharts.value || []).forEach(c => { try { if (c) c.destroy(); } catch(_) {} });
});

async function loadSummary() {
  loadingSummary.value = true;
  try {
    const data = await getResultsSummary(ensayoId);
    resumen.value = data || {};

    if (resumen.value.by_question && Array.isArray(resumen.value.by_question) && resumen.value.by_question.length > 0) {
      preguntasList.value = resumen.value.by_question.map(p => ({
        id: p.pregunta_id,
        texto: p.texto || '',
        tipo: p.tipo || '',
        porcentaje_correctos: p.porcentaje_correctas ?? 0,
        enunciado: p.texto || ''
      }));
    } else {
      try {
        const ensayoFull = await fetchEnsayo(ensayoId);
        if (ensayoFull && Array.isArray(ensayoFull.preguntas) && ensayoFull.preguntas.length > 0) {
          const preguntasBase = ensayoFull.preguntas.map(p => ({
            id: p.id,
            texto: p.enunciado || p.texto || '',
            tipo: p.tipo || '',
            porcentaje_correctos: 0,
            enunciado: p.enunciado || p.texto || ''
          }));
          const promesas = preguntasBase.map(async (p) => {
            try {
              const bd = await getQuestionBreakdown(ensayoId, p.id);
              return { ...p, porcentaje_correctos: bd.porcentaje_correctos ?? 0 };
            } catch (err) {
              console.warn('No breakdown for question', p.id, err);
              return p;
            }
          });
          preguntasList.value = await Promise.all(promesas);
        } else {
          preguntasList.value = [];
        }
      } catch (err) {
        console.warn('No se pudo obtener ensayoFull', err);
        preguntasList.value = [];
      }
    }

    if (Array.isArray(resumen.value.by_tag)) {
      tagCanvases.value = new Array(resumen.value.by_tag.length);
      tagCharts.value = new Array(resumen.value.by_tag.length);
    } else {
      tagCanvases.value = [];
      tagCharts.value = [];
    }

    setTimeout(() => {
      drawAllTagCharts();
    }, 80);

  } catch (err) {
    console.error('Error cargando resumen', err);
    preguntasList.value = [];
  } finally {
    loadingSummary.value = false;
  }
}

function drawAllTagCharts() {
  if (!Array.isArray(resumen.value?.by_tag)) return;
  resumen.value.by_tag.forEach((t, idx) => {
    drawSingleTagChart(t, idx);
  });
}

function drawSingleTagChart(tagObj, idx) {
  const pct = Number(tagObj.porcentaje_correctas ?? 0);
  const correct = isFinite(pct) ? Math.max(0, Math.min(100, pct)) : 0;
  const incorrect = Math.max(0, 100 - correct);

  let canvas = ensureCanvasHealthyForIndex(tagCanvases, idx);
  if (!canvas) return;
  if (canvas.clientWidth === 0 || canvas.clientHeight === 0) return;

  try { if (tagCharts.value[idx]) { tagCharts.value[idx].destroy(); tagCharts.value[idx] = null; } } catch (e) { console.warn('error destruyendo tagCharts[idx]', e); }

  const devicePixelRatio = computeSafeDevicePixelRatioForCanvas(canvas);

  const data = {
    labels: ['Correctas', 'Incorrectas'],
    datasets: [{
      data: [correct, incorrect],
      backgroundColor: ['rgba(46,204,113,0.85)', 'rgba(231,76,60,0.85)'],
      borderColor: ['rgba(255,255,255,0.06)', 'rgba(255,255,255,0.06)'],
      borderWidth: 1
    }]
  };

  try {
    const ctx = canvas.getContext && canvas.getContext('2d');
    if (!ctx) throw new Error('No canvas context for tag');
    tagCharts.value[idx] = new Chart(ctx, {
      type: 'doughnut',
      data,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        devicePixelRatio,
        plugins: { legend: { position: 'bottom' } },
        cutout: '50%'
      }
    });
  } catch (err) {
    console.error('Error creando tagChart idx', idx, err);
  }
}

async function fetchAndShowBreakdown(preguntaId) {
  loadingBreakdown.value = true;
  breakdownData.value = null;
  try {
    const data = await getQuestionBreakdown(ensayoId, preguntaId);
    breakdownData.value = data;
    drawBreakdownChart();
  } catch (err) {
    console.error('Error getting breakdown', err);
    alert('Error al obtener desglose. Revisa consola.');
  } finally {
    loadingBreakdown.value = false;
  }
}

function drawBreakdownChart() {
  const canvas = breakCanvas.value;
  if (!canvas || !breakdownData.value) return;
  if (canvas.clientWidth === 0 || canvas.clientHeight === 0) return;

  try { safeDestroyChartOnCanvas(canvas); } catch(_) {}

  const labels = (breakdownData.value.opciones || []).map(o => o.texto || ('Opción ' + o.id));
  const values = (breakdownData.value.opciones || []).map(o => { const n = Number(o.porcentaje ?? 0); return isFinite(n) ? Math.max(0, Math.min(100, n)) : 0; });

  const devicePixelRatio = computeSafeDevicePixelRatioForCanvas(canvas);

  try {
    const ctx = canvas.getContext && canvas.getContext('2d');
    if (!ctx) throw new Error('No canvas context available for breakChart');

    breakChart = new Chart(ctx, {
      type: 'pie',
      data: { labels, datasets: [{ data: values, backgroundColor: labels.map((_, i) => `rgba(${(80 + i*30)%255}, ${(60 + i*40)%255}, ${(140 + i*10)%255}, 0.8)` ) }] },
      options: { responsive: true, maintainAspectRatio: false, devicePixelRatio, plugins: { legend: { position: 'bottom' } } }
    });
  } catch (err) {
    console.error('Error creando breakChart', err);
  }
}

function trim(s) {
  if (!s) return '';
  return s.length > 120 ? s.slice(0,120) + '...' : s;
}
</script>

<style scoped>

.ensayo-resultados {
  font-family: 'Segoe UI', sans-serif;
  color: white;
  padding: 24px;
  min-height: 60vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 18px;
}

.ensayo-resultados > * {
  width: 100%;
  max-width: 1200px;
  box-sizing: border-box;
}

.header-row {
  display:flex;
  justify-content:space-between;
  align-items:center;
  gap:12px;
}

.titulo {
  font-size: 1.6rem;
  margin: 0;
}

.meta-right { text-align:right; }

.participantes { font-size:0.95rem; opacity:0.95; }


.seccion { width:100%; margin-top: 8px; }
.seccion-titulo { font-size:1.1rem; margin: 8px 0; color: #eaf3ea; }


.tags-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
  width: 100%;
  margin: 12px 0;
}

.tag-card {
  background: rgba(255,255,255,0.03);
  padding: 12px;
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-height: 200px;
  box-shadow: 0 6px 18px rgba(0,0,0,0.16);
}

.tag-header {
  width: 100%;
  display:flex;
  justify-content: space-between;
  align-items:center;
  margin-bottom: 10px;
}

.tag-name { font-size: 0.98rem; color: #f7f7f7; }
.tag-meta { font-size: 0.86rem; opacity: 0.9; color: #dfe6ea; }

.tag-canvas-wrap { width: 100%; display:flex; justify-content:center; align-items:center; }
.tag-chart-canvas {
  width: 100%;
  max-width: 260px;
  height: 160px;
  display: block;
  background: transparent;
  border-radius: 8px;
  box-sizing: border-box;
}


.tag-footer { margin-top: 10px; display:flex; gap:12px; justify-content:space-between; width:100%; font-size: 0.95em; color:#e6f4ea; }


.preg-list { list-style:none; padding:0; margin: 12px 0 0 0; }
.preg-item { margin-bottom: 8px; padding: 10px; border-radius:8px; background: rgba(255,255,255,0.02); display:flex; justify-content:space-between; align-items:center; }
.preg-meta { display:flex; gap:12px; align-items:center; width:100%; justify-content:space-between; }

.preg-link {
  text-align:left;
  background: transparent;
  border: none;
  color: #f0f0f0;
  cursor: pointer;
  font-weight: 600;
  padding: 8px 10px;
  border-radius: 6px;
}

.nav-btn-small {
  background-color: #f4f4f4;
  color: #2c3e50;
  padding: 6px 10px;
  border-radius: 8px;
  border: 1px solid #ccc;
}
.nav-btn-small:hover { background:#e0e0e0; }


.porc { font-weight:700; color:#e6f4ea; }


.breakdown-area { margin-top: 18px; padding: 14px; background: rgba(0,0,0,0.25); border-radius:10px; width:100%; box-sizing:border-box; }
.break-text { opacity: 0.95; margin-bottom: 8px; color: #eef6ee; }


.canvas-wrap, .tag-canvas-wrap { display:flex; justify-content:center; width:100%; }
.break-canvas {
  width: 100%;
  max-width: 1100px;
  height: 320px;
  display: block;
  margin: 12px 0;
  background: rgba(255,255,255,0.02);
  border-radius: 8px;
  box-sizing: border-box;
  max-height: 420px;
}


.loading { opacity: 0.85; margin: 8px 0; color: #dfeff0; }
.no-data { opacity: 0.85; margin: 8px 0; color: #dfe6ea; text-align:center; }


.break-stats { margin-top: 8px; display:flex; flex-direction:column; gap:6px; color: #dfe6ea; }
.op-row { font-size: 0.95rem; }


@media (max-width: 720px) {
  .tag-chart-canvas { max-width: 200px; height: 140px; }
  .break-canvas { height: 260px; }
  .ensayo-resultados { padding: 16px; }
}
</style>
