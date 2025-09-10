// src/api/ensayos.js
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api', // ajusta si usas otro base
  headers: { 'Content-Type': 'application/json' },
  timeout: 10000,
});

function authHeader() {
  const token = localStorage.getItem('token');
  return token ? { Authorization: 'Token ' + token } : {};
}

export async function fetchAllEnsayos() {
  try {
    const resp = await api.get('/exams/'); // intentamos el viewset /exams/
    return resp.data;
  } catch (err) {
    // fallback si tu backend expone /ensayos/
    const resp = await api.get('/ensayos/');
    return resp.data;
  }
}
export async function fetchEnsayo(id) {
  // intenta /exams/:id/ y si falla, /ensayos/:id/
  try {
    const resp = await api.get(`/exams/${id}/`, { headers: authHeader() });
    return resp.data;
  } catch (err) {
    const resp = await api.get(`/ensayos/${id}/`, { headers: authHeader() });
    return resp.data;
  }
}

export async function submitEnsayo(ensayoId, respuestas) {
  const url = `http://127.0.0.1:8000/api/ensayos/${ensayoId}/submit/`;
  const resp = await axios.post(url, { respuestas }, { headers: { ...authHeader(), 'Content-Type': 'application/json' } });
  return resp.data;
}

export async function getResultsSummary(ensayoId) {
  const url = `${API_BASE}/ensayos/${ensayoId}/results/summary/`;
  const resp = await axios.get(url, { headers: { ...authHeader() } });
  return resp.data;
}

export async function getQuestionBreakdown(ensayoId, preguntaId) {
  const url = `${API_BASE}/ensayos/${ensayoId}/questions/${preguntaId}/breakdown/`;
  const resp = await axios.get(url, { headers: { ...authHeader() } });
  return resp.data;
}