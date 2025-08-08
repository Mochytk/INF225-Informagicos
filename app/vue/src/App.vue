<template>
  <div class="fondo-pizarra">
    <LoginForm />
    <router-view />
    <VolverButton v-if="$route.path !== '/' && $route.path !== '/acceso-restringido'" class="volver-inferior" />
  </div>
</template>


<style>
html, body {
  margin: 0;
  padding: 0;
}
</style>

<style>
.fondo-pizarra {
  min-height: 100vh;
  background-image: url('/img/fondo_pizarra.png');
  background-size: 100% 100%;
  background-position: center;
  background-repeat: no-repeat;
  background-attachment: fixed;
}

.volver-inferior {
  position: fixed;
  bottom: 20px;
  left: 20px;
  z-index: 1000;
}

@media (max-width: 600px) {
  .fondo-pizarra {
    background-size: cover;
  }
  .volver-inferior {
    bottom: 10px;
    left: 10px;
  }
}

</style>

<script setup>
  import VolverButton from './components/VolverButton.vue';
</script>

