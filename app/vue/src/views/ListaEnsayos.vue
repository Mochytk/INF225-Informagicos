<template>
  <div class="lista-ensayos">
    <div class="header">
      <h2 class="title">Ensayos — {{ materia }}</h2>
    </div>

    <div v-if="loading" class="loading">Cargando...</div>
    <div v-else-if="ensayosFiltrados.length === 0" class="no-data">No hay ensayos disponibles.</div>

    <ul v-else class="ensayos-list">
      <li v-for="e in ensayosFiltrados" :key="e.id" class="ensayo-item">
        <div class="info">
          <strong class="ensayo-title">{{ e.titulo }}</strong>
          <div class="meta">{{ e.materia }} · {{ e.curso || '' }}</div>
        </div>
        <div class="actions">
          <button class="btn-rendir" @click="irAEnsayo(e.id)">Rendir</button>
        </div>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { fetchAllEnsayos } from '@/api/ensayos';

const props = defineProps({
  materia: { type: String, required: true }
});

const ensayos = ref([]);
const loading = ref(false);
const router = useRouter();

const ensayosFiltrados = computed(() => {
  const mat = (props.materia || '').toString().trim().toLowerCase();
  if (!mat) return ensayos.value;
  return ensayos.value.filter(e => ((e.materia || '').toString().toLowerCase() === mat));
});

onMounted(async () => {
  loading.value = true;
  try {
    const data = await fetchAllEnsayos();
    ensayos.value = Array.isArray(data) ? data : (data.results || []);
  } catch (err) {
    console.error('Error al obtener ensayos', err);
    ensayos.value = [];
  } finally {
    loading.value = false;
  }
});

function irAEnsayo(id) {
  router.push({ name: 'rendir-ensayo', params: { id } });
}
</script>

<style scoped>
.lista-ensayos {
  font-family: 'Segoe UI', sans-serif;
  color: white;
  padding: 24px;
  min-height: 60vh;
  display: flex;
  flex-direction: column;
  gap: 12px;
  align-items: center;
}
.lista-ensayos > * {
  width: 100%;
  max-width: 1000px;
  box-sizing: border-box;
}

.header { display: flex; justify-content: space-between; align-items: center; }
.title { margin: 0 0 6px 0; color: #eaf3ea; font-size: 1.3rem; }

.loading, .no-data {
  text-align: center;
  opacity: 0.85;
  margin: 12px 0;
  color: #dfeff0;
}

.ensayos-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 12px; }

.ensayo-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding: 14px;
  border-radius: 10px;
  background: rgba(255,255,255,0.03);
  box-shadow: 0 6px 18px rgba(0,0,0,0.06);
}

.info { display:flex; flex-direction:column; gap:4px; }
.ensayo-title { color: #f6fbf6; font-size: 1rem; }
.meta { font-size: 0.9rem; color: #d6e7d6; opacity: 0.9; }

.actions { display:flex; gap:8px; align-items:center; }

.btn-rendir {
  background: #2ecc71;
  color: white;
  border: none;
  padding: 8px 14px;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 700;
}
.btn-rendir:hover { background: #27ae60; }

@media (max-width: 720px) {
  .ensayo-item { flex-direction: column; align-items: flex-start; }
  .actions { width: 100%; display:flex; justify-content: flex-end; margin-top:8px; }
}
</style>
