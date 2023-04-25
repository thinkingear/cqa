import axios from 'axios';

axios.defaults.withCredentials = true;
const service = axios.create({
    baseURL: 'http://localhost:8080',
    timeout: 10000,
});

export default service;
