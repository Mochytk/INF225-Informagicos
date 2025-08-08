<template>
    <div class="crear_ensayos">
        <h1>Crear Ensayos</h1>
        <form @submit.prevent="crearEnsayo">
            <div>
                <label for="nombre">Nombre del ensayo: </label>
                <input type="text" id="nombre" v-model="ensayo.nombre" required />
            </div>
            <div>
                <label for="materia">Materia: </label>
                <select id="materia" v-model="ensayo.materia" required>
                    <option value="" disabled selected>Selecciona una materia</option>
                    <option value="Matematicas">Matemáticas</option>
                    <option value="Lenguaje">Lenguaje</option>
                    <option value="Ciencias">Ciencias</option>
                    <option value="Historia">Historia</option>
                </select>
            </div>
            <button class="boton" type="submit" @click="alerta()">Crear Ensayo</button>
        </form>
        <p>Nota: Aún hay problemas con la comunicación con el backend, por lo que esta sección aún no funciona apropiadamente
            (queda pendiente para el Hito 5).</p>
    </div>
</template>

<script>
import axios from 'axios';

export default {
    data() {
        return {
            ensayo: {
                nombre: '',
                materia: '',
                creador: this.obtenerCreador(),
            }
        };
    },
    methods: {
        crearEnsayo() {
            axios.post('http://127.0.1:8000/api/', this.ensayo, {
                headers: {
                    Authorization: `Bearer ${localStorage.getItem('token')}`
                }
            })
            .then(response => {
                console.log("Ensayo creado exitosamente:", response.data);
                this.ensayo = { nombre: '', materia: '', creador: this.obtenerCreador() }; // Resetear formulario
                alert("Ensayo creado exitosamente.");
                this.$router.push('/docente/editor-ensayos'); // Redirigir al editor de ensayos
            })
            .catch(error => {
                console.error("Error al crear el ensayo:", error);
                alert("Error al crear el ensayo. Por favor, inténtalo de nuevo.");
            });
            console.log('Ensayo creado:', this.ensayo);
        },
        obtenerCreador() {
            return localStorage.getItem('username') || 'Docente';
        }
    }
};
</script>

<style scoped>
.crear_ensayos {
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