<template>
  <div class="completed-ensayos">
    <div class="header-row">
      <h2 class="titulo">Mis ensayos completados</h2>
    </div>

    <div class="contenido">
      <div v-if="loading" class="loading">Cargando...</div>

      <div v-else>
        <div v-if="ensayos.length === 0" class="empty-state">
          No tienes ensayos completados aún.
        </div>

        <ul v-else class="ensayos-list">
          <li v-for="r in ensayos" :key="r.resultado_id" class="ensayo-item">
            <div class="meta">
              <strong class="ensayo-titulo">{{ r.titulo || r.ensayo_titulo || ('Ensayo ' + r.ensayo_id) }}</strong>
              <small class="fecha">{{ formatDate(r.fecha) }}</small>
            </div>

            <div class="stats">
              <span class="puntaje">Puntaje: <strong>{{ r.puntaje ?? '-' }}</strong></span>
              <button class="btn-revisar" @click="irARevision(r.ensayo_id, r.resultado_id)">Revisar</button>
            </div>
          </li>
        </ul>
      </div>
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
  try {
    const d = new Date(iso);
    return d.toLocaleString();
  } catch (e) {
    return iso;
  }
}

async function load() {
  loading.value = true;
  try {
    const data = await getEnsayosCompletados();

    ensayos.value = Array.isArray(data) ? data : (data.results || []);
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
.completed-ensayos {
  font-family: 'Segoe UI', sans-serif;
  color: white;
  padding: 24px;
  display:flex;
  flex-direction:column;
  align-items:center;
  gap:12px;
  min-height: 60vh;
}

.header-row { width:100%; max-width:1000px; display:flex; justify-content:space-between; align-items:center; }
.titulo { margin:0; font-size:1.4rem; color:#eaf3ea; }

.contenido { width:100%; max-width:1000px; box-sizing:border-box; }

.loading { color:#dfeff0; opacity:0.9; margin:12px 0; }

.empty-state {
  background: rgba(255,255,255,0.02);
  padding:18px;
  border-radius:10px;
  text-align:center;
  color:#e9f1ea;
  box-shadow: 0 4px 10px rgba(0,0,0,0.12);
}

.ensayos-list {
  list-style:none;
  padding:0;
  margin:0;
  display:flex;
  flex-direction:column;
  gap:12px;
}

.ensayo-item {
  display:flex;
  justify-content:space-between;
  align-items:center;
  gap:12px;
  padding:14px;
  border-radius:10px;
  background: rgba(255,255,255,0.03);
  box-shadow: 0 6px 18px rgba(0,0,0,0.12);
}

.meta { display:flex; flex-direction:column; gap:4px; }
.ensayo-titulo { font-size:1rem; color:#f6fbf6; }
.fecha { color:#dfe6e8; font-size:0.9rem; }

.stats { display:flex; gap:12px; align-items:center; }
.puntaje { color:#edf7ee; font-size:0.95rem; }

.btn-revisar {
  background: #2ecc71;
  color: white;
  border: none;
  padding: 8px 14px;
  border-radius: 8px;
  cursor: pointer;
  font-weight:700;
}
.btn-revisar:hover { background: #27ae60; }

@media (max-width:720px) {
  .completed-ensayos { padding:16px; }
  .ensayo-item { flex-direction:column; align-items:flex-start; gap:8px; }
  .stats { width:100%; justify-content:space-between; }
}
</style>
