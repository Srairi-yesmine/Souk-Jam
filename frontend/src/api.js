import axios from 'axios'

const API_BASE_URL = 'http://localhost:5000'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000  // 60 second timeout for large file uploads
})

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  // IMPORTANT: Let axios/browser handle Content-Type for FormData automatically
  // Only set Content-Type for non-FormData requests
  if (!(config.data instanceof FormData)) {
    config.headers['Content-Type'] = 'application/json'
  } else {
    // For FormData, explicitly DELETE Content-Type to let browser set it with boundary
    delete config.headers['Content-Type']
  }
  return config
})

// Auth API
export const authAPI = {
  login: (email, password) => api.post('/auth/login', { email, password }),
  register: (data) => api.post('/auth/register', data),
  getUsers: () => api.get('/auth/users'),
  getUser: (id) => api.get(`/auth/users/${id}`),
  uploadProfilePhoto: (id, file) => {
    const formData = new FormData()
    formData.append('profile_photo', file)
    return api.put(`/auth/users/${id}/profile-photo`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  }
}

// Instruments API
export const instrumentsAPI = {
  getAll: (params) => api.get('/instruments', { params }),
  getOne: (id) => api.get(`/instruments/${id}`),
  create: (data) => api.post('/instruments', data),
  update: (id, data) => api.put(`/instruments/${id}`, data),
  delete: (id) => api.delete(`/instruments/${id}`)
}

// Rentals API
export const rentalsAPI = {
  getAll: (params) => api.get('/rentals', { params }),
  getOne: (id) => api.get(`/rentals/${id}`),
  create: (data) => api.post('/rentals', data),
  counterOffer: (id, data) => api.patch(`/rentals/${id}/counter-offer`, data),
  accept: (id) => api.patch(`/rentals/${id}/accept`, {}),
  reject: (id) => api.patch(`/rentals/${id}/reject`, {}),
  getByRenter: (id) => api.get(`/rentals/by-renter/${id}`),
  getByOwner: (id) => api.get(`/rentals/by-owner/${id}`)
}

// Jam API
export const jamAPI = {
  discover: (limit = 5) => api.get('/jam/discover', { params: { limit } }),
  sendRequest: (userId) => api.post(`/jam/request/${userId}`, {}),
  skipUser: (userId) => api.post(`/jam/skip/${userId}`, {}),
  getMatches: () => api.get('/jam/matches')
}

export default api
