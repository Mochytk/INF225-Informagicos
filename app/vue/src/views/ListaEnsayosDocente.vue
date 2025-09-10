<template>
  <div class="lista-docente">
    <h2>Ensayos disponibles</h2>
    <div v-if="loading">Cargando...</div>
    <div v-else>
      <ul class="lista">
        <li v-for="e in ensayos" :key="e.id" class="ensayo-item">
          <div>
            <strong>{{ e.titulo }}</strong>
            <div class="detalle">{{ e.materia }} · {{ e.curso || '' }}</div>
          </div>
          <div>
            <button @click="verResultados(e.id)">Ver resultados</button>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { fetchAllEnsayos } from '@/api/ensayos';

const router = useRouter();
const ensayos = ref([]);
const loading = ref(false);

onMounted(async () => {
  // protección básica por rol
  const rol = (localStorage.getItem('rol') || '').toLowerCase();
  if (rol !== 'docente' && !JSON.parse(localStorage.getItem('is_staff') || 'false')) {
    router.push('/acceso-restringido');
    return;
  }

  loading.value = true;
  try {
    const data = await fetchAllEnsayos();
    ensayos.value = Array.isArray(data) ? data : (data.results || []);
  } catch (err) {
    console.error('Error al cargar ensayos', err);
    ensayos.value = [];
  } finally {
    loading.value = false;
  }
});

function verResultados(id) {
  router.push({ name: 'ensayo-resultados', params: { id } });
}
</script>

<style scoped>
.lista-docente { color: white; padding: 20px; }
.lista { list-style:none; padding:0; margin:0; display:flex; flex-direction:column; gap:12px; }
.ensayo-item { display:flex; justify-content:space-between; align-items:center; padding:12px; background: rgba(0,0,0,0.25); border-radius:8px;}
button { background:#1976d2; color:white; border:none; padding:8px 12px; border-radius:6px; cursor:pointer; }
.detalle { font-size:0.9rem; opacity:0.8; }
</style>
