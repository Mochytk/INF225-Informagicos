import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:8000/api/',
});

export const login = async (email, password) => {
    const response = await api.post('/usuarios/login/', { email, password });
    return response.data;
};

export const logout = () => {
    localStorage.removeItem('token');
};