import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000,
})

// Upload Document
export const uploadDocument = async (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/upload/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

// Get Upload Status
export const getUploadStatus = async (docId) => {
  return api.get(`/upload/status/${docId}`)
}

// Query Knowledge Base
export const queryKnowledge = async (query, topK = 5) => {
  return api.post('/query/', { query, top_k: topK })
}

// Search Documents
export const searchDocuments = async (keywords) => {
  return api.post('/query/search', { keywords })
}

// List Documents
export const listDocuments = async () => {
  return api.get('/admin/documents')
}

// Get Document Details
export const getDocumentDetails = async (docId) => {
  return api.get(`/admin/documents/${docId}`)
}

// Delete Document
export const deleteDocument = async (docId) => {
  return api.delete(`/admin/documents/${docId}`)
}

// Get Statistics
export const getStatistics = async () => {
  return api.get('/admin/stats')
}

// Clear All Data
export const clearAllData = async () => {
  return api.post('/admin/clear')
}

export default api
