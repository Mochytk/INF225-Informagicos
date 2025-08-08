import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:8000/api/',
    headers: { 'Authorization': 'Bearer ' + localStorage.getItem('token') }
});

export const getEnsayos = () => api.get('/ensayos/');
export const subirIntento = (data) => api.post('/intentos/', data);
