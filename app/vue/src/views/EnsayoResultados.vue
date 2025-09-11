<template>
  <div class="ensayo-resultados">
    <h2>Resultados — {{ resumen.titulo || ('Ensayo ' + ensayoId) }}</h2>
    <p v-if="resumen.total_participantes !== undefined">Participantes: {{ resumen.total_participantes }}</p>

    <div class="controls">
      <label>Tipo de gráfico:
        <select v-model="chartType">
          <option value="bar">Barras</option>
          <option value="pie">Torta</option>
        </select>
      </label>
    </div>

    <div v-if="loadingSummary" class="loading">Cargando resumen...</div>

    <div class="canvas-wrap">
      <canvas v-if="!loadingSummary" ref="summaryCanvas" class="summary-canvas"></canvas>
    </div>

    <h3>Por etiquetas</h3>
    <div v-if="!resumen.by_tag || resumen.by_tag.length === 0" class="no-data">No hay datos por etiquetas.</div>
    <div class="canvas-wrap">
      <canvas v-if="resumen.by_tag && resumen.by_tag.length > 0" ref="tagCanvas" class="tag-canvas"></canvas>
    </div>

    <h3>Preguntas</h3>
    <div v-if="preguntasList.length === 0" class="no-data">No hay datos por tipo.</div>

    <ul class="preg-list">
      <li v-for="(p, idx) in preguntasList" :key="p.id" class="preg-item">
        <div class="preg-meta">
          <button class="preg-link" @click="fetchAndShowBreakdown(p.id)">
            {{ idx+1 }}. {{ trim(p.texto || p.enunciado || 'Pregunta') }}
          </button>
          <span class="porc">{{ (p.porcentaje_correctos ?? 0) }}% correctas</span>
        </div>
      </li>
    </ul>

    <div v-if="loadingBreakdown" class="loading">Cargando desglose...</div>

    <div v-if="breakdownData" class="breakdown-area">
      <h4>Desglose pregunta</h4>
      <p class="break-text">{{ breakdownData.texto }}</p>
      <div class="canvas-wrap">
        <canvas ref="breakCanvas" class="break-canvas"></canvas>
      </div>
      <div class="break-stats">
        <div v-for="(op, i) in breakdownData.opciones" :key="i">
          • {{ op.texto || ('Opción ' + op.id) }} — {{ op.porcentaje }} %
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onBeforeUnmount } from 'vue';
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

const summaryCanvas = ref(null);
const breakCanvas = ref(null);
const tagCanvas = ref(null);

let summaryChart = null;
let breakChart = null;
let tagChart = null;

const chartType = ref('bar');
const breakdownData = ref(null);

// parámetros de seguridad
const MAX_CANVAS_DIM = 32767; // límite obligatorio
const maxCanvasWidthPx = 1100; // ancho máximo visual en px para el canvas (ajustable)

// ---- helpers robustos ----
function safeDestroyChartOnCanvas(canvas) {
  if (!canvas) return;
  try {
    const existing = Chart.getChart(canvas);
    if (existing) existing.destroy();
  } catch (e) {
    // si destroy falla debido a canvas en estado de error, intentamos reemplazar el canvas
    console.warn('safeDestroyChartOnCanvas: error destroying chart', e);
  }
}

function replaceCanvasNodeAndUpdateRef(canvasRef) {
  // canvasRef es la ref reactive (summaryCanvas, tagCanvas o breakCanvas)
  const old = canvasRef.value;
  if (!old || !old.parentNode) return canvasRef.value;
  const parent = old.parentNode;
  const newCanvas = old.cloneNode(false); // no children
  // copiar clases/atributos visuales
  newCanvas.className = old.className;
  newCanvas.style.cssText = old.style.cssText;
  parent.replaceChild(newCanvas, old);
  canvasRef.value = newCanvas;
  return newCanvas;
}

function computeSafeDevicePixelRatioForCanvas(canvas) {
  const cw = Math.max(1, canvas.clientWidth || 1);
  const windowDpr = window.devicePixelRatio || 1;
  const maxDprAllowed = Math.floor(MAX_CANVAS_DIM / cw) || 1;
  // limitamos por seguridad entre 1 y 2 (ajustable)
  return Math.max(1, Math.min(windowDpr, maxDprAllowed, 2));
}

function ensureCanvasHealthy(canvasRef) {
  // Garantiza que el canvas asociado a la ref esté en estado utilizable.
  let canvas = canvasRef.value;
  if (!canvas) return null;

  // Si clientWidth = 0 (no visible) no intentamos forzar nada
  if (canvas.clientWidth === 0) return canvas;

  // forzamos un ancho visual máximo para que clientWidth no crezca infinito
  try {
    const boundedWidth = Math.min(canvas.clientWidth, maxCanvasWidthPx);
    canvas.style.width = boundedWidth + 'px';
    // alto fijo (si quieres responsive vertical, ajusta aquí)
    canvas.style.height = '320px';
  } catch (e) {
    // ignore
  }

  // intentar destruir chart existente de forma segura
  try {
    const existing = Chart.getChart(canvas);
    if (existing) {
      try {
        existing.destroy();
      } catch (errDestroy) {
        // si destroy falla porque canvas está en error state -> reemplazar canvas
        console.warn('destroy failed, replacing canvas node', errDestroy);
        canvas = replaceCanvasNodeAndUpdateRef(canvasRef);
      }
    }
  } catch (ex) {
    // si Chart.getChart o destroy lanza excepción -> reemplazamos canvas
    console.warn('safe destroy/getChart failed, replacing canvas', ex);
    canvas = replaceCanvasNodeAndUpdateRef(canvasRef);
  }

  return canvasRef.value;
}

// ---- lifecycle ----
onMounted(async () => {
  const rol = (localStorage.getItem('rol') || '').toLowerCase();
  if (rol !== 'docente' && !JSON.parse(localStorage.getItem('is_staff') || 'false')) {
    router.push('/acceso-restringido');
    return;
  }
  await loadSummary();
});

onBeforeUnmount(() => {
  try { if (summaryChart) summaryChart.destroy(); } catch(_) {}
  try { if (breakChart) breakChart.destroy(); } catch(_) {}
  try { if (tagChart) tagChart.destroy(); } catch(_) {}
});

watch(chartType, () => {
  drawSummaryChart();
  drawTagChart();
});

// ---- main logic ----
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

    // dibujar gráficos
    drawSummaryChart();
    drawTagChart();
  } catch (err) {
    console.error('Error cargando resumen', err);
    preguntasList.value = [];
  } finally {
    loadingSummary.value = false;
  }
}

function drawSummaryChart() {
  // obtenemos un canvas sano y acotado
  let canvas = ensureCanvasHealthy(summaryCanvas);
  if (!canvas) return;
  // si invisible o sin tamaño evadir
  if (canvas.clientWidth === 0 || canvas.clientHeight === 0) return;
  if (!resumen.value?.by_type) return;

  const labels = resumen.value.by_type.map(b => b.tipo || 'sin tipo');
  const values = resumen.value.by_type.map(b => {
    const v = Number(b.porcentaje_correctas ?? 0);
    return isFinite(v) ? Math.max(0, Math.min(100, v)) : 0;
  });

  // después de asegurar canvas, volvemos a intentar destruir cualquier chart atado
  safeDestroyChartOnCanvas(canvas);

  const devicePixelRatio = computeSafeDevicePixelRatioForCanvas(canvas);

  const config = {
    type: chartType.value === 'bar' ? 'bar' : 'pie',
    data: {
      labels,
      datasets: [{
        label: '% respuestas correctas',
        data: values,
        backgroundColor: labels.map((_, i) => `rgba(${(50 + (i*40)) % 255}, ${(100 + (i*30)) % 255}, ${(150 + (i*20)) % 255}, 0.7)`),
        borderColor: 'rgba(255,255,255,0.08)',
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      devicePixelRatio,
      plugins: { legend: { display: chartType.value === 'pie' } },
      scales: chartType.value === 'bar' ? { y: { beginAtZero: true, max: 100 } } : {}
    }
  };

  try {
    const ctx = canvas.getContext && canvas.getContext('2d');
    if (!ctx) throw new Error('No canvas context available');
    summaryChart = new Chart(ctx, config);
  } catch (err) {
    console.error('Error creando summaryChart', err);
  }
}

function drawTagChart() {
  let canvas = ensureCanvasHealthy(tagCanvas);
  if (!canvas) return;
  if (canvas.clientWidth === 0 || canvas.clientHeight === 0) return;

  const data = resumen.value?.by_tag;
  if (!Array.isArray(data) || data.length === 0) {
    safeDestroyChartOnCanvas(canvas);
    tagChart = null;
    return;
  }

  const labels = data.map(t => t.tag || 'Sin etiqueta');
  const rawValues = data.map(t => Number(t.porcentaje_correctas ?? 0));
  const values = rawValues.map(v => (isFinite(v) ? Math.max(0, Math.min(100, v)) : 0));

  safeDestroyChartOnCanvas(canvas);
  const devicePixelRatio = computeSafeDevicePixelRatioForCanvas(canvas);

  try {
    const ctx = canvas.getContext && canvas.getContext('2d');
    if (!ctx) throw new Error('No canvas context available for tagChart');

    tagChart = new Chart(ctx, {
      type: chartType.value === 'pie' ? 'pie' : 'bar',
      data: {
        labels,
        datasets: [{
          label: '% correctas por etiqueta',
          data: values,
          backgroundColor: labels.map((_, i) => `rgba(${(80 + i*30)%255}, ${(60 + i*40)%255}, ${(140 + i*10)%255}, 0.8)`),
          borderColor: 'rgba(0,0,0,0.06)',
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        devicePixelRatio,
        scales: chartType.value === 'bar' ? { y: { beginAtZero: true, max: 100 } } : {}
      }
    });
  } catch (err) {
    console.error('Error creando tagChart', err);
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
  let canvas = ensureCanvasHealthy(breakCanvas);
  if (!canvas) return;
  if (canvas.clientWidth === 0 || canvas.clientHeight === 0) return;
  if (!breakdownData.value) return;

  safeDestroyChartOnCanvas(canvas);

  const labels = (breakdownData.value.opciones || []).map(o => o.texto || ('Opción ' + o.id));
  const values = (breakdownData.value.opciones || []).map(o => {
    const n = Number(o.porcentaje ?? 0);
    return isFinite(n) ? Math.max(0, Math.min(100, n)) : 0;
  });

  const devicePixelRatio = computeSafeDevicePixelRatioForCanvas(canvas);

  try {
    const ctx = canvas.getContext && canvas.getContext('2d');
    if (!ctx) throw new Error('No canvas context available for breakChart');

    breakChart = new Chart(ctx, {
      type: 'pie',
      data: {
        labels,
        datasets: [{ data: values, backgroundColor: labels.map((_, i) => `rgba(${(80 + i*30)%255}, ${(60 + i*40)%255}, ${(140 + i*10)%255}, 0.8)`) }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        devicePixelRatio,
        plugins: { legend: { position: 'bottom' } }
      }
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
  color: white;
  padding: 24px;
  min-height: 60vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.ensayo-resultados > * {
  width: 100%;
  max-width: 1200px;
  box-sizing: border-box;
}

.controls { margin: 12px 0; }

.canvas-wrap {
  display: flex;
  justify-content: center;
  width: 100%;
}

.summary-canvas, .break-canvas, .tag-canvas {
  width: 100%;
  max-width: 1100px; /* importante: evita que canvas crezca demasiado */
  height: 320px;
  display: block;
  margin: 12px 0;
  background: rgba(255,255,255,0.02);
  border-radius: 8px;
  box-sizing: border-box;
}

.loading { opacity: 0.85; margin: 8px 0; }
.preg-list { list-style:none; padding:0; margin: 12px 0 0 0; }
.preg-item { margin-bottom: 8px; padding: 8px; border-radius:6px; background: rgba(255,255,255,0.02); display:flex; justify-content:space-between; align-items:center; }
.preg-meta { display:flex; gap:12px; align-items:center; width:100%; justify-content:space-between; }
.preg-link { text-align:left; background:transparent; border:none; color: #f0f0f0; cursor:pointer; font-weight: 500; padding:0; }
.porc { font-weight:700; color:#e6f4ea; }
.breakdown-area { margin-top: 14px; padding: 12px; background: rgba(0,0,0,0.25); border-radius:8px; }
.break-text { opacity: 0.9; margin-bottom: 8px; }
.no-data { opacity: 0.8; margin: 8px 0; text-align: center; }
</style>
