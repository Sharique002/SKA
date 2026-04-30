import { useEffect, useRef, useState } from 'react'
import { uploadDocument, listDocuments } from '../services/api'
import { Upload as UploadIcon, CheckCircle, AlertCircle, FileText, Loader2, X } from 'lucide-react'

function Upload() {
  const [file, setFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [result, setResult] = useState(null)
  const [documents, setDocuments] = useState([])
  const [loadingDocs, setLoadingDocs] = useState(true)
  const [dragging, setDragging] = useState(false)
  const fileInput = useRef(null)

  useEffect(() => {
    fetchDocuments()
  }, [])

  const selectFile = (selected) => {
    if (selected) {
      setFile(selected)
      setResult(null)
    }
  }

  const handleFileSelect = (e) => {
    selectFile(e.target.files[0])
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setDragging(false)
    selectFile(e.dataTransfer.files[0])
  }

  const handleUpload = async () => {
    if (!file) return

    setUploading(true)
    try {
      const response = await uploadDocument(file)
      setResult({ success: true, data: response.data })
      setFile(null)
      if (fileInput.current) {
        fileInput.current.value = ''
      }
      fetchDocuments()
    } catch (error) {
      setResult({
        success: false,
        error: error.response?.data?.message || error.message,
      })
    } finally {
      setUploading(false)
    }
  }

  const fetchDocuments = async () => {
    try {
      setLoadingDocs(true)
      const response = await listDocuments()
      setDocuments(response.data.documents || [])
    } catch (error) {
      console.error('Error fetching documents:', error)
    } finally {
      setLoadingDocs(false)
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
      <section className="grid gap-6 lg:grid-cols-[minmax(0,1.1fr)_minmax(320px,0.9fr)]">
        <div className="card overflow-hidden">
          <div className="accent-strip" />
          <div className="p-6 lg:p-8">
            <div className="mb-6 flex items-center gap-4">
              <div className="flex h-14 w-14 items-center justify-center rounded-lg border-2 border-ink bg-primary-500">
                <UploadIcon size={30} strokeWidth={2.5} />
              </div>
              <div>
                <h1 className="text-3xl font-black text-ink">Upload Documents</h1>
                <p className="font-semibold text-gray-600">PDF, DOCX, DOC, TXT, and MD files</p>
              </div>
            </div>

            <div
              className={`cursor-pointer rounded-lg border-2 border-dashed p-8 text-center transition-all lg:p-12 ${
                dragging ? 'border-ink bg-amber shadow-[4px_4px_0_#101010]' : 'border-gray-500 bg-white hover:border-ink hover:bg-[#fff3c9]'
              }`}
              onClick={() => fileInput.current?.click()}
              onDragOver={(e) => {
                e.preventDefault()
                setDragging(true)
              }}
              onDragLeave={() => setDragging(false)}
              onDrop={handleDrop}
            >
              <UploadIcon size={54} className="mx-auto mb-5 text-secondary-500" strokeWidth={2.2} />
              <p className="mb-2 text-xl font-black text-ink">{file ? file.name : 'Drop a file here'}</p>
              <p className="text-sm font-semibold uppercase text-gray-500">or browse from your computer</p>
              <input
                ref={fileInput}
                type="file"
                onChange={handleFileSelect}
                accept=".pdf,.docx,.doc,.txt,.md"
                className="hidden"
              />
            </div>

            {file && (
              <div className="mt-6 rounded-lg border-2 border-ink bg-[#e8f0ff] p-4">
                <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                  <div className="flex min-w-0 items-center gap-3">
                    <div className="flex h-11 w-11 flex-shrink-0 items-center justify-center rounded-md border-2 border-ink bg-white">
                      <FileText size={22} />
                    </div>
                    <div className="min-w-0">
                      <p className="truncate font-black text-ink">{file.name}</p>
                      <p className="text-sm font-semibold text-gray-600">{formatBytes(file.size)}</p>
                    </div>
                  </div>
                  <div className="flex gap-3">
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        setFile(null)
                        if (fileInput.current) {
                          fileInput.current.value = ''
                        }
                      }}
                      className="btn-secondary h-11 w-11 p-0"
                      aria-label="Remove selected file"
                    >
                      <X size={18} />
                    </button>
                    <button onClick={handleUpload} disabled={uploading} className="btn-primary">
                      {uploading ? <Loader2 size={18} className="animate-spin" /> : <UploadIcon size={18} />}
                      {uploading ? 'Uploading' : 'Upload and process'}
                    </button>
                  </div>
                </div>
              </div>
            )}

            {result && (
              <div className={`mt-6 rounded-lg border-2 border-ink p-4 ${
                result.success ? 'bg-green-100' : 'bg-red-100'
              }`}>
                {result.success ? (
                  <div>
                    <p className="mb-3 flex items-center gap-2 font-black text-green-950">
                      <CheckCircle size={20} /> Upload successful
                    </p>
                    <div className="grid gap-2 text-sm font-semibold text-green-900 sm:grid-cols-3">
                      <p><strong>ID:</strong> {result.data.document_id}</p>
                      <p><strong>File:</strong> {result.data.filename}</p>
                      <p><strong>Chunks:</strong> {result.data.num_chunks}</p>
                    </div>
                  </div>
                ) : (
                  <p className="flex items-center gap-2 font-black text-red-950">
                    <AlertCircle size={20} /> {result.error}
                  </p>
                )}
              </div>
            )}
          </div>
        </div>

        <aside className="flat-panel bg-white p-6">
          <h2 className="text-xl font-black text-ink">Processing Stack</h2>
          <div className="mt-5 space-y-4">
            {['Extract text', 'Create chunks', 'Generate embeddings', 'Store vectors'].map((item, index) => (
              <div key={item} className="flex items-center gap-3">
                <span className={`flex h-9 w-9 items-center justify-center rounded-md border-2 border-ink font-black ${
                  index % 2 === 0 ? 'bg-primary-500' : 'bg-amber'
                }`}>
                  {index + 1}
                </span>
                <span className="font-black text-gray-800">{item}</span>
              </div>
            ))}
          </div>
        </aside>
      </section>

      <section className="card overflow-hidden">
        <div className="accent-strip" />
        <div className="p-6 lg:p-8">
          <div className="mb-6 flex items-center justify-between gap-4">
            <h2 className="text-2xl font-black text-ink">Recent Uploads</h2>
            <button onClick={fetchDocuments} className="btn-secondary">
              Refresh
            </button>
          </div>

          {loadingDocs ? (
            <div className="py-8 text-center">
              <div className="mx-auto h-9 w-9 animate-spin rounded-full border-4 border-secondary-500 border-t-transparent" />
            </div>
          ) : documents.length > 0 ? (
            <div className="space-y-4">
              {documents.slice(0, 5).map((doc) => (
                <div key={doc.id} className="rounded-lg border-2 border-ink bg-white p-4">
                  <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                    <div className="min-w-0 flex-1">
                      <div className="mb-3 flex flex-wrap items-center gap-3">
                        <p className="truncate text-lg font-black text-ink">{doc.filename}</p>
                        {getStatusBadge(doc.status)}
                      </div>
                      <div className="grid gap-3 text-sm sm:grid-cols-4">
                        <p><span className="font-black text-gray-500">Type</span><br />{doc.file_type.toUpperCase()}</p>
                        <p><span className="font-black text-gray-500">Chunks</span><br />{doc.num_chunks}</p>
                        <p><span className="font-black text-gray-500">Size</span><br />{formatBytes(doc.file_size)}</p>
                        <p><span className="font-black text-gray-500">Uploaded</span><br />{new Date(doc.upload_date).toLocaleDateString()}</p>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="rounded-lg border-2 border-dashed border-gray-500 p-10 text-center">
              <FileText size={46} className="mx-auto mb-4 text-gray-400" />
              <p className="text-lg font-black text-gray-600">No documents uploaded yet</p>
            </div>
          )}
        </div>
      </section>
    </div>
  )
}

export default Upload
