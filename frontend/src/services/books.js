import api from './api'
export const getBooks = (params) => api.get('/books/', { params })
export const getBook = (id) => api.get(`/books/${id}/`)
export const getGenres = () => api.get('/genres/')
export const getReviews = (id) => api.get(`/books/${id}/reviews/`)
export const addReview = (id, data) => api.post(`/books/${id}/reviews/`, data)
export const getSimilar = (id) => api.get(`/books/${id}/similar/`)
