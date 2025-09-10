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

    <canvas v-if="!loadingSummary" ref="summaryCanvas" class="summary-canvas"></canvas>

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
      <canvas ref="breakCanvas" class="break-canvas"></canvas>
      <div class="break-stats">
        <div v-for="(op, i) in breakdownData.opciones" :key="i">
          • {{ op.texto || ('Opción ' + op.id) }} — {{ op.porcentaje }} %
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
/* EnsayoResultados.vue
   - Usa getResultsSummary, getQuestionBreakdown, fetchEnsayo desde src/api/ensayos.js
   - Dibuja gráficos con chart.js
*/

import { ref, onMounted, watch, onBeforeUnmount } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { getResultsSummary, getQuestionBreakdown, fetchEnsayo } from '@/api/ensayos';
import { Chart, registerables } from 'chart.js';
Chart.register(...registerables);

const route = useRoute();
const router = useRouter();
const ensayoId = Number(route.params.id || route.props?.id || route.params?.ensayoId);

const resumen = ref({});
const preguntasList = ref([]); // { id, texto, tipo, porcentaje_correctos }
const loadingSummary = ref(true);
const loadingBreakdown = ref(false);

const summaryCanvas = ref(null);
const breakCanvas = ref(null);
let summaryChart = null;
let breakChart = null;

const chartType = ref('bar');
const breakdownData = ref(null);

onMounted(async () => {
  // protección básica por rol (asume localStorage.rol o is_staff)
  const rol = (localStorage.getItem('rol') || '').toLowerCase();
  if (rol !== 'docente' && !JSON.parse(localStorage.getItem('is_staff') || 'false')) {
    router.push('/acceso-restringido');
    return;
  }
  await loadSummary();
});

onBeforeUnmount(() => {
  if (summaryChart) {
    try { summaryChart.destroy(); } catch(e) { /* ignore */ }
  }
  if (breakChart) {
    try { breakChart.destroy(); } catch(e) { /* ignore */ }
  }
});

// redraw summary when chart type changes
watch(chartType, () => {
  drawSummaryChart();
});

async function loadSummary() {
  loadingSummary.value = true;
  try {
    const data = await getResultsSummary(ensayoId);
    resumen.value = data || {};

    // Preferir by_question si backend lo devuelve
    if (resumen.value.by_question && Array.isArray(resumen.value.by_question) && resumen.value.by_question.length > 0) {
      preguntasList.value = resumen.value.by_question.map(p => ({
        id: p.pregunta_id,
        texto: p.texto || '',
        tipo: p.tipo || '',
        porcentaje_correctos: p.porcentaje_correctas ?? 0,
        enunciado: p.texto || ''
      }));
    } else {
      // Fallback: obtener preguntas desde fetchEnsayo y pedir breakdown por pregunta
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

          // Pedir breakdown para cada pregunta en paralelo (optimizable)
          const promesas = preguntasBase.map(async (p) => {
            try {
              const bd = await getQuestionBreakdown(ensayoId, p.id);
              return { ...p, porcentaje_correctos: bd.porcentaje_correctos ?? 0 };
            } catch (err) {
              // si falla por alguna pregunta, devolvemos la pregunta sin porcentaje
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

    // Dibuja gráfico resumen por tipo
    drawSummaryChart();
  } catch (err) {
    console.error('Error cargando resumen', err);
    preguntasList.value = [];
  } finally {
    loadingSummary.value = false;
  }
}

function drawSummaryChart() {
  const canvas = summaryCanvas.value;
  if (!canvas || !resumen.value.by_type) return;

  const labels = resumen.value.by_type.map(b => b.tipo || 'sin tipo');
  const values = resumen.value.by_type.map(b => b.porcentaje_correctas ?? b.porcentaje_correctas ?? 0);

  if (summaryChart) summaryChart.destroy();

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
      plugins: {
        legend: { display: chartType.value === 'pie' }
      },
      scales: chartType.value === 'bar' ? {
        y: { beginAtZero: true, max: 100 }
      } : {}
    }
  };

  // crear chart
  try {
    summaryChart = new Chart(canvas.getContext('2d'), config);
  } catch (err) {
    console.error('Error creando summaryChart', err);
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

  if (breakChart) breakChart.destroy();

  const labels = (breakdownData.value.opciones || []).map(o => o.texto || ('Opción ' + o.id));
  const values = (breakdownData.value.opciones || []).map(o => o.porcentaje ?? 0);

  try {
    breakChart = new Chart(canvas.getContext('2d'), {
      type: 'pie',
      data: {
        labels,
        datasets: [{ data: values, backgroundColor: labels.map((_, i) => `rgba(${(80 + i*30)%255}, ${(60 + i*40)%255}, ${(140 + i*10)%255}, 0.8)`) }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
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
.ensayo-resultados { color: white; padding: 24px; min-height: 60vh; }
.controls { margin: 12px 0; }
.summary-canvas, .break-canvas { width: 100%; height: 320px; display:block; margin: 12px 0; background: rgba(255,255,255,0.02); border-radius: 8px; }
.loading { opacity: 0.85; margin: 8px 0; }
.preg-list { list-style:none; padding:0; margin: 12px 0 0 0; }
.preg-item { margin-bottom: 8px; padding: 8px; border-radius:6px; background: rgba(255,255,255,0.02); display:flex; justify-content:space-between; align-items:center; }
.preg-meta { display:flex; gap:12px; align-items:center; width:100%; justify-content:space-between; }
.preg-link { text-align:left; background:transparent; border:none; color: #f0f0f0; cursor:pointer; font-weight: 500; padding:0; }
.porc { font-weight:700; color:#e6f4ea; }
.breakdown-area { margin-top: 14px; padding: 12px; background: rgba(0,0,0,0.25); border-radius:8px; }
.break-text { opacity: 0.9; margin-bottom: 8px; }
.no-data { opacity: 0.8; margin: 8px 0; }
</style>
