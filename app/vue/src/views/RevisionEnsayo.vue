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
          <div class="enunciado">{{ q.texto || q.enunciado }}</div>
          <div class="status">{{ q.correcta ? 'Correcta' : 'Incorrecta' }}</div>
        </div>

        <div class="respuesta">
          <strong>Tu respuesta:</strong>
          <span>{{ q.respuesta_texto || q.opcion_texto || q.respuesta || '—' }}</span>
        </div>

        <div class="acciones">
          <button @click="toggleExp(q.pregunta_id)">Ver explicación</button>

          <!-- si es docente, mostrar botón editar -->
          <button v-if="esDocente" @click="editarMode = editarMode === q.pregunta_id ? null : q.pregunta_id">
            {{ editarMode === q.pregunta_id ? 'Cancelar' : 'Editar explicación' }}
          </button>
        </div>

        <div v-if="openExp === q.pregunta_id" class="explicacion">
          <p v-if="q.explicacion_texto">{{ q.explicacion_texto }}</p>
          <p v-if="q.explicacion_url">Video/Link: <a :href="q.explicacion_url" target="_blank">{{ q.explicacion_url }}</a></p>
          <p v-if="!q.explicacion_texto && !q.explicacion_url">No hay explicación disponible.</p>
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
const preguntas = ref([]); // array con { pregunta_id, texto, correcta, respuesta_texto, opcion_texto, explicacion_texto, explicacion_url }
const loading = ref(false);

const filtro = ref('all');
const openExp = ref(null);
const editarMode = ref(null);
const editText = ref('');
const editUrl = ref('');

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

async function guardarExplicacion(preguntaId) {
  try {
    await editarExplicacion(preguntaId, { explicacion_texto: editText.value, explicacion_url: editUrl.value });
    // actualizar local copy
    const q = preguntas.value.find(x => x.pregunta_id === preguntaId);
    if (q) {
      q.explicacion_texto = editText.value;
      q.explicacion_url = editUrl.value;
    }
    cancelEdit();
    alert('Explicación guardada');
  } catch (err) {
    console.error('Error guardando explicación', err);
    alert('No se pudo guardar explicación. Revisa la consola.');
  }
}

async function load() {
  loading.value = true;
  try {
    const data = await getRevision(ensayoId, resultadoId);
    // Esperamos un JSON con resumen + preguntas. Ajusta según tu backend:
    // ej. { resumen: {...}, preguntas: [...] } o directamente { preguntas: [...] }
    resumen.value = data.resumen || { titulo: data.titulo || '' };
    // Intentar extraer preguntas de varias formas:
    preguntas.value = data.preguntas || data.items || data.questions || data.lista_preguntas || [];

    // normalizar campos si es necesario (ejemplo de mapeo)
    preguntas.value = preguntas.value.map(p => ({
      pregunta_id: p.pregunta_id ?? p.id,
      texto: p.texto ?? p.enunciado ?? p.pregunta_texto,
      correcta: !!p.correcta,
      respuesta_texto: p.respuesta_texto ?? p.respuesta ?? p.alumno_respuesta ?? '',
      opcion_texto: p.opcion_texto ?? (p.opcion ? p.opcion.texto : '') ?? '',
      explicacion_texto: p.explicacion_texto ?? p.explicacion?.texto ?? '',
      explicacion_url: p.explicacion_url ?? p.explicacion?.url ?? ''
    }));
  } catch (err) {
    console.error('Error cargando revisión', err);
    alert('No se pudo cargar la revisión. Revisa la consola.');
    router.push('/alumno'); // volver al dashboard
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
</style>
