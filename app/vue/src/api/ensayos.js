// src/api/ensayos.js
import axios from 'axios';

const API_BASE = 'http://127.0.0.1:8000/api';

// cliente axios reutilizable
const apiClient = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
});

function authHeaders() {
  const token = localStorage.getItem('token');
  return token ? { Authorization: `Token ${token}` } : {};
}

export async function fetchAllEnsayos() {
  try {
    const resp = await apiClient.get('/exams/', { headers: authHeaders() });
    return resp.data;
  } catch (err) {
    const resp = await apiClient.get('/ensayos/', { headers: authHeaders() });
    return resp.data;
  }
}

export async function fetchEnsayo(id) {
  try {
    const resp = await apiClient.get(`/exams/${id}/`, { headers: authHeaders() });
    return resp.data;
  } catch (err) {
    const resp = await apiClient.get(`/ensayos/${id}/`, { headers: authHeaders() });
    return resp.data;
  }
}

export async function submitEnsayo(ensayoId, respuestas) {
  const url = `/ensayos/${ensayoId}/submit/`;
  // El backend acepta { "respuestas": [...] } o un array; ajusta si tu frontend manda distinto
  const payload = { respuestas };
  const resp = await apiClient.post(url, payload, { headers: { 'Content-Type': 'application/json', ...authHeaders() } });
  return resp.data;
}

export async function getResultsSummary(ensayoId) {
  const url = `/ensayos/${ensayoId}/results/summary/`;
  const resp = await apiClient.get(url, { headers: authHeaders() });
  return resp.data;
}

export async function getQuestionBreakdown(ensayoId, preguntaId) {
  const url = `/ensayos/${ensayoId}/questions/${preguntaId}/breakdown/`;
  const resp = await apiClient.get(url, { headers: authHeaders() });
  return resp.data;
}

export async function getEnsayosCompletados() {
  const res = await apiClient.get('/ensayos/completados/', { headers: authHeaders() });
  return res.data;
}

export async function getRevision(ensayoId, resultadoId) {
  const res = await apiClient.get(`/ensayos/${ensayoId}/results/${resultadoId}/review/`, { headers: authHeaders() });
  return res.data;
}

export async function editarExplicacion(preguntaId, payload) {
  // Uso PATCH por ser partial update; si tu backend espera PUT, cámbialo a apiClient.put(...)
  const res = await apiClient.patch(`/preguntas/${preguntaId}/explicacion/`, payload, { headers: authHeaders() });
  return res.data;
}
