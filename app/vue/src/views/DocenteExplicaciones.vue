
<template>
  <div class="docente-explicaciones">
    <h2>Editar explicaciones — Docente</h2>

    <div v-if="!isDocente" class="forbidden">
      Acceso denegado. Se necesita rol docente.
    </div>

    <div v-else>
      <div class="selector-ensayo">
        <label>Seleccionar ensayo:
          <select v-model="selectedEnsayoId" @change="onChangeEnsayo">
            <option value="">-- elige un ensayo --</option>
            <option v-for="e in ensayos" :key="e.id" :value="e.id">
              {{ e.title || e.titulo || e.name || ('Ensayo ' + e.id) }}
            </option>
          </select>
        </label>
      </div>

      <div v-if="loading" class="loading">Cargando...</div>

      <div v-if="summary && summary.by_question">
        <h3>Preguntas de: {{ summary.titulo }}</h3>
        <ul class="preg-list">
          <li v-for="q in preguntas" :key="q.pregunta_id" class="preg-item">
            <div class="preg-enunciado">{{ limit(q.texto || q.enunciado, 180) }}</div>

            <div class="exp-editor">
              <label>Explicación (texto)</label>
              <textarea v-model="q.edit_explicacion_texto" rows="3"></textarea>

              <label>Explicación (URL)</label>
              <input v-model="q.edit_explicacion_url" placeholder="https://..." />

              <div class="actions">
                <button @click="guardar(q)" :disabled="q.saving">Guardar</button>
                <span v-if="q.saving">Guardando...</span>
                <span v-if="q.saved" class="ok">Guardado ✓</span>
                <span v-if="q.error" class="err">Error</span>
              </div>

              <div class="current">
                <strong>Actual:</strong>
                <div v-if="q.explicacion_texto">{{ q.explicacion_texto }}</div>
                <div v-if="q.explicacion_url">URL: <a :href="q.explicacion_url" target="_blank">{{ q.explicacion_url }}</a></div>
                <div v-if="!q.explicacion_texto && !q.explicacion_url">Sin explicación</div>
              </div>
            </div>
          </li>
        </ul>
      </div>

      <div v-if="!loading && (!summary || (summary.by_question && summary.by_question.length === 0))">
        <p>No hay preguntas o explicaciones para este ensayo.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { fetchAllEnsayos, getResultsSummary, editarExplicacion } from '@/api/ensayos';
import { useRouter } from 'vue-router';

const router = useRouter();
const ensayos = ref([]);
const selectedEnsayoId = ref('');
const loading = ref(false);
const summary = ref(null);
const preguntas = ref([]);

const isDocente = ((localStorage.getItem('rol') || '').toLowerCase() === 'docente') || JSON.parse(localStorage.getItem('is_staff') || 'false');

onMounted(async () => {
  if (!localStorage.getItem('token')) {
    router.push('/acceso-restringido');
    return;
  }
  if (!isDocente) return;
  try {
    const data = await fetchAllEnsayos();

    ensayos.value = Array.isArray(data) ? data : (data.results || []);
  } catch (err) {
    console.error('Error cargando ensayos', err);
  }
});

async function onChangeEnsayo() {
  if (!selectedEnsayoId.value) {
    summary.value = null;
    preguntas.value = [];
    return;
  }
  loading.value = true;
  try {
    const s = await getResultsSummary(selectedEnsayoId.value);
    summary.value = s;
    
    preguntas.value = (s.by_question || []).map(q => ({
      pregunta_id: q.pregunta_id,
      texto: q.texto || q.enunciado || '',
      explicacion_texto: q.explicacion_texto || '',
      explicacion_url: q.explicacion_url || '',
      edit_explicacion_texto: q.explicacion_texto || '',
      edit_explicacion_url: q.explicacion_url || '',
      saving: false,
      saved: false,
      error: null
    }));
  } catch (err) {
    console.error('Error cargando summary', err);
    summary.value = null;
    preguntas.value = [];
  } finally {
    loading.value = false;
  }
}

async function guardar(q) {
  q.saving = true;
  q.saved = false;
  q.error = null;
  try {
    const payload = {
      texto: q.edit_explicacion_texto || null,
      url: q.edit_explicacion_url || null
    };

    const res = await editarExplicacion(q.pregunta_id, payload);

    q.explicacion_texto = res.explicacion_texto ?? q.edit_explicacion_texto;
    q.explicacion_url = res.explicacion_url ?? q.edit_explicacion_url;
    q.saved = true;
    setTimeout(() => q.saved = false, 2000);
  } catch (err) {
    console.error('Error guardando explicación', err);
    q.error = true;
  } finally {
    q.saving = false;
  }
}

function limit(s, n=140) {
  return s && s.length>n ? s.slice(0,n)+'...' : (s||'');
}
</script>

<style scoped>
.docente-explicaciones { color: white; padding: 20px; min-height: 60vh; }
.selector-ensayo { margin-bottom: 20px; }
.preg-list { list-style:none; padding:0; margin:0; display:flex; flex-direction:column; gap:14px; }
.preg-item { background: rgba(255,255,255,0.03); padding:12px; border-radius:8px; }
.preg-enunciado { font-weight:700; margin-bottom:8px; }
.exp-editor textarea { width:100%; min-height:60px; padding:8px; border-radius:6px; }
.exp-editor input { width:100%; padding:8px; border-radius:6px; margin-top:6px; }
.actions { margin-top:8px; display:flex; gap:8px; align-items:center; }
.actions button { background:#3498db; color:white; border:none; padding:8px 12px; border-radius:6px; cursor:pointer; }
.actions .ok { color:#2ecc71; margin-left:8px; }
.actions .err { color:#e74c3c; margin-left:8px; }
.current { margin-top:10px; opacity:0.9; font-size:0.95em; }
</style>
