<template>
  <div class="home-container">
    <h1 class="titulo">Bienvenido</h1>
    <div class="contenido">
      <div class="materias">
        <img :src="imgs.lenguaje" alt="Lenguaje" />
        <img :src="imgs.matematicas" alt="Matemáticas" />
        <img :src="imgs.historia" alt="Historia" />
        <img :src="imgs.ciencias" alt="Ciencias" />
      </div>

      <div class="login">
        <h2>Iniciar Sesión</h2>
        <form @submit.prevent="login">
          <div class="entrada">
            <label for="email">Correo: </label>
            <input type="email" v-model="email" required />
          </div>

          <div class="entrada">
            <label for="password">Contraseña: </label>
            <input type="password" v-model="contraseña" required />
          </div>

          <button class="main-button" type="submit">Ingresar</button>

          <div v-if="error" style="color: red;">{{ error }}</div>
        </form>
      </div>
    </div>

    <div class="info-botones">
      <router-link to="/como-funciona">
        <button class="secondary-button">Cómo funciona la plataforma</button>
      </router-link>
      <router-link to="/about">
        <button class="secondary-button">Sobre nosotros</button>
      </router-link>
    </div>
  </div>
</template>



<script>
import axios from 'axios'

export default {
  data() {
    return {
      email: '',
      contraseña: '',
      error: '',
      imgs :  {
        lenguaje: '/img/lenguaje.jpg',
        matematicas: '/img/matematicas.jpg',
        historia: '/img/historia.jpg',
        ciencias: '/img/ciencias.jpg',
      }
    }
  },
  methods: {
    async login() {
      try {
        const response = await axios.post('http://127.0.0.1:8000/api/login/', {
          email: this.email,
          contraseña: this.contraseña
        });

        const { token, rol, username } = response.data;

        // Guardamos token y rol (puedes usar localStorage o Vuex)
        localStorage.setItem('token', token);
        localStorage.setItem('rol', rol);

        // Redirigir según el rol
        if (rol.toLowerCase() === 'alumno') {
          this.$router.push('/alumno');
        } else if (rol.toLowerCase() === 'docente') {
          this.$router.push('/docente');
        }
        else{
          console.warn('Rol no reconocido:', rol);
          this.error = 'Rol no reconocido. Contacte al administrador.';
        }

      } catch (err) {
        console.error('Error de inicio de sesión', err.response?.data || err.message);
        this.error = err.response?.data?.error || 'Ocurrió un error al iniciar sesión';
      }
    }
  }
}

</script>


<style scoped>
.home-container {
  color: white;
  padding: 40px 20px;
  min-height: 100vh;
  font-family: 'Segoe UI', sans-serif;
  text-align: center;
}

.titulo {
  font-size: 3em;
  margin-bottom: 40px;
}

.contenido {
  display: flex;
  justify-content: center;
  gap: 60px;
  flex-wrap: wrap;
  align-items: center;
}

.materias {
  display: grid;
  grid-template-columns: repeat(2, 130px);
  gap: 20px;
}

.materias img {
  width: 130px;
  height: 130px;
  border-radius: 12px;
  object-fit: cover;
  box-shadow: 0 0 10px #00000044;
}

.login {
  display: flex;
  flex-direction: column;
  align-items: left;
  gap: 15px;
}

.entrada {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}
.entrada label {
  width: 110px;
  text-align: right;
  margin-right: 10px;
}
.entrada input {
  flex: 1;
  font-size: 1.1em;
  padding: 6px 10px;
}

.info-botones {
  margin-top: 50px;
  display: flex;
  justify-content: center;
  gap: 10px;
  flex-direction: column;
  align-items: center;
  flex-wrap: wrap;
}

.button-group, .info-buttons {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin: 20px auto;
  max-width: 300px;
}

.main-button, .secondary-button {
  padding: 12px 20px;
  font-size: 1em;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.main-button {
  background-color: #3498db;
  color: white;
}
.main-button:hover {
  background-color: #2980b9;
}

.secondary-button {
  background-color: #ecf0f1;
  color: #2c3e50;
}
.secondary-button:hover {
  background-color: #bdc3c7;
}

</style>
