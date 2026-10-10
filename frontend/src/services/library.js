import api from './api'
export const getLibrary = () => api.get('/reading-list/')
export const addToLibrary = (data) => api.post('/reading-list/', data)
export const updateLibrary = (id, data) => api.patch(`/reading-list/${id}/`, data)
export const removeFromLibrary = (id) => api.delete(`/reading-list/${id}/`)
