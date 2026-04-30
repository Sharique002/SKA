import { useEffect, useMemo, useState } from 'react'
import { listDocuments, deleteDocument } from '../services/api'
import { FileText, Filter, RefreshCw, Search, Trash2 } from 'lucide-react'

function Documents() {
  const [documents, setDocuments] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('All')
  const [deleting, setDeleting] = useState(null)

  useEffect(() => {
    fetchDocuments()
  }, [])

  const filteredDocs = useMemo(() => {
    return documents.filter((doc) => {
      const matchesName = searchTerm
        ? doc.filename.toLowerCase().includes(searchTerm.toLowerCase())
        : true
      const matchesStatus = statusFilter === 'All' ? true : doc.status === statusFilter
      return matchesName && matchesStatus
    })
  }, [documents, searchTerm, statusFilter])

  const fetchDocuments = async () => {
    try {
      setLoading(true)
      const response = await listDocuments()
      setDocuments(response.data.documents || [])
    } catch (error) {
      console.error('Error fetching documents:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (docId, filename) => {
    if (!window.confirm(`Are you sure you want to delete "${filename}"?`)) return

    setDeleting(docId)
    try {
      await deleteDocument(docId)
      setDocuments(documents.filter((d) => d.id !== docId))
    } catch (error) {
      console.error('Error deleting document:', error)
      alert('Failed to delete document')
    } finally {
      setDeleting(null)
    }
  }

  const getStatusBadge = (status) => {
    switch (status) {
      case 'processed':
        return <span className="badge-success">Processed</span>
      case 'processing':
        return <span className="badge-warning">Processing</span>
      case 'failed':
        return <span className="badge-danger">Failed</span>
      default:
        return <span className="badge bg-white text-gray-700">{status}</span>
    }
  }

  const formatBytes = (bytes = 0) => `${(bytes / 1024).toFixed(2)} KB`

  return (
    <div className="animate-fade-in space-y-8">
      <section className="card overflow-hidden">
        <div className="accent-strip" />
        <div className="flex flex-col gap-5 p-6 lg:flex-row lg:items-center lg:justify-between">
          <div className="flex items-center gap-4">
            <div className="flex h-14 w-14 items-center justify-center rounded-lg border-2 border-ink bg-amber">
              <FileText size={30} strokeWidth={2.5} />
            </div>
            <div>
              <h1 className="text-3xl font-black text-ink">Document Management</h1>
              <p className="font-semibold text-gray-600">
                Total documents: <span className="font-black text-ink">{documents.length}</span>
              </p>
            </div>
          </div>
          <button onClick={fetchDocuments} className="btn-secondary">
            <RefreshCw size={18} />
            Refresh
          </button>
        </div>
      </section>

      <section className="toolbar-panel p-5">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label className="mb-2 flex items-center gap-2 text-sm font-black uppercase text-gray-700">
              <Search size={17} />
              Search filename
            </label>
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search documents..."
              className="input-field"
            />
          </div>
          <div>
            <label className="mb-2 flex items-center gap-2 text-sm font-black uppercase text-gray-700">
              <Filter size={17} />
              Status
            </label>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="input-field"
            >
              <option>All</option>
              <option>processed</option>
              <option>processing</option>
              <option>failed</option>
            </select>
          </div>
        </div>
        <p className="mt-4 text-sm font-black uppercase text-gray-500">
          Showing {filteredDocs.length} of {documents.length}
        </p>
      </section>

      <section className="space-y-4">
        {loading ? (
          <div className="card p-12 text-center">
            <div className="mx-auto h-12 w-12 animate-spin rounded-full border-4 border-secondary-500 border-t-transparent" />
          </div>
        ) : filteredDocs.length > 0 ? (
          filteredDocs.map((doc) => (
            <article key={doc.id} className="card p-5">
              <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                <div className="min-w-0 flex-1">
                  <div className="mb-4 flex flex-wrap items-center gap-3">
                    <h2 className="truncate text-xl font-black text-ink">{doc.filename}</h2>
                    {getStatusBadge(doc.status)}
                  </div>

                  <div className="grid grid-cols-2 gap-3 text-sm sm:grid-cols-4">
                    <div className="rounded-md border-2 border-ink bg-white p-3">
                      <p className="font-black uppercase text-gray-500">Type</p>
                      <p className="mt-1 font-black text-ink">{doc.file_type.toUpperCase()}</p>
                    </div>
                    <div className="rounded-md border-2 border-ink bg-[#e8f0ff] p-3">
                      <p className="font-black uppercase text-gray-500">Chunks</p>
                      <p className="mt-1 font-black text-ink">{doc.num_chunks}</p>
                    </div>
                    <div className="rounded-md border-2 border-ink bg-[#fff3c9] p-3">
                      <p className="font-black uppercase text-gray-500">Size</p>
                      <p className="mt-1 font-black text-ink">{formatBytes(doc.file_size)}</p>
                    </div>
                    <div className="rounded-md border-2 border-ink bg-[#ffe1cc] p-3">
                      <p className="font-black uppercase text-gray-500">Uploaded</p>
                      <p className="mt-1 font-black text-ink">{new Date(doc.upload_date).toLocaleDateString()}</p>
                    </div>
                  </div>
                </div>

                <button
                  onClick={() => handleDelete(doc.id, doc.filename)}
                  disabled={deleting === doc.id}
                  className="btn-secondary h-11 w-11 flex-shrink-0 p-0 text-red-700 hover:bg-red-100"
                  aria-label={`Delete ${doc.filename}`}
                >
                  <Trash2 size={20} />
                </button>
              </div>
            </article>
          ))
        ) : (
          <div className="card p-12 text-center">
            <Search size={48} className="mx-auto mb-4 text-gray-400" />
            <p className="text-lg font-black text-gray-600">No documents found</p>
            <p className="mt-2 font-semibold text-gray-500">Upload documents to populate the library.</p>
          </div>
        )}
      </section>
    </div>
  )
}

export default Documents
