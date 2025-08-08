<template>
    <div>
      <h1>Ensayos PAES</h1>
      <div v-for="ensayo in ensayos" :key="exam.id">
        {{ exam.title }}
      </div>
    </div>
  </template>
  
  <script>
  import { getEnsayos } from '../api/ensayos.js';
  
  export default {
    data() {
      return { ensayos: [] };
    },
    async created() {
      this.ensayos = (await getEnsayos()).data;
    }
  };
  </script>