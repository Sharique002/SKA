import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { BrainCircuit } from 'lucide-react'
import Layout from './components/Layout'
import Home from './pages/Home'
import Upload from './pages/Upload'
import Query from './pages/Query'
import Documents from './pages/Documents'
import Statistics from './pages/Statistics'
import api from './services/api'

function App() {
  const [backendOnline, setBackendOnline] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    checkBackendHealth()
    const interval = setInterval(checkBackendHealth, 30000)
    return () => clearInterval(interval)
  }, [])

  const checkBackendHealth = async () => {
    try {
      const response = await api.get('/health')
      setBackendOnline(response.status === 200)
    } catch (error) {
      setBackendOnline(false)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center p-6">
        <div className="card max-w-sm w-full overflow-hidden text-center">
          <div className="accent-strip" />
          <div className="p-8">
            <div className="mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-lg border-2 border-ink bg-secondary-500 text-white shadow-[4px_4px_0_#101010]">
              <BrainCircuit size={34} strokeWidth={2.4} />
            </div>
            <div className="mx-auto h-12 w-12 animate-spin rounded-full border-4 border-primary-500 border-t-transparent"></div>
            <p className="mt-5 text-sm font-black uppercase text-gray-700">Loading SKA workspace</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <Router>
      <Layout backendOnline={backendOnline}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/upload" element={<Upload />} />
          <Route path="/query" element={<Query />} />
          <Route path="/documents" element={<Documents />} />
          <Route path="/statistics" element={<Statistics />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App
