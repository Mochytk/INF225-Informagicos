<template>
  <div>
    <!--Barra suprior-->
    <div class="barra-superior">
      <span class="bienvenida">
        Bienvenido, {{ nombreUsuario }}
      </span>
      <div class="nav-botones">
        <button class="nav-btn" @click="mostrarSeccionResultados">Ver resultados</button>
        <button class="nav-btn" @click="mostrarSeccionCrearEnsayo">Crear ensayo</button>
      </div>

      <button class="cerrar-sesion" @click="logout">Cerrar sesión</button>
    </div>
  </div>
<div v-if="mostrarResultados" class="resultados-contenedor">
  <!-- Globo de búsqueda -->
  <div class="globo-busqueda">
    <label for="curso">Curso:</label>
    <select id="curso" class="selector">
      <option>2do medio A</option>
      <option>2do medio B</option>
      <option>3ro medio</option>
      <option>4to medio</option>
    </select>

    <label for="prueba">N° prueba:</label>
    <select id="prueba" class="selector">
      <option>Comprensión lectora Nº 7</option>
      <option>Matemática Diagnóstico</option>
    </select>

    <button class="boton-buscar">Buscar</button>
  </div>

  <!-- Tabla y promedio debajo -->
  <div class="tabla-promedio-wrapper">
    <table class="tabla-resultados">
      <thead>
        <tr>
          <th>Nombre</th>
          <th>Apellido</th>
          <th>Puntaje</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(r, index) in resultados" :key="index">
          <td>{{ r.nombre }}</td>
          <td>{{ r.apellido }}</td>
          <td>{{ r.puntaje }}</td>
        </tr>
      </tbody>
    </table>

    <div class="promedio-box">
      <label for="promedio">Promedio</label>
      <input id="promedio" type="text" :value="promedio" readonly />
    </div>
  </div>
</div>
<div v-else class="creador-ensayos">
  <h1>Crear ensayo</h1>
  <p>Nota: la funcionalidad para crear y editar ensayos está en desarrollo.</p>
  <div class="botones">
    <RouterLink to="/docente/creador-ensayos">
      <button>Crear nuevo ensayo</button>
    </RouterLink>
    <RouterLink to="/docente/editor-ensayos">
      <button>Editar ensayo</button>
    </RouterLink>
  </div>
</div>


</template>

<script>
export default {
  data() {
    return {
      nombreUsuario: localStorage.getItem('username') || 'Docente',
      mostrarResultados: true,
      resultados: [
      { nombre: 'José', apellido: 'Yañez', puntaje: 750 },
      { nombre: 'Martín', apellido: 'Ferrera', puntaje: 930 },
      { nombre: 'Rodrigo', apellido: 'Caceres', puntaje: 1000 },
      { nombre: 'Sergio', apellido: 'Rojas', puntaje: 640 },
      { nombre: 'Jaime', apellido: 'Donoso', puntaje: 100 },
      { nombre: 'Dan', apellido: 'Gonzalez', puntaje: 820 },
      { nombre: 'Alonso', apellido: 'Fuenzalida', puntaje: 470 },
      { nombre: 'Sebastian', apellido: 'Albornoz', puntaje: 220 },
      { nombre: 'Ricardo', apellido: 'Salas', puntaje: 1000 },
      { nombre: 'José Luis', apellido: 'Martí', puntaje: 160 },
      { nombre: 'Viktor', apellido: 'Tapia', puntaje: 100 },
      { nombre: 'Mauricio', apellido: 'Solar', puntaje: 120 },
    ],
    }
  },
  computed: {
    promedio() {
    const puntajesValidos = this.resultados
      .map(r => parseFloat(r.puntaje))
      .filter(p => !isNaN(p) && isFinite(p));

    if (puntajesValidos.length === 0) return 0;

    const suma = puntajesValidos.reduce((a, b) => a + b, 0);
    return (suma / puntajesValidos.length).toFixed(1);
  }
},
  methods: {
    crearEnsayo() {
      // Aquí irá navegación o funcionalidad real
      alert("Funcionalidad para crear ensayo próximamente.");
    },
    mostrarSeccionResultados(){
      this.mostrarResultados = true;
    },
    mostrarSeccionCrearEnsayo(){
      this.mostrarResultados = false;
    },
    verResultados() {
      alert("Aquí se mostrarán los resultados de los alumnos.");
    },
    logout() {
      localStorage.clear();
      this.$router.push('/');
    }
  },
  mounted() {
    // Protección: si no está logeado, redirige
    if (!localStorage.getItem('token') || localStorage.getItem('rol') !== 'docente') {
      console.warn('Acceso restringido: no tienes permiso para ver esta página.');
      alert('Acceso restringido: no tienes permiso para ver esta página.');
      this.$router.push('/acceso-restringido');
    }
  }
}
</script>



<style scoped>

.barra-superior {
  background-color: white;
  color: #2c3e50;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 25px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  font-size: 1.1em;
  font-weight: bold;
}

.bienvenida {
  font-size: 1.2em;
  font-family: 'Segoe UI', sans-serif;
}

.creador-ensayos {
  text-align: center;
  padding: 40px;
  color: white;
  font-family: 'Segoe UI', sans-serif;
}

.nav-botones {
  display: flex;
  gap: 15px;
}

.nav-btn {
  background-color: #f4f4f4;
  border: 1px solid #ccc;
  border-radius: 8px;
  padding: 8px 16px;
  cursor: pointer;
  font-weight: normal;
  font-size: 0.95em;
}


.nav-btn:hover {
  background-color: #e0e0e0;
}

.cerrar-sesion {
  background-color: #3498db;
  border: none;
  color: white;
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 0.95em;
  cursor: pointer;
}

.cerrar-sesion:hover {
  background-color: #2980b9;
}

.dashboard-container {
  text-align: center;
  padding: 40px;
  color: white;
}

.botones button {
  margin: 10px;
  padding: 10px 20px;
  font-size: 18px;
  background-color: #2ecc71;
  border: none;
  border-radius: 10px;
  cursor: pointer;
}

.contenido-docente {
  padding: 30px;
  color: white;
}

.botones button:hover {
  background-color: #27ae60;
}

.resultados-contenedor {
  display: flex;
  flex-direction: column;
  justify-content: center;
  margin-top: 30px;
  gap: 30px;
}

.globo-busqueda {
  background-color: white;
  color: #2c3e50;
  padding: 20px 30px;
  border-radius: 30px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  display: flex;
  gap: 15px;
  align-items: center;
  flex-wrap: wrap;
}

.selector {
  padding: 8px 12px;
  border-radius: 8px;
  border: 1px solid #ccc;
  font-size: 1em;
}

.boton-buscar {
  background-color: #3498db;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 20px;
  font-size: 1em;
  cursor: pointer;
}

.boton-buscar:hover {
  background-color: #2980b9;
}

.tabla-contenedor {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin: 30px 60px;
  flex-wrap: wrap;
}

.tabla-resultados {
  border-collapse: collapse;
  width: 600px;
  background-color: white;
  font-size: 1em;
  color: black;
}

.tabla-resultados th,
.tabla-resultados td {
  border: 1px solid black;
  padding: 10px;
  text-align: left;
}

.tabla-resultados th {
  background-color: #b8e994; /* verde pastel */
}

.promedio-box {
  background-color: white;
  padding: 20px;
  border: 2px solid black;
  border-radius: 10px;
  font-size: 1.2em;
  color: black;
  display: flex;
  flex-direction: column;
  align-items: center;
  height: fit-content;
  margin-top: 20px;
}
.promedio-box input {
  margin-top: 10px;
  width: 100px;
  text-align: center;
  font-size: 1.1em;
  border: 1px solid black;
}

.tabla-promedio-wrapper {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  gap: 30px;
  flex-wrap: wrap;
}

</style>
