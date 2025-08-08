<template>
    <button class="volver" @click="goBack">🔙 Volver</button>
</template>

  <script setup>
  import { useRouter } from 'vue-router';
  
  const router = useRouter();
  
  function goBack() {
    router.back();
  }
  </script>
  
  <style scoped>
  .volver {
    margin: 20px;
    padding: 10px 18px;
    font-size: 1em;
    background-color: #bdc3c7;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    transition: background-color 0.3s ease, transform 0.3s ease;
  }
  .volver:hover {
    background-color: #95a5a6;
    transform: scale(1.02);
  }
  </style>
  