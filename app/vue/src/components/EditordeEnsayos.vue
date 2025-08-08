<template>
    <div class="editor">
        <h1>Editor de Ensayos</h1>
        <p>Nota: la funcionalidad para editar ensayos está en desarrollo.</p>
        <button class="boton" @click="mostrar">Mostrar Ensayos</button>
        <p>Haz clic en el botón para mostrar los ensayos disponibles.</p>
        <p>Recuerda que esta funcionalidad está en desarrollo y puede no estar completamente implementada.</p>
    </div>
</template>

<script>
import axios from 'axios';

export default {
    data() {
        return {
            ensayos: [],
            error: ''
        };
    },
    methods: {
        async mostrar() {
            try {
                const response = await axios.get('http://127.0.0.1:8000/api/', {
                    headers: {
                        Authorization: `Bearer ${localStorage.getItem('token')}`
                    }
                });
                this.ensayos = response.data;
                this.mostrarTabla = true;
            } catch (error) {
                console.error("Error al obtener los ensayos:", error);
                alert("Error al obtener los ensayos.");
            }
        },
        mounted() {
            // Protección: si no está logeado, redirige
            if (!localStorage.getItem('token')) {
                this.$router.push('/acceso-restringido');
            }
        },
    }
};
</script>

<style scoped>
.editor {
    font-family: 'Segoe UI', sans-serif;
    color: #ffffff;
    padding: 20px;
}
h1 {
    color: #ffffff;
    text-align: center;
    margin-top: 80px;
    font-family: 'Segoe UI', sans-serif;
}
p {
    color: #ffffff;
    line-height: 1.6;
    font-family: 'Segoe UI', sans-serif;
}
.boton {
    background-color: #3498db;
    color: white;
    padding: 10px 20px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
}
</style>