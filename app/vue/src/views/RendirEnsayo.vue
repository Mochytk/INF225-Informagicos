<template>
  <div class="rendir-ensayo" v-if="!loading">
    <h2>{{ ensayo.titulo }}</h2>
    <p class="meta">{{ ensayo.materia }} · {{ ensayo.curso }}</p>
    <div :class="temporizadorClase">
      <p id="t"></p>
    </div>

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
const answers = ref({}); 
const resultado = ref(null);

const temporizadorClase = ref('temporizador');

function iniciarTemporizador() {
  let tiempoRestante = 2400; // tiempo en segundos (por defecto: 40 minutos)
  const temporizador = document.getElementById('t');

  const intervalo = setInterval(() => {
    if (tiempoRestante <= 0) {
      clearInterval(intervalo);
      finalizarEnsayo();
      return;
    }

    if (tiempoRestante <= 300) {
      if (tiempoRestante <= 60) {
        temporizadorClase.value = 'temporizador alerta-tiempo unminuto';
      } else {
        temporizadorClase.value = 'temporizador alerta-tiempo';
      }
    }
    else {
      temporizadorClase.value = 'temporizador';
    }

    if (tiempoRestante === 60) {
      alert('¡Queda un minuto! Por favor, finaliza el ensayo.');
    }

    const minutos = Math.floor(tiempoRestante / 60);
    const segundos = tiempoRestante % 60;
    temporizador.textContent = `Tiempo restante: ${minutos} min ${segundos} seg`;
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
    ensayo.value = data;
    ensayo.value.preguntas.forEach(p => {
      answers.value[p.id] = isAlternativa(p.tipo) ? null : '';
    });
  } catch (err) {
    console.error('Error cargando ensayo', err);
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
  const payload = { respuestas: [] };
  for (const p of ensayo.value.preguntas) {
    const val = answers.value[p.id];
    if (isAlternativa(p.tipo)) {
      if (val === null || val === undefined) {
      }
      payload.respuestas.push({ pregunta_id: p.id, opcion_id: val });
    } else {
      payload.respuestas.push({ pregunta_id: p.id, texto: val || '' });
    }
  }

  try {
    const resp = await submitEnsayo(ensayo.value.id, payload.respuestas);
    resultado.value = { puntaje: resp.puntaje, fecha: resp.fecha };
  } catch (err) {
    console.error('Error al enviar ensayo', err);
    alert(err.response?.data?.error || 'Error al enviar ensayo');
  }
}

function finalizarEnsayo() {
  alert('¡El tiempo ha terminado! Tu ensayo será enviado automáticamente.');
  enviar();
}
</script>

<style scoped>
.rendir-ensayo { color: white; padding: 20px; }
.pregunta-card { background: rgba(255,255,255,0.04); padding:16px; margin-bottom:14px; border-radius:8px; }
.enunciado { margin-bottom: 8px; }
.opcion { margin: 6px 0; }
textarea { width: 100%; border-radius:6px; padding:8px; background: rgba(255,255,255,0.03); color: white; border:1px solid rgba(255,255,255,0.06); font-family: 'Segoe UI', sans-serif;}
.acciones { margin-top: 20px; }
button { background:#145a32; color:white; padding:8px 16px; border-radius:8px; border:none; cursor:pointer; }
.resultado-box { margin-top:20px; padding:12px; background: rgba(0,0,0,0.3); border-radius:8px; }
</style>
