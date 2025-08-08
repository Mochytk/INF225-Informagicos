import { createRouter, createWebHistory } from 'vue-router';
import HomePage from '../components/HomePage.vue';
import ComoFunciona from '../components/ComoFunciona.vue';
import About from '../components/About.vue';
import SeleccionarMateria from '../components/SeleccionarMateria.vue'; 
import Historial from '../components/Historial.vue';
import Ranking from '../components/Ranking.vue';
import ResultadosAlumno from '../components/ResultadosAlumno.vue';
import AlumnoDashboard from '../components/AlumnoDashboard.vue';
import DocenteDashboard from '../components/DocenteDashboard.vue';
import Restringido from '../components/Restringido.vue';
import CreadordeEnsayos from '@/components/CreadordeEnsayos.vue';
import EditordeEnsayos from '@/components/EditordeEnsayos.vue';
import Ensayo from '@/components/Ensayo.vue';

const routes = [
  { path: '/', component: HomePage },
  //{ path: '/:rol', component: Dashboard },
  { path: '/como-funciona', component: ComoFunciona},
  { path: '/about', component: About},
  { path: '/docente/historial', component: Historial},
  { path: '/docente/ranking', component: Ranking},
  { path: '/alumno/resultados', component: ResultadosAlumno},
  { path: '/alumno/materias', component: SeleccionarMateria },
  { path: '/alumno', component: AlumnoDashboard},
  { path: '/docente', component: DocenteDashboard},
  { path: '/acceso-restringido', component: Restringido},
  { path: '/docente/creador-ensayos', component: CreadordeEnsayos},
  { path: '/docente/editor-ensayos', component: EditordeEnsayos},
  { path: '/alumno/ensayo', component: Ensayo},
  { path: '/docente/editor-ensayos/:id', component: EditordeEnsayos, props: true},
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
