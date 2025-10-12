<template>
  <div class="revision-ensayo">
    <h2>Revisión — {{ resumen.titulo || ('Ensayo ' + ensayoId) }}</h2>

    <div class="controls">
      <label>Filtrar:
        <select v-model="filtro">
          <option value="all">Todas</option>
          <option value="correct">Solo correctas</option>
          <option value="incorrect">Solo incorrectas</option>
        </select>
      </label>
    </div>

    <div v-if="loading">Cargando revisión...</div>

    <ul v-else class="preg-list">
      <li v-for="q in filteredQuestions" :key="q.pregunta_id" :class="['preg', q.correcta ? 'ok' : 'ko']">
        <div class="preg-header">
          <div class="enunciado">{{ q.enunciado }}</div>
          <div class="status">{{ q.correcta ? 'Correcta' : 'Incorrecta' }}</div>
        </div>

        <div class="respuesta">
          <strong>Tu respuesta:</strong>
          <span v-if="q.opcion_elegida_texto && q.opcion_elegida_texto.trim() !== ''">
            {{ q.opcion_elegida_texto }}
          </span>
          <span v-else class="muted">Sin respuesta</span>
        </div>
        <ul v-if="q.all_options && q.all_options.length" class="opciones-list">
          <li v-for="op in q.all_options" :key="op.id">
            <span :class="{'op-correct': op.id === q.correct_option_id, 'op-selected': op.id === q.opcion_elegida_id}">
              {{ op.texto }}
            </span>
            <small v-if="op.id === q.correct_option_id"> — (Respuesta correcta)</small>
            <small v-if="op.id === q.opcion_elegida_id"> — (Elegida)</small>
          </li>
        </ul>

        <div class="acciones">
          <button @click="toggleExp(q.pregunta_id)">{{ openExp === q.pregunta_id ? 'Ocultar explicación' : 'Ver explicación' }}</button>

          <button v-if="esDocente" @click="toggleEditMode(q)">
            {{ editarMode === q.pregunta_id ? 'Cancelar' : 'Editar explicación' }}
          </button>
        </div>

        <div v-if="openExp === q.pregunta_id" class="explicacion">
          <p v-if="q.correct_option_text"><strong>Respuesta correcta:</strong> {{ q.correct_option_text }}</p>

          <p v-if="q.explicacion_texto"><strong>Explicación:</strong> {{ q.explicacion_texto }}</p>
          <p v-if="q.explicacion_url">Recurso: <a :href="q.explicacion_url" target="_blank">{{ q.explicacion_url }}</a></p>
          <p v-if="!q.explicacion_texto && !q.explicacion_url && !q.correct_option_text">No hay explicación disponible.</p>
        </div>

        <div v-if="editarMode === q.pregunta_id" class="editor">
          <textarea v-model="editText" rows="4" placeholder="Explicación breve..."></textarea>
          <input v-model="editUrl" placeholder="URL de video (opcional)" />
          <div class="editor-actions">
            <button @click="guardarExplicacion(q.pregunta_id)">Guardar</button>
            <button @click="cancelEdit">Cancelar</button>
          </div>
        </div>
      </li>
    </ul>

    <br /><br />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';
import { getRevision } from '@/api/ensayos'; 

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

const token = localStorage.getItem('token') || '';
const esDocente = (localStorage.getItem('rol') || '').toLowerCase() === 'docente' || JSON.parse(localStorage.getItem('is_staff') || 'false');

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
}

function toggleEditMode(q) {
  if (editarMode.value === q.pregunta_id) {
    cancelEdit();
    return;
  }
  editarMode.value = q.pregunta_id;
  editText.value = q.explicacion_texto || '';
  editUrl.value = q.explicacion_url || '';
}


async function guardarExplicacion(preguntaId) {
  try {
    const payload = { texto: editText.value || '', url: editUrl.value || '' };
    const headers = { Authorization: token ? `Token ${token}` : '' , 'Content-Type': 'application/json' };
    // PATCH
    await axios.patch(`http://127.0.0.1:8000/api/preguntas/${preguntaId}/explicacion/`, payload, { headers });

    // actualizar copia local
    const q = preguntas.value.find(x => x.pregunta_id === preguntaId);
    if (q) {
      q.explicacion_texto = editText.value;
      q.explicacion_url = editUrl.value;
    }
    cancelEdit();
    alert('Explicación guardada');
  } catch (err) {
    console.error('Error guardando explicación', err);
    alert('No se pudo guardar explicación. Revisa la consola (500/403).');
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
.revision-ensayo { color: white; padding: 20px; }
.controls { margin-bottom:12px; }
.preg-list { list-style:none; padding:0; margin:0; }
.preg { padding:12px; border-radius:8px; margin-bottom:10px; background: rgba(255,255,255,0.03); }
.preg.ok { border-left:6px solid #2ecc71; }
.preg.ko { border-left:6px solid #e74c3c; }
.preg-header { display:flex; justify-content:space-between; align-items:center; gap:12px; }
.enunciado { font-weight:600; }
.acciones { margin-top:8px; display:flex; gap:8px; }
.editor textarea, .editor input { width:100%; margin-top:6px; padding:6px; border-radius:6px; }
.editor-actions { margin-top:8px; display:flex; gap:8px; }
.opciones-list { margin-top:8px; padding-left:18px; }
.opciones-list li { margin-bottom:6px; }
.op-correct { font-weight:700; color:#2ecc71; }
.op-selected { text-decoration: underline; }
.muted { color: #bbb; font-style: italic; }
.explicacion { margin-top:8px; padding:10px; background: rgba(0,0,0,0.15); border-radius:6px; }
</style>
