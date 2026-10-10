import api from './api'
export const login = (data) => api.post('/auth/token/', data)
export const register = (data) => api.post('/auth/register/', data)
export const getMe = () => api.get('/me/')
export const updateMe = (data) => api.patch('/me/', data)
