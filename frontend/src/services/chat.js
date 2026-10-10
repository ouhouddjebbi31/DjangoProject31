import api from './api'

export const sendChatMessage = (message, history) => api.post('/chat/', { message, history })
