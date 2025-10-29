<template>
  <div class="lista-docente">
    <h2 class="titulo">Ensayos disponibles</h2>

    <div v-if="loading" class="loading">Cargando ensayos...</div>

    <div v-else>
      <ul class="lista">
        <li v-for="e in ensayos" :key="e.id" class="ensayo-item">
          <div class="info">
            <strong class="ensayo-titulo">{{ e.titulo }}</strong>
            <div class="detalle">{{ e.materia }} <span v-if="e.curso">· {{ e.curso }}</span></div>
          </div>

          <div class="acciones">
            <button class="nav-btn" @click="verResultados(e.id)">Ver resultados</button>
          </div>
        </li>
      </ul>

      <div v-if="ensayos.length === 0" class="no-data">
        No hay ensayos disponibles.
      </div>
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
.lista-docente {
  font-family: 'Segoe UI', sans-serif;
  color: white;
  padding: 32px 40px;
  min-height: 60vh;
}


.titulo {
  font-size: 1.8rem;
  margin-bottom: 18px;
}


.lista {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 14px;
}


.ensayo-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
  background: rgba(255,255,255,0.04);
  border-radius: 10px;
  box-shadow: 0 6px 18px rgba(0,0,0,0.25);
  transition: transform 0.12s ease, box-shadow 0.12s ease;
}

.ensayo-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 26px rgba(0,0,0,0.35);
}

.info {
  display:flex;
  flex-direction:column;
  gap:6px;
}


.ensayo-titulo {
  font-size: 1.05rem;
  color: #f7f7f7;
}


.detalle {
  font-size: 0.95rem;
  opacity: 0.85;
  color: #dfe6ea;
}


.acciones {
  display:flex;
  align-items:center;
  gap:8px;
}


.nav-btn {
  background-color: #f4f4f4;
  color: #2c3e50;
  border: 1px solid #ccc;
  border-radius: 8px;
  padding: 8px 14px;
  cursor: pointer;
  font-size: 0.95em;
  font-weight: 600;
}

.nav-btn:hover {
  background-color: #e0e0e0;
}


.no-data {
  margin-top: 18px;
  opacity: 0.9;
  color: #dcdcdc;
  text-align: center;
  padding: 8px;
}


.loading {
  color: #e6eef6;
  opacity: 0.95;
}
</style>
