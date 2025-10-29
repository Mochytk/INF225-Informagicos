<template>
  <div class="revision-ensayo">
    <div class="header-row">
      <h2 class="titulo">Revisión — {{ resumen.titulo || ('Ensayo ' + ensayoId) }}</h2>
    </div>

    <div class="controls">
      <label class="lbl-filter">Filtrar:
        <select v-model="filtro" class="select-input">
          <option value="all">Todas</option>
          <option value="correct">Solo correctas</option>
          <option value="incorrect">Solo incorrectas</option>
        </select>
      </label>
    </div>

    <div v-if="loading" class="loading">Cargando revisión...</div>

    <ul v-else class="preg-list">
      <li v-for="q in filteredQuestions" :key="q.pregunta_id" :class="['preg-item', q.correcta ? 'ok' : 'ko']">
        <div class="preg-header">
          <div class="enunciado">{{ q.enunciado }}</div>
          <div class="status" :class="q.correcta ? 'stat-ok' : 'stat-ko'">{{ q.correcta ? 'Correcta' : 'Incorrecta' }}</div>
        </div>

        <div class="respuesta">
          <strong>Tu respuesta:</strong>
          <span v-if="q.opcion_elegida_texto && q.opcion_elegida_texto.trim() !== ''">
            {{ q.opcion_elegida_texto }}
          </span>
          <span v-else class="muted">Sin respuesta</span>
        </div>

        <ul v-if="q.all_options && q.all_options.length" class="opciones-list">
          <li v-for="op in q.all_options" :key="op.id" class="op-item">
            <span :class="{
                'op-correct': op.id === q.correct_option_id,
                'op-selected': op.id === q.opcion_elegida_id
              }">
              {{ op.texto }}
            </span>
            <small v-if="op.id === q.correct_option_id" class="note"> — Respuesta correcta</small>
            <small v-if="op.id === q.opcion_elegida_id" class="note"> — Elegida</small>
          </li>
        </ul>

        <div class="acciones">
          <button class="btn" @click="toggleExp(q.pregunta_id)">
            {{ openExp === q.pregunta_id ? 'Ocultar explicación' : 'Ver explicación' }}
          </button>

          <button v-if="esDocente" class="btn ghost" @click="toggleEditMode(q)">
            {{ editarMode === q.pregunta_id ? 'Cancelar' : 'Editar explicación' }}
          </button>
        </div>

        <div v-if="openExp === q.pregunta_id" class="explicacion">
          <p v-if="q.correct_option_text"><strong>Respuesta correcta:</strong> {{ q.correct_option_text }}</p>

          <p v-if="q.explicacion_texto"><strong>Explicación:</strong> {{ q.explicacion_texto }}</p>
          <p v-if="q.explicacion_url">Recurso: <a :href="q.explicacion_url" target="_blank" rel="noopener">{{ q.explicacion_url }}</a></p>
          <p v-if="!q.explicacion_texto && !q.explicacion_url && !q.correct_option_text" class="muted">No hay explicación disponible.</p>
        </div>

        <div v-if="editarMode === q.pregunta_id" class="editor">
          <label class="lbl">Explicación (texto)</label>
          <textarea v-model="editText" rows="4" class="txt-area"></textarea>

          <label class="lbl">Explicación (URL)</label>
          <input v-model="editUrl" placeholder="https://..." class="txt-input" />

          <div class="editor-actions">
            <button class="save-btn" :disabled="saving" @click="guardarExplicacion(q.pregunta_id)">
              <span v-if="!saving">Guardar</span>
              <span v-else>Guardando...</span>
            </button>
            <button class="btn ghost" @click="cancelEdit">Cancelar</button>
            <span v-if="saved" class="ok">Guardado ✓</span>
            <span v-if="error" class="err">Error</span>
          </div>
        </div>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { getRevision, editarExplicacion } from '@/api/ensayos';

const route = useRoute();
const router = useRouter();
const ensayoId = Number(route.params.ensayoId);
const resultadoId = Number(route.params.resultadoId);

const resumen = ref({});
const preguntas = ref([]);
const loading = ref(false);

const filtro = ref('all');
const openExp = ref(null);
const editarMode = ref(null);
const editText = ref('');
const editUrl = ref('');

const saving = ref(false);
const saved = ref(false);
const error = ref(false);

const esDocente = ((localStorage.getItem('rol') || '').toLowerCase() === 'docente') || JSON.parse(localStorage.getItem('is_staff') || 'false');

const filteredQuestions = computed(() => {
  if (filtro.value === 'all') return preguntas.value;
  if (filtro.value === 'correct') return preguntas.value.filter(p => p.correcta);
  return preguntas.value.filter(p => !p.correcta);
});

function toggleExp(preguntaId) {
  openExp.value = openExp.value === preguntaId ? null : preguntaId;
}

function cancelEdit() {
  editarMode.value = null;
  editText.value = '';
  editUrl.value = '';
  saving.value = false;
  saved.value = false;
  error.value = false;
}

function toggleEditMode(q) {
  if (editarMode.value === q.pregunta_id) {
    cancelEdit();
    return;
  }
  editarMode.value = q.pregunta_id;
  editText.value = q.explicacion_texto || '';
  editUrl.value = q.explicacion_url || '';
  saved.value = false;
  error.value = false;
}

async function guardarExplicacion(preguntaId) {
  saving.value = true;
  saved.value = false;
  error.value = false;
  try {
    const payload = { texto: editText.value || null, url: editUrl.value || null };
    const res = await editarExplicacion(preguntaId, payload); // usa la función centralizada en api/ensayos
    // actualizar copia local
    const q = preguntas.value.find(x => x.pregunta_id === preguntaId);
    if (q) {
      q.explicacion_texto = res.explicacion_texto ?? editText.value;
      q.explicacion_url = res.explicacion_url ?? editUrl.value;
    }
    saved.value = true;
    setTimeout(() => saved.value = false, 2000);
    cancelEdit();
  } catch (err) {
    console.error('Error guardando explicación', err);
    error.value = true;
  } finally {
    saving.value = false;
  }
}

async function load() {
  loading.value = true;
  try {
    const data = await getRevision(ensayoId, resultadoId);
    resumen.value = { titulo: data.ensayo_titulo || data.titulo || '' };

    const raw = data.preguntas || [];
    preguntas.value = raw.map(p => {
   
      return {
        pregunta_id: p.pregunta_id ?? p.id,
        enunciado: p.enunciado ?? p.texto ?? p.question_text ?? '',
        tipo: p.tipo ?? '',
        opcion_elegida_texto: (p.opcion_elegida_texto ?? p.opcion_texto ?? p.texto_alumno ?? '') || '',
        opcion_elegida_id: p.opcion_elegida_id ?? null,
        correct_option_id: p.correct_option_id ?? null,
        correct_option_text: p.correct_option_text ?? '',
        correcta: !!p.correcta,
        texto_alumno: p.texto_alumno ?? p.opcion_elegida_texto ?? '',
        explicacion_texto: p.explicacion_texto ?? '',
        explicacion_url: p.explicacion_url ?? '',
        all_options: p.all_options ?? (p.opciones ?? [])
      };
    });
  } catch (err) {
    console.error('Error cargando revisión ', err);
    alert('No se pudo cargar la revisión. Revisa la consola.');
    router.push('/alumno');
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  if (!localStorage.getItem('token')) {
    router.push('/acceso-restringido');
    return;
  }
  load();
});
</script>

<style scoped>
.revision-ensayo {
  font-family: 'Segoe UI', sans-serif;
  color: white;
  padding: 24px;
  min-height: 60vh;
  display:flex;
  flex-direction:column;
  align-items:center;
  gap:12px;
}
.header-row { width:100%; max-width:1000px; display:flex; justify-content:space-between; align-items:center; }
.titulo { margin:0; font-size:1.4rem; color:#eaf3ea; }

.controls { width:100%; max-width:1000px; display:flex; justify-content:flex-end; margin-bottom:8px; }
.lbl-filter { color:#dfeff0; font-weight:500; }
.select-input {
  margin-left:8px;
  background: rgba(255,255,255,0.06);
  color: black;
  border: 1px solid rgba(255,255,255,0.12);
  border-radius:6px;
  padding:6px 8px;
}

.loading { opacity: 0.85; margin: 8px 0; color:#dfeff0; }

.preg-list { list-style:none; padding:0; margin:0; width:100%; max-width:1000px; display:flex; flex-direction:column; gap:12px; }
.preg-item { padding:12px; border-radius:10px; background: rgba(255,255,255,0.03); box-shadow:0 4px 10px rgba(0,0,0,0.15); }
.preg-item.ok { border-left:6px solid #2ecc71; }
.preg-item.ko { border-left:6px solid #e74c3c; }

.preg-header { display:flex; justify-content:space-between; align-items:center; gap:12px; margin-bottom:8px; }
.enunciado { font-weight:600; color:#f8f8f8; }
.status { padding:6px 10px; border-radius:999px; font-weight:600; font-size:0.9rem; }
.stat-ok { background: rgba(46,204,113,0.12); color:#2ecc71; }
.stat-ko { background: rgba(231,76,60,0.08); color:#e74c3c; }

.respuesta { margin-top:6px; color:#eaf3ea; }
.muted { color: #bbb; font-style: italic; }

.opciones-list { margin-top:8px; padding-left:18px; }
.op-item { margin-bottom:6px; color:#f1f1f1; }
.op-correct { font-weight:700; color:#2ecc71; }
.op-selected { text-decoration: underline; font-weight:600; color:#ffd966; }
.note { font-size:0.85rem; color:#dfe6ea; margin-left:6px; }

.acciones { margin-top:10px; display:flex; gap:8px; align-items:center; }
.btn {
  background: #f4f4f4;
  color: #2c3e50;
  border: none;
  padding: 8px 12px;
  border-radius: 8px;
  cursor: pointer;
  font-weight:600;
}
.btn:hover { background:#e0e0e0; }
.btn.ghost { background: transparent; border: 1px solid rgba(255,255,255,0.06); color:#f2f2f2; }
.btn.ghost:hover { background: rgba(255,255,255,0.03); }

.explicacion { margin-top:10px; padding:12px; background: rgba(0,0,0,0.18); border-radius:8px; color:#e8f4ea; }

.editor { margin-top:10px; padding:12px; background: rgba(255,255,255,0.02); border-radius:8px; }
.lbl { display:block; font-weight:600; margin-bottom:6px; color:#eaf3ea; }
.txt-area, .txt-input {
  width:100%;
  border-radius:8px;
  border:1px solid rgba(255,255,255,0.12);
  background: rgba(255,255,255,0.04);
  color:#f7f7f7;
  padding:8px;
  box-sizing:border-box;
  margin-bottom:8px;
}
.txt-area:focus, .txt-input:focus { outline:none; border-color:#4dd0e1; background: rgba(255,255,255,0.06); }
.editor-actions { display:flex; gap:10px; align-items:center; }
.save-btn {
  background: #f4f4f4;
  color: #2c3e50;
  border: none;
  padding: 8px 14px;
  border-radius: 8px;
  cursor:pointer;
  font-weight:600;
}
.save-btn:disabled { opacity:0.6; cursor:not-allowed; }

.ok { color:#2ecc71; font-weight:700; margin-left:8px; }
.err { color:#e74c3c; font-weight:700; margin-left:8px; }

@media (max-width:720px) {
  .revision-ensayo { padding:16px; }
  .preg-item { padding:10px; }
  .titulo { font-size:1.2rem; }
}
</style>
