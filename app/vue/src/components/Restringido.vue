<template>
    <div class="acceso-restringido">
        <h1>Acceso restringido</h1>
        <p>Lo sentimos, no tienes acceso a esta sección.</p>
        <p>Por favor, contacta al administrador si crees que esto es un error.</p>
        <p>Si eres un alumno, por favor inicia sesión como alumno.</p>
        <p>Si eres un profesor, por favor inicia sesión como profesor.</p>

        <RouterLink to="/">
            <button>Regresar al inicio</button>
        </RouterLink>
        <RouterLink v-if="rol === 'docente'" to="/docente">
            <button>Volver al apartado de Docente</button>
        </RouterLink>
        <RouterLink v-else-if="rol === 'alumno'" to="/alumno">
            <button>Volver al apartado de Alumno</button>
        </RouterLink>
    </div>
</template>

<style scoped>
.acceso-restringido {
    color: white;
    padding: 40px 20px;
    min-height: 100vh;
    font-family: 'Segoe UI', sans-serif;
    text-align: center;
}

button {
    background-color: #3498db;
    color: white;
    padding: 10px 20px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-size: 16px;
}
button:hover {
    background-color: #2980b9;
}

</style>