<template>
  <div class="rendir-ensayo" v-if="!loading">
    <h2>{{ ensayo.titulo }}</h2>
    <p class="meta">{{ ensayo.materia }} · {{ ensayo.curso }}</p>

    <form @submit.prevent="enviar">
      <div v-for="preg in ensayo.preguntas" :key="preg.id" class="pregunta-card">
        <h3>Pregunta {{ loopIndex(preg) }} - {{ tipoLabel(preg.tipo) }}</h3>
        <p class="enunciado">{{ preg.enunciado || preg.texto || 'Sin enunciado' }}</p>

        <div v-if="isAlternativa(preg.tipo)">
          <div v-for="op in preg.opciones" :key="op.id" class="opcion">
            <label>
              <input type="radio"
                     :name="'preg-' + preg.id"
                     :value="op.id"
                     v-model="answers[preg.id]" />
              {{ op.texto }}
            </label>
          </div>
        </div>

        <div v-else>
          <textarea v-model="answers[preg.id]" placeholder="Escribe tu respuesta..." rows="5"></textarea>
        </div>
      </div>

      <div class="acciones">
        <button type="submit">Enviar ensayo</button>
      </div>
    </form>

    <div v-if="resultado" class="resultado-box">
      <h3>Resultado</h3>
      <p>Puntaje: {{ resultado.puntaje }}</p>
      <p>Fecha: {{ resultado.fecha }}</p>
    </div>
  </div>

  <div v-else> Cargando ensayo... </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { fetchEnsayo, submitEnsayo } from '@/api/ensayos';

const route = useRoute();
const router = useRouter();
const id = route.params.id;

const ensayo = ref({ preguntas: [] });
const loading = ref(true);
const answers = ref({}); // map preguntaId -> opcionId | texto
const resultado = ref(null);

onMounted(async () => {
  const token = localStorage.getItem('token');
  if (!token) {
    router.push('/'); // o /acceso-restringido
    return;
  }
  try {
    const data = await fetchEnsayo(id);
    ensayo.value = data;
    // inicializar answers por pregunta
    ensayo.value.preguntas.forEach(p => {
      // si es alternativa, default null; si desarrollo, empty string
      answers.value[p.id] = isAlternativa(p.tipo) ? null : '';
    });
  } catch (err) {
    console.error('Error cargando ensayo', err);
    // redirigir o mostrar mensaje
  } finally {
    loading.value = false;
  }
});

function isAlternativa(tipo) {
  if (!tipo) return false;
  tipo = tipo.toString().toLowerCase();
  return tipo.includes('alternativa') || tipo.includes('multiple') || tipo.includes('vf');
}

function tipoLabel(tipo) {
  if (!tipo) return 'Desconocido';
  return tipo.charAt(0).toUpperCase() + tipo.slice(1);
}

function loopIndex(preg) {
  return ensayo.value.preguntas.indexOf(preg) + 1;
}

async function enviar() {
  // construir payload
  const payload = { respuestas: [] };
  for (const p of ensayo.value.preguntas) {
    const val = answers.value[p.id];
    if (isAlternativa(p.tipo)) {
      if (val === null || val === undefined) {
        // opcional: puedes forzar que respondan todas
        // return alert(`Debes responder la pregunta ${p.id}`);
      }
      payload.respuestas.push({ pregunta_id: p.id, opcion_id: val });
    } else {
      payload.respuestas.push({ pregunta_id: p.id, texto: val || '' });
    }
  }

  try {
    const resp = await submitEnsayo(ensayo.value.id, payload.respuestas);
    resultado.value = { puntaje: resp.puntaje, fecha: resp.fecha };
    // opcional: guardar localmente o redirigir al listado de resultados
  } catch (err) {
    console.error('Error al enviar ensayo', err);
    alert(err.response?.data?.error || 'Error al enviar ensayo');
  }
}
</script>

<style scoped>
.rendir-ensayo { color: white; padding: 20px; }
.pregunta-card { background: rgba(255,255,255,0.04); padding:16px; margin-bottom:14px; border-radius:8px; }
.enunciado { margin-bottom: 8px; }
.opcion { margin: 6px 0; }
textarea { width: 100%; border-radius:6px; padding:8px; background: rgba(255,255,255,0.03); color: white; border:1px solid rgba(255,255,255,0.06); }
.acciones { margin-top: 20px; }
button { background:#145a32; color:white; padding:8px 16px; border-radius:8px; border:none; cursor:pointer; }
.resultado-box { margin-top:20px; padding:12px; background: rgba(0,0,0,0.3); border-radius:8px; }
</style>
