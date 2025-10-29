<template>
  <div class="rendir-ensayo">
    <div class="header">
      <h2 class="titulo">{{ ensayo.titulo || ('Ensayo ' + id) }}</h2>
      <p class="meta">{{ ensayo.materia || '' }} · {{ ensayo.curso || '' }}</p>
    </div>

    <div :class="temporizadorClase" v-if="!loading">
      <p id="t"></p>
    </div>

    <form @submit.prevent="enviar" v-if="!loading" class="form-ensayo">
      <div v-for="preg in ensayo.preguntas" :key="preg.id" class="pregunta-card">
        <h3 class="preg-titulo">Pregunta {{ loopIndex(preg) }}</h3>
        <p class="enunciado">{{ preg.enunciado || preg.texto || 'Sin enunciado' }}</p>

        <div v-if="isAlternativa(preg.tipo)" class="opciones">
          <label v-for="op in preg.opciones" :key="op.id" class="opcion">
            <input
              type="radio"
              :name="'preg-' + preg.id"
              :value="op.id"
              v-model="answers[preg.id]" />
            <span class="op-texto">{{ op.texto }}</span>
          </label>
        </div>

        <div v-else>
          <textarea v-model="answers[preg.id]" placeholder="Escribe tu respuesta..." rows="6" class="respuesta-textarea"></textarea>
        </div>
      </div>

      <div class="acciones">
        <button type="submit" class="btn-enviar">Enviar ensayo</button>
      </div>
    </form>

    <div v-if="loading" class="loading">Cargando ensayo...</div>

    <div v-if="resultado" class="resultado-box">
      <h3>Resultado</h3>
      <p>Puntaje: <strong>{{ resultado.puntaje }}</strong></p>
      <p>Fecha: {{ resultado.fecha }}</p>
    </div>
  </div>
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
const answers = ref({});
const resultado = ref(null);
const temporizadorClase = ref('temporizador');

function iniciarTemporizador() {
  let tiempoRestante = 2400;
  const temporizador = document.getElementById('t');
  const intervalo = setInterval(() => {
    if (tiempoRestante <= 0) {
      clearInterval(intervalo);
      finalizarEnsayo();
      return;
    }
    if (tiempoRestante <= 300) {
      temporizadorClase.value = tiempoRestante <= 60 ? 'temporizador alerta-tiempo unminuto' : 'temporizador alerta-tiempo';
    } else {
      temporizadorClase.value = 'temporizador';
    }
    if (tiempoRestante === 60) {
      alert('¡Queda un minuto! Por favor, finaliza el ensayo.');
    }
    const minutos = Math.floor(tiempoRestante / 60);
    const segundos = tiempoRestante % 60;
    if (temporizador) temporizador.textContent = `Tiempo restante: ${minutos} min ${segundos} seg`;
    tiempoRestante--;
  }, 1000);
}

onMounted(async () => {
  iniciarTemporizador();
  const token = localStorage.getItem('token');
  if (!token) {
    router.push('/');
    return;
  }
  try {
    const data = await fetchEnsayo(id);
    ensayo.value = data || { preguntas: [] };
    ensayo.value.preguntas = ensayo.value.preguntas || [];
    ensayo.value.preguntas.forEach(p => {
      answers.value[p.id] = isAlternativa(p.tipo) ? null : '';
    });
  } catch (err) {
    router.push('/alumno');
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
  return (ensayo.value.preguntas || []).indexOf(preg) + 1;
}

async function enviar() {
  const payload = { respuestas: [] };
  for (const p of ensayo.value.preguntas) {
    const val = answers.value[p.id];
    if (isAlternativa(p.tipo)) {
      payload.respuestas.push({ pregunta_id: p.id, opcion_id: val });
    } else {
      payload.respuestas.push({ pregunta_id: p.id, texto: val || '' });
    }
  }
  try {
    const resp = await submitEnsayo(ensayo.value.id, payload.respuestas);
    resultado.value = { puntaje: resp.puntaje, fecha: resp.fecha };
  } catch (err) {
    alert(err.response?.data?.error || 'Error al enviar ensayo');
  }
}

function finalizarEnsayo() {
  alert('¡El tiempo ha terminado! Tu ensayo será enviado automáticamente.');
  enviar();
}
</script>

<style scoped>
.rendir-ensayo {
  font-family: 'Segoe UI', sans-serif;
  color: white;
  padding: 24px;
  min-height: 60vh;
  display:flex;
  flex-direction:column;
  align-items:center;
  gap:16px;
}

.rendir-ensayo > * { width:100%; max-width:1000px; box-sizing:border-box; }

.header { display:flex; flex-direction:column; gap:6px; }
.titulo { margin:0; color:#eaf3ea; font-size:1.4rem; }
.meta { margin:0; color:#dfe6e8; font-size:0.95rem; }

.temporizador {
  margin: 6px 0 12px 0;
  padding: 8px 12px;
  background: rgba(255,255,255,0.02);
  border-radius: 8px;
  text-align:center;
}
.alerta-tiempo { background: rgba(231,76,60,0.12); color:#ffdcdc; }
.unminuto { background: rgba(231,76,60,0.18); color:#ffdcdc; }

.form-ensayo { width:100%; }

.pregunta-card {
  background: rgba(255,255,255,0.03);
  padding:16px;
  margin-bottom:14px;
  border-radius:10px;
  box-shadow: 0 6px 18px rgba(0,0,0,0.08);
}

.preg-titulo { margin:0 0 8px 0; font-size:1rem; color:#f6fbf6; }
.enunciado { margin:0 0 12px 0; color:#e7f1ea; }

.opciones { display:flex; flex-direction:column; gap:8px; }
.opcion { display:flex; align-items:center; gap:10px; padding:6px 8px; border-radius:6px; background: rgba(255,255,255,0.01); }
.op-texto { color:#eef7ee; }

.respuesta-textarea {
  width:100%;
  border-radius:8px;
  padding:10px;
  background: rgba(255,255,255,0.02);
  color: white;
  border:1px solid rgba(255,255,255,0.06);
  font-family: 'Segoe UI', sans-serif;
}

.acciones { margin-top: 14px; display:flex; justify-content:flex-end; }
.btn-enviar {
  background: #2ecc71;
  color: white;
  border: none;
  padding: 10px 18px;
  border-radius: 10px;
  cursor: pointer;
  font-weight:700;
}
.btn-enviar:hover { background: #27ae60; }

.loading { color:#dfeff0; opacity:0.9; margin:12px 0; text-align:center; }

.resultado-box {
  margin-top:20px;
  padding:16px;
  background: rgba(0,0,0,0.25);
  border-radius:8px;
  width:100%;
  max-width:700px;
  box-sizing:border-box;
  color:#eaf3ea;
}

@media (max-width:720px) {
  .rendir-ensayo { padding:16px; }
  .acciones { justify-content:center; }
}
</style>
