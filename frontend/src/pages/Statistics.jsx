import { useEffect, useState } from 'react'
import { getStatistics, clearAllData } from '../services/api'
import { AlertTriangle, BarChart3, Database, FileText, Layers, RefreshCw, Trash2 } from 'lucide-react'

function Statistics() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [clearing, setClearing] = useState(false)
  const [confirmClear, setConfirmClear] = useState(false)

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      setLoading(true)
      const response = await getStatistics()
      setStats(response.data)
    } catch (error) {
      console.error('Error fetching stats:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleClearData = async () => {
    if (!confirmClear) {
      setConfirmClear(true)
      return
    }

    setClearing(true)
    try {
      await clearAllData()
      alert('All data cleared successfully!')
      setConfirmClear(false)
      fetchStats()
    } catch (error) {
      alert('Error clearing data: ' + error.message)
    } finally {
      setClearing(false)
    }
  }

  const overviewMetrics = [
    { icon: FileText, label: 'Documents', value: stats?.total_documents || 0, tone: 'bg-white' },
    { icon: Layers, label: 'Text chunks', value: stats?.total_chunks || 0, tone: 'bg-[#e8f0ff]' },
    { icon: Database, label: 'Storage MB', value: stats?.total_storage_mb || 0, tone: 'bg-[#fff3c9]' },
    { icon: BarChart3, label: 'Vectors', value: stats?.vector_db?.total_vectors || 0, tone: 'bg-[#ffe1cc]' },
  ]

  if (loading) {
    return (
      <div className="toolbar-panel p-12 text-center">
        <div className="mx-auto h-12 w-12 animate-spin rounded-full border-4 border-secondary-500 border-t-transparent" />
      </div>
    )
  }

  return (
    <div className="animate-fade-in space-y-8">
      <section className="card overflow-hidden">
        <div className="accent-strip" />
        <div className="flex flex-col gap-5 p-6 lg:flex-row lg:items-center lg:justify-between">
          <div className="flex items-center gap-4">
            <div className="flex h-14 w-14 items-center justify-center rounded-lg border-2 border-ink bg-secondary-500 text-white">
              <BarChart3 size={30} strokeWidth={2.5} />
            </div>
            <div>
              <h1 className="text-3xl font-black text-ink">System Analytics</h1>
              <p className="font-semibold text-gray-600">Index, storage, and processing status</p>
            </div>
          </div>
          <button onClick={fetchStats} className="btn-secondary">
            <RefreshCw size={18} />
            Refresh
          </button>
        </div>
      </section>

      {stats && (
        <>
          <section className="grid grid-cols-1 gap-5 sm:grid-cols-2 xl:grid-cols-4">
            {overviewMetrics.map((metric) => (
              <div key={metric.label} className={`card p-5 ${metric.tone}`}>
                <div className="mb-4 flex h-11 w-11 items-center justify-center rounded-md border-2 border-ink bg-white">
                  <metric.icon size={23} strokeWidth={2.4} />
                </div>
                <div className="text-3xl font-black text-ink">{metric.value}</div>
                <div className="mt-1 text-sm font-black uppercase text-gray-700">{metric.label}</div>
              </div>
            ))}
          </section>

          {stats.status_breakdown && (
            <section>
              <h2 className="mb-4 text-2xl font-black text-ink">Document Status</h2>
              <div className="grid grid-cols-1 gap-5 sm:grid-cols-3">
                <div className="card bg-green-100 p-6">
                  <p className="text-sm font-black uppercase text-green-800">Processed</p>
                  <p className="mt-2 text-4xl font-black text-green-900">
                    {stats.status_breakdown.processed || 0}
                  </p>
                </div>
                <div className="card bg-[#fff3c9] p-6">
                  <p className="text-sm font-black uppercase text-yellow-800">Processing</p>
                  <p className="mt-2 text-4xl font-black text-yellow-900">
                    {stats.status_breakdown.processing || 0}
                  </p>
                </div>
                <div className="card bg-red-100 p-6">
                  <p className="text-sm font-black uppercase text-red-800">Failed</p>
                  <p className="mt-2 text-4xl font-black text-red-900">
                    {stats.status_breakdown.failed || 0}
                  </p>
                </div>
              </div>
            </section>
          )}

          {stats.vector_db && (
            <section>
              <h2 className="mb-4 text-2xl font-black text-ink">Vector Database</h2>
              <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
                <div className="card bg-[#e8f0ff] p-6">
                  <p className="text-sm font-black uppercase text-gray-600">Total vectors</p>
                  <p className="mt-2 text-4xl font-black text-secondary-600">
                    {stats.vector_db.total_vectors || 0}
                  </p>
                </div>
                <div className="card bg-white p-6">
                  <p className="text-sm font-black uppercase text-gray-600">Index type</p>
                  <p className="mt-2 text-2xl font-black text-ink">
                    {stats.vector_db.index_type || 'Unknown'}
                  </p>
                  <p className="mt-2 font-black text-gray-500">Dimension: {stats.vector_db.dimension || 'N/A'}</p>
                </div>
              </div>
            </section>
          )}

          <section>
            <h2 className="mb-4 text-2xl font-black text-ink">System Actions</h2>
            <div className="toolbar-panel space-y-4 p-5">
              <button onClick={fetchStats} className="btn-primary w-full">
                <RefreshCw size={18} />
                Refresh statistics
              </button>

              {!confirmClear ? (
                <button
                  onClick={handleClearData}
                  className="inline-flex min-h-[2.75rem] w-full items-center justify-center gap-2 rounded-md border-2 border-ink bg-red-600 px-4 py-2 font-black text-white shadow-[4px_4px_0_#101010] transition-all hover:translate-x-0.5 hover:translate-y-0.5 hover:shadow-[2px_2px_0_#101010]"
                >
                  <Trash2 size={18} />
                  Clear all data
                </button>
              ) : (
                <div className="rounded-lg border-2 border-ink bg-red-100 p-4">
                  <p className="flex items-center gap-2 font-black text-red-950">
                    <AlertTriangle size={20} />
                    This will permanently delete all documents and data.
                  </p>
                  <p className="mt-2 text-sm font-semibold text-red-800">This action cannot be undone.</p>
                  <div className="mt-4 flex flex-col gap-3 sm:flex-row">
                    <button
                      onClick={handleClearData}
                      disabled={clearing}
                      className="inline-flex min-h-[2.75rem] flex-1 items-center justify-center gap-2 rounded-md border-2 border-ink bg-red-600 px-4 py-2 font-black text-white disabled:opacity-50"
                    >
                      {clearing ? 'Clearing' : 'Confirm delete'}
                    </button>
                    <button onClick={() => setConfirmClear(false)} className="btn-secondary flex-1">
                      Cancel
                    </button>
                  </div>
                </div>
              )}
            </div>
          </section>
        </>
      )}
    </div>
  )
}

export default Statistics
