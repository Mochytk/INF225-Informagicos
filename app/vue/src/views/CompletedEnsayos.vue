<template>
  <div class="completed-ensayos">
    <h2>Mis ensayos completados</h2>

    <div v-if="loading">Cargando...</div>
    <div v-else>
      <div v-if="ensayos.length === 0">No tienes ensayos completados aún.</div>

      <ul class="ensayos-list">
        <li v-for="r in ensayos" :key="r.resultado_id" class="ensayo-item">
          <div class="meta">
            <strong>{{ r.titulo || ('Ensayo ' + r.ensayo_id) }}</strong>
            <small>{{ formatDate(r.fecha) }}</small>
          </div>
          <div class="stats">
            <span>Puntaje: {{ r.puntaje }}</span>
            <button @click="irARevision(r.ensayo_id, r.resultado_id)">Revisar</button>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { getEnsayosCompletados } from '@/api/ensayos';

const router = useRouter();
const ensayos = ref([]);
const loading = ref(false);

function formatDate(iso) {
  if (!iso) return '';
  try { return new Date(iso).toLocaleString(); } catch(e){ return iso; }
}

async function load() {
  loading.value = true;
  try {
    const data = await getEnsayosCompletados();
    // Esperamos array de resultados: [{ ensayo_id, resultado_id, titulo, puntaje, fecha }, ...]
    ensayos.value = Array.isArray(data) ? data : [];
  } catch (err) {
    console.error('Error cargando ensayos completados', err);
    ensayos.value = [];
  } finally {
    loading.value = false;
  }
}

function irARevision(ensayoId, resultadoId) {
  router.push({ name: 'revision-ensayo', params: { ensayoId, resultadoId } });
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
.completed-ensayos { color: white; padding: 20px; }
.ensayos-list { list-style:none; padding:0; margin:0; }
.ensayo-item { display:flex; justify-content:space-between; align-items:center; gap:12px; padding:10px; border-radius:8px; background: rgba(255,255,255,0.03); margin-bottom:8px; }
.meta small { display:block; color:#ddd; font-size:0.9rem; }
.stats button { background:#2ecc71; border:none; padding:8px 12px; border-radius:8px; color:white; cursor:pointer; }
</style>
