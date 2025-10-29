<template>
  <div class="docente-explicaciones">
    <div class="header-row">
      <h2 class="titulo">Editar explicaciones — Docente</h2>
    </div>

    <div v-if="!isDocente" class="forbidden">
      Acceso denegado. Se necesita rol docente.
    </div>

    <div v-else>
      <div class="selector-ensayo">
        <label>
          <span>Seleccionar ensayo:</span>
          <select v-model="selectedEnsayoId" @change="onChangeEnsayo" class="select-input">
            <option value="">-- elige un ensayo --</option>
            <option v-for="e in ensayos" :key="e.id" :value="e.id">
              {{ e.title || e.titulo || e.name || ('Ensayo ' + e.id) }}
            </option>
          </select>
        </label>
      </div>

      <div v-if="loading" class="loading">Cargando...</div>

      <div v-if="summary && summary.by_question">
        <h3 class="subtitulo">Preguntas de: {{ summary.titulo }}</h3>

        <ul class="preg-list">
          <li v-for="q in preguntas" :key="q.pregunta_id" class="preg-item">
            <div class="preg-enunciado">{{ limit(q.texto || q.enunciado, 180) }}</div>

            <div class="exp-editor">
              <label class="lbl">Explicación (texto)</label>
              <textarea v-model="q.edit_explicacion_texto" rows="3" class="txt-area"></textarea>

              <label class="lbl">Explicación (URL)</label>
              <input v-model="q.edit_explicacion_url" placeholder="https://..." class="txt-input" />

              <div class="actions">
                <button class="save-btn" @click="guardar(q)" :disabled="q.saving">
                  <span v-if="!q.saving">Guardar</span>
                  <span v-else>Guardando...</span>
                </button>

                <span v-if="q.saved" class="ok">Guardado ✓</span>
                <span v-if="q.error" class="err">Error</span>
              </div>

              <div class="current">
                <strong>Actual:</strong>
                <div v-if="q.explicacion_texto">{{ q.explicacion_texto }}</div>
                <div v-if="q.explicacion_url">
                  URL: <a :href="q.explicacion_url" target="_blank">{{ q.explicacion_url }}</a>
                </div>
                <div v-if="!q.explicacion_texto && !q.explicacion_url" class="sin-exp">
                  Sin explicación
                </div>
              </div>
            </div>
          </li>
        </ul>
      </div>

      <div v-if="!loading && (!summary || (summary.by_question && summary.by_question.length === 0))" class="no-data">
        No hay preguntas o explicaciones para este ensayo.
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

const isDocente = ((localStorage.getItem('rol') || '').toLowerCase() === 'docente') ||
  JSON.parse(localStorage.getItem('is_staff') || 'false');

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
    setTimeout(() => (q.saved = false), 2000);
  } catch (err) {
    console.error('Error guardando explicación', err);
    q.error = true;
  } finally {
    q.saving = false;
  }
}

function limit(s, n = 140) {
  return s && s.length > n ? s.slice(0, n) + '...' : s || '';
}
</script>

<style scoped>
.docente-explicaciones {
  font-family: 'Segoe UI', sans-serif;
  color: white;
  padding: 24px;
  min-height: 70vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 18px;
}

.header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  max-width: 1000px;
}

.titulo {
  font-size: 1.6rem;
  font-weight: 600;
  margin: 0;
}

.selector-ensayo {
  margin-top: 12px;
  width: 100%;
  max-width: 600px;
  font-family: 'Segoe UI', sans-serif;
  
}

.select-input {
  font-family: 'Segoe UI', sans-serif;
  background: rgba(255,255,255,0.08);
  color: black;
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: 6px;
  padding: 6px 8px;
  margin-left: 6px;
  cursor: pointer;
}

.select-input:hover {
  background: rgba(255,255,255,0.15);
  font-family: 'Segoe UI', sans-serif;
}

.loading { opacity: 0.85; margin: 10px 0; color: #dfeff0; }
.no-data { opacity: 0.8; margin: 12px 0; text-align: center; }

.subtitulo {
  font-size: 1.2rem;
  margin: 16px 0 10px 0;
  color: #eaf3ea;
}


.preg-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 14px;
  width: 100%;
  max-width: 1000px;
}

.preg-item {
  background: rgba(255,255,255,0.03);
  padding: 16px;
  border-radius: 10px;
  box-shadow: 0 4px 10px rgba(0,0,0,0.2);
}

.preg-enunciado {
  font-weight: 600;
  margin-bottom: 10px;
  color: #f8f8f8;
}

.lbl {
  font-weight: 500;
  margin-top: 6px;
  display: block;
  color: #dfeff0;
}

.txt-area, .txt-input {
  width: 100%;
  border-radius: 8px;
  border: 1px solid rgba(255,255,255,0.15);
  background: rgba(255,255,255,0.06);
  color: #f7f7f7;
  padding: 8px;
  margin-top: 4px;
  font-family: inherit;
  box-sizing: border-box;
}

.txt-area:focus, .txt-input:focus {
  outline: none;
  border-color: #4dd0e1;
  background: rgba(255,255,255,0.1);
}


.actions {
  margin-top: 10px;
  display: flex;
  gap: 10px;
  align-items: center;
}

.save-btn {
  background: #f4f4f4;
  color: #2c3e50;
  border: none;
  padding: 8px 14px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
}

.save-btn:hover {
  background: #e0e0e0;
}

.save-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.ok { color: #2ecc71; font-weight: 600; }
.err { color: #e74c3c; font-weight: 600; }


.current {
  margin-top: 10px;
  padding-top: 8px;
  border-top: 1px solid rgba(255,255,255,0.1);
  font-size: 0.95em;
  color: #dfe6ea;
}

.sin-exp {
  opacity: 0.8;
  font-style: italic;
}

a {
  color: #82d8f7;
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}


@media (max-width: 720px) {
  .preg-item { padding: 12px; }
  .titulo { font-size: 1.4rem; }
}
</style>
