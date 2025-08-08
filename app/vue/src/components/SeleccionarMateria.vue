<template>
    <div class="materias-container">
      <h1 class="titulo">Escoge una materia</h1>
  
      <div class="materias-grid">
        <div class="materia" @click="seleccionarMateria('Lenguaje')">
          <img :src="imagenes.lenguaje" alt="Lenguaje" class="materia-img" />
          <p>Lenguaje</p>
        </div>
        <div class="materia" @click="seleccionarMateria('Matematicas')">
          <img :src="imagenes.matematicas" alt="Matematicas" class="materia-img" />
          <p>Matemáticas</p>
        </div>
        <div class="materia" @click="seleccionarMateria('Historia')">
          <img :src="imagenes.historia" alt="Historia" class="materia-img" />
          <p>Historia</p>
        </div>
        <div class="materia" @click="seleccionarMateria('Ciencias')">
          <img :src="imagenes.ciencias" alt="Ciencias" class="materia-img" />
          <p>Ciencias</p>
        </div>
      </div>
    </div>
  </template>
  
<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const imagenes = {
    lenguaje: '/img/lenguaje.jpg',
    matematicas: '/img/matematicas.jpg',
    historia: '/img/historia.jpg',
    ciencias: '/img/ciencias.jpg',
};

function verResultados() {
    alert("Aquí se mostrarán tus resultados.");
}

function logout() {
    localStorage.clear();
    router.push('/');
}

function seleccionarMateria(nombre) {
    localStorage.setItem('materiaSeleccionada', nombre);
    router.push('/alumno/ensayo');
}

onMounted(() => {
    // Protección: si no está logeado, redirige
    if (!localStorage.getItem('token')) {
        router.push('/acceso-restringido');
    }
});
</script>
  
  <style scoped>
  .materias-container {
    background-color: transparent;
    color: white;
    text-align: center;
    padding: 40px 20px;
    min-height: 100vh;
    font-family: 'Segoe UI', sans-serif;
  }
  
  .titulo {
    font-size: 2.5em;
    margin-bottom: 40px; /*margen entre el 'escoge una materia' y lo botones */
  }
  
  .materias-grid {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 30px; /*espacio entre los botones*/
  }
  
  .materia {
    background-color: white;
    color: black;
    padding: 15px;
    border-radius: 10px;
    width: 150px;
    cursor: pointer;
    transition: transform 0.2s ease;
  }
  
  .materia:hover {
    transform: scale(1.05);
  }
  
  .materia-img { /*pa las imagenes */
    width: 100%;
    height: 100px;
    object-fit: contain;
    margin-bottom: 10px;
    border-radius: 20px;
  }
  </style>
  