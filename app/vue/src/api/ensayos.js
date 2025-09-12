
import axios from 'axios';

const API_BASE = 'http://127.0.0.1:8000/api';

function authHeader() {
  const token = localStorage.getItem('token');
  return token ? { Authorization: 'Token ' + token } : {};
}

export async function fetchAllEnsayos() {
  try {
    const resp = await axios.get(`${API_BASE}/exams/`, { headers: { ...authHeader() } });
    return resp.data;
  } catch (err) {
    const resp = await axios.get(`${API_BASE}/ensayos/`, { headers: { ...authHeader() } });
    return resp.data;
  }
}

export async function fetchEnsayo(id) {
  try {
    const resp = await axios.get(`${API_BASE}/exams/${id}/`, { headers: { ...authHeader() } });
    return resp.data;
  } catch (err) {
    const resp = await axios.get(`${API_BASE}/ensayos/${id}/`, { headers: { ...authHeader() } });
    return resp.data;
  }
}

export async function submitEnsayo(ensayoId, respuestas) {
  const url = `${API_BASE}/ensayos/${ensayoId}/submit/`;
  const resp = await axios.post(url, { respuestas }, { headers: { 'Content-Type': 'application/json', ...authHeader() } });
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
