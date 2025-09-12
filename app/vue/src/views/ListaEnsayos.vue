<template>
  <div class="lista-ensayos">
    <h2>Ensayos — {{ materia }}</h2>
    <div v-if="loading">Cargando...</div>
    <div v-if="!loading && ensayosFiltrados.length === 0">No hay ensayos disponibles.</div>

    <ul>
      <li v-for="e in ensayosFiltrados" :key="e.id" class="ensayo-item">
        <strong>{{ e.titulo }}</strong>
        <div class="meta">{{ e.materia }} · {{ e.curso }}</div>
        <button @click="irAEnsayo(e.id)">Rendir</button>
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

const ensayosFiltrados = computed(() =>
  ensayos.value.filter(e => (e.materia || '').toLowerCase() === props.materia.toLowerCase())
);

onMounted(async () => {
  loading.value = true;
  try {
    const data = await fetchAllEnsayos();
    ensayos.value = Array.isArray(data) ? data : data.results || [];
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
.lista-ensayos { color: white; padding: 20px; }
.ensayo-item { margin: 12px 0; padding: 10px; background: rgba(255,255,255,0.06); border-radius: 8px; display:flex; justify-content:space-between; align-items:center;}
.meta { font-size: 0.9rem; opacity: 0.9; }
button { background:#2ecc71; color:white; padding:8px 12px; border-radius:6px; border:none; cursor:pointer; }
</style>
