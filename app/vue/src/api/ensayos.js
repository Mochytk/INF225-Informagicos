// src/api/ensayos.js
import axios from 'axios';

const API_BASE = 'http://127.0.0.1:8000/api'; // <- Asegúrate que coincide con tu backend

function authHeader() {
  const token = localStorage.getItem('token');
  return token ? { Authorization: 'Token ' + token } : {};
}

// obtiene listado de ensayos (intenta /exams/ y si falla usa /ensayos/)
export async function fetchAllEnsayos() {
  try {
    const resp = await axios.get(`${API_BASE}/exams/`, { headers: { ...authHeader() } });
    return resp.data;
  } catch (err) {
    const resp = await axios.get(`${API_BASE}/ensayos/`, { headers: { ...authHeader() } });
    return resp.data;
  }
}

// obtiene un ensayo específico
export async function fetchEnsayo(id) {
  try {
    const resp = await axios.get(`${API_BASE}/exams/${id}/`, { headers: { ...authHeader() } });
    return resp.data;
  } catch (err) {
    const resp = await axios.get(`${API_BASE}/ensayos/${id}/`, { headers: { ...authHeader() } });
    return resp.data;
  }
}

// envía respuestas de un ensayo
export async function submitEnsayo(ensayoId, respuestas) {
  const url = `${API_BASE}/ensayos/${ensayoId}/submit/`;
  const resp = await axios.post(url, { respuestas }, { headers: { 'Content-Type': 'application/json', ...authHeader() } });
  return resp.data;
}

// obtiene resumen (by_type, by_question si backend lo devuelve)
export async function getResultsSummary(ensayoId) {
  const url = `${API_BASE}/ensayos/${ensayoId}/results/summary/`;
  const resp = await axios.get(url, { headers: { ...authHeader() } });
  return resp.data;
}

// obtiene desglose de una pregunta
export async function getQuestionBreakdown(ensayoId, preguntaId) {
  const url = `${API_BASE}/ensayos/${ensayoId}/questions/${preguntaId}/breakdown/`;
  const resp = await axios.get(url, { headers: { ...authHeader() } });
  return resp.data;
}
