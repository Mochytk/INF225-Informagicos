<template>
    <div class="dashboard-container">
    <h1>Bienvenido, {{ nombreUsuario }}</h1>
    <p>Rol: Alumno</p>

        <div class="botones">
            <RouterLink to="/alumno/materias">
                <button>Realizar Ensayo</button>
            </RouterLink>
            <RouterLink to="/alumno/resultados">
                <button>Ver Resultados</button>
            </RouterLink>
            <button @click="logout">Cerrar Sesión</button>
        </div>
    </div>
</template>

<script>
export default {
    data() {
        return {
            nombreUsuario: localStorage.getItem('username') || 'Alumno'
        }
    },
    methods: {
        verResultados() {
            alert("Aquí se mostrarán tus resultados.");
        },
        logout() {
            localStorage.clear();
            this.$router.push('/');
        }
    },
    mounted() {
      // Protección: si no está logeado, redirige
    if (!localStorage.getItem('token') || localStorage.getItem('rol') !== 'alumno') {
        console.warn('Acceso restringido: no tienes permiso para ver esta página.');
        alert('Acceso restringido: no tienes permiso para ver esta página.');
        this.$router.push('/acceso-restringido');
        }
    }
}
</script>

<style scoped>
.dashboard-container {
    font-family: 'Segoe UI', sans-serif;
    color: white;
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

.botones button:hover {
    background-color: #27ae60;
}
</style>  