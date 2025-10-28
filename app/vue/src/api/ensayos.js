
import axios from 'axios';

const API_BASE = 'http://127.0.0.1:8000/api';


const api = axios.create({
  baseURL: API_BASE,

});


function authHeader() {
  const token = localStorage.getItem('token');
  return token ? { Authorization: 'Token ' + token } : {};
}



export async function fetchAllEnsayos() {
  try {
    const resp = await api.get('/exams/', { headers: { ...authHeader() } });
    return resp.data;
  } catch (err) {

    const resp = await api.get('/ensayos/', { headers: { ...authHeader() } });
    return resp.data;
  }
}

export async function fetchEnsayo(id) {
  try {
    const resp = await api.get(`/exams/${id}/`, { headers: { ...authHeader() } });
    return resp.data;
  } catch (err) {
    const resp = await api.get(`/ensayos/${id}/`, { headers: { ...authHeader() } });
    return resp.data;
  }
}

export async function submitEnsayo(ensayoId, respuestas) {
  const url = `/ensayos/${ensayoId}/submit/`;
  const resp = await api.post(url, Array.isArray(respuestas) ? respuestas : { respuestas }, {
    headers: { 'Content-Type': 'application/json', ...authHeader() }
  });
  return resp.data;
}

export async function getResultsSummary(ensayoId) {
  const url = `/ensayos/${ensayoId}/results/summary/`;
  const resp = await api.get(url, { headers: { ...authHeader() } });
  return resp.data;
}

export async function getQuestionBreakdown(ensayoId, preguntaId) {
  const url = `/ensayos/${ensayoId}/questions/${preguntaId}/breakdown/`;
  const resp = await api.get(url, { headers: { ...authHeader() } });
  return resp.data;
}

export async function getEnsayosCompletados() {
  const res = await api.get('/ensayos/completados/', { headers: { ...authHeader() } });
  return res.data;
}

export async function getRevision(ensayoId, resultadoId) {
  const res = await api.get(`/ensayos/${ensayoId}/results/${resultadoId}/review/`, { headers: { ...authHeader() } });
  return res.data;
}


export async function editarExplicacion(preguntaId, payload) {
  const url = `/preguntas/${preguntaId}/explicacion/`;


  const body = {};
  if ('texto' in payload) body.texto = payload.texto;
  if ('url' in payload) body.url = payload.url;
  if ('explicacion_texto' in payload) body.texto = payload.explicacion_texto;
  if ('explicacion_url' in payload) body.url = payload.explicacion_url;

  const res = await api.patch(url, body, { headers: { 'Content-Type': 'application/json', ...authHeader() } });
  return res.data;
}
