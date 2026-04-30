import { useState } from 'react'
import { queryKnowledge } from '../services/api'
import { AlertCircle, FileText, Loader2, Search, SlidersHorizontal, Sparkles } from 'lucide-react'

function Query() {
  const [query, setQuery] = useState('')
  const [topK, setTopK] = useState(5)
  const [searching, setSearching] = useState(false)
  const [result, setResult] = useState(null)

  const handleSearch = async () => {
    if (!query.trim()) return

    setSearching(true)
    try {
      const response = await queryKnowledge(query, topK)
      setResult(response.data)
    } catch (error) {
      setResult({
        error: error.response?.data?.error || error.message,
      })
    } finally {
      setSearching(false)
    }
  }

  const getConfidenceClass = (confidence) => {
    if (confidence >= 0.7) return 'bg-green-100 text-green-800'
    if (confidence >= 0.4) return 'bg-amber text-ink'
    return 'bg-red-100 text-red-800'
  }

  const examples = [
    'What are the main topics discussed?',
    'Summarize the key points',
    'What are the important dates mentioned?',
    'List the main conclusions',
  ]

  return (
    <div className="animate-fade-in space-y-8">
      <section className="card overflow-hidden">
        <div className="accent-strip" />
        <div className="grid gap-6 p-6 lg:grid-cols-[minmax(0,1fr)_320px] lg:p-8">
          <div>
            <div className="mb-6 flex items-center gap-4">
              <div className="flex h-14 w-14 items-center justify-center rounded-lg border-2 border-ink bg-secondary-500 text-white">
                <Search size={30} strokeWidth={2.5} />
              </div>
              <div>
                <h1 className="text-3xl font-black text-ink">Knowledge Query</h1>
                <p className="font-semibold text-gray-600">Ask against your indexed documents</p>
              </div>
            </div>

            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault()
                  handleSearch()
                }
              }}
              placeholder="Ask any question about your documents..."
              className="input-field h-32 resize-none text-lg"
            />

            <div className="mt-5 flex flex-col gap-4 sm:flex-row sm:items-end">
              <div className="flex-1 rounded-lg border-2 border-ink bg-[#e8f0ff] p-4">
                <label className="mb-3 flex items-center gap-2 text-sm font-black uppercase text-gray-700">
                  <SlidersHorizontal size={18} />
                  Sources: {topK}
                </label>
                <input
                  type="range"
                  min="1"
                  max="10"
                  value={topK}
                  onChange={(e) => setTopK(parseInt(e.target.value))}
                  className="w-full accent-orange-600"
                />
              </div>
              <button onClick={handleSearch} disabled={!query.trim() || searching} className="btn-primary px-8">
                {searching ? <Loader2 size={18} className="animate-spin" /> : <Search size={18} />}
                {searching ? 'Searching' : 'Search'}
              </button>
            </div>
          </div>

          <aside className="flat-panel bg-white p-5">
            <div className="mb-4 flex items-center gap-2 font-black text-ink">
              <Sparkles size={20} strokeWidth={2.5} />
              Example Questions
            </div>
            <div className="space-y-3">
              {examples.map((example) => (
                <button
                  key={example}
                  onClick={() => setQuery(example)}
                  className="w-full rounded-lg border-2 border-ink bg-white p-3 text-left text-sm font-bold text-gray-700 shadow-[3px_3px_0_#101010] transition-all hover:translate-x-1 hover:translate-y-1 hover:bg-amber hover:shadow-[1px_1px_0_#101010]"
                >
                  {example}
                </button>
              ))}
            </div>
          </aside>
        </div>
      </section>

      {result && (
        <section className="animate-slide-up space-y-6">
          {result.error ? (
            <div className="rounded-lg border-2 border-ink bg-red-100 p-5 shadow-[4px_4px_0_#101010]">
              <p className="flex items-center gap-2 font-black text-red-950">
                <AlertCircle size={20} /> Error: {result.error}
              </p>
            </div>
          ) : (
            <>
              <div className="card overflow-hidden">
                <div className="accent-strip" />
                <div className="p-6">
                  <div className="mb-5 flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                    <h2 className="text-2xl font-black text-ink">Answer</h2>
                    <span className={`badge ${getConfidenceClass(result.confidence)}`}>
                      {(result.confidence * 100).toFixed(0)}% confidence
                    </span>
                  </div>
                  <p className="whitespace-pre-line text-base font-semibold leading-8 text-gray-700">{result.answer}</p>
                  <p className="mt-5 text-xs font-black uppercase text-gray-500">
                    Processing time: {result.processing_time?.toFixed(2)}s
                  </p>
                </div>
              </div>

              {result.sources && result.sources.length > 0 && (
                <div>
                  <h2 className="mb-4 text-2xl font-black text-ink">Sources</h2>
                  <div className="space-y-4">
                    {result.sources.map((source, index) => (
                      <details key={`${source.filename}-${index}`} className="card p-5">
                        <summary className="cursor-pointer list-none">
                          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                            <div className="flex min-w-0 items-center gap-3">
                              <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-md border-2 border-ink bg-amber">
                                <FileText size={20} />
                              </div>
                              <span className="truncate font-black text-ink">Source {index + 1}: {source.filename}</span>
                            </div>
                            <span className="badge bg-[#e8f0ff] text-secondary-600">
                              {(source.similarity * 100).toFixed(0)}% relevant
                            </span>
                          </div>
                        </summary>
                        <div className="mt-4 rounded-lg border-2 border-dashed border-gray-500 bg-white p-4 text-sm font-semibold leading-7 text-gray-700">
                          {source.content}
                        </div>
                      </details>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
        </section>
      )}
    </div>
  )
}

export default Query
