import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getStatistics } from '../services/api'
import {
  ArrowRight,
  BarChart3,
  BrainCircuit,
  Database,
  FileText,
  Layers,
  Search,
  Upload,
} from 'lucide-react'

function InterfaceIllustration() {
  return (
    <div className="relative min-h-[350px] overflow-hidden rounded-lg border-2 border-ink bg-white p-5 shadow-[6px_6px_0_#101010]">
      <div className="absolute -right-9 bottom-0 h-36 w-24 rotate-12 rounded-t-full border-2 border-ink bg-[#6b7d00]" />
      <div className="absolute -left-8 top-8 h-28 w-28 rotate-12 rounded-lg border-2 border-ink bg-primary-500" />
      <div className="absolute left-5 top-16 z-10 flex h-20 w-24 -rotate-3 items-center justify-center border-2 border-ink bg-secondary-500 text-4xl font-black text-white shadow-[4px_4px_0_#101010]">
        Text
      </div>
      <div className="absolute left-1 top-32 z-20 flex h-20 w-32 -rotate-2 items-center justify-center border-2 border-ink bg-primary-500 text-4xl font-black">
        &lt;/&gt;
      </div>

      <div className="ml-auto w-full max-w-[360px] rounded-2xl border-[10px] border-ink bg-white p-5">
        <div className="mb-5 flex items-center justify-center gap-3">
          <span className="h-3 w-3 rounded-full bg-ink" />
          <span className="h-3 w-28 bg-ink" />
        </div>
        <div className="grid grid-cols-3 gap-4">
          <div className="aspect-square border-2 border-ink bg-[#7aa2e8]">
            <div className="h-full w-full bg-[linear-gradient(135deg,transparent_49%,#101010_50%,transparent_51%),linear-gradient(45deg,transparent_49%,#101010_50%,transparent_51%)]" />
          </div>
          <div className="aspect-square border-2 border-gray-500 bg-white">
            <div className="h-full w-full bg-[linear-gradient(135deg,transparent_49%,#101010_50%,transparent_51%),linear-gradient(45deg,transparent_49%,#101010_50%,transparent_51%)]" />
          </div>
          <div className="relative aspect-square border-2 border-ink bg-amber">
            <span className="absolute left-2 top-2 h-2 w-2 bg-ink" />
            <span className="absolute right-2 top-2 h-2 w-2 bg-ink" />
            <span className="absolute bottom-2 left-2 h-2 w-2 bg-ink" />
            <span className="absolute bottom-2 right-2 h-2 w-2 bg-ink" />
          </div>
        </div>

        <div className="relative mt-5 h-16 bg-secondary-500">
          <span className="absolute left-12 top-8 h-[2px] w-44 -rotate-[35deg] bg-yellow-300" />
          <span className="absolute left-24 top-10 h-[2px] w-36 -rotate-[35deg] bg-yellow-300" />
          <span className="absolute right-5 top-8 h-14 w-14 rounded-full border-[6px] border-ink bg-white" />
          <span className="absolute right-1 top-20 h-11 w-[7px] -rotate-45 bg-ink" />
        </div>

        <div className="mt-7 space-y-6">
          <div className="relative h-5 bg-amber">
            <span className="absolute left-28 -top-3 h-11 w-4 bg-ink" />
          </div>
          <div className="relative h-5 bg-secondary-500">
            <span className="absolute left-44 -top-3 h-11 w-4 bg-ink" />
          </div>
          <div className="relative h-5 border-2 border-gray-500 bg-amber">
            <span className="absolute right-24 -top-4 h-12 w-4 bg-ink" />
          </div>
        </div>

        <div className="mt-7 grid grid-cols-2 gap-5">
          <div className="relative flex min-h-[94px] items-center justify-center border-2 border-dashed border-gray-600">
            <span className="absolute -left-2 -top-2 h-4 w-4 bg-secondary-500" />
            <span className="absolute -right-2 -top-2 h-4 w-4 bg-secondary-500" />
            <span className="absolute -bottom-2 -left-2 h-4 w-4 bg-secondary-500" />
            <span className="absolute -bottom-2 -right-2 h-4 w-4 bg-secondary-500" />
            <div className="h-16 w-12 rounded-full border-2 border-ink bg-amber" />
          </div>
          <div className="relative flex min-h-[94px] items-center justify-center border-2 border-ink bg-primary-500">
            <div className="h-0 w-0 border-y-[27px] border-l-[42px] border-y-transparent border-l-white" />
            <span className="absolute bottom-3 right-3 h-10 w-10 border-l-2 border-t-2 border-dotted border-ink" />
          </div>
        </div>
      </div>
    </div>
  )
}

function MetricCard({ icon: Icon, label, value, tone }) {
  return (
    <div className={`card p-5 ${tone}`}>
      <div className="mb-4 flex h-11 w-11 items-center justify-center rounded-md border-2 border-ink bg-white">
        <Icon size={23} strokeWidth={2.4} />
      </div>
      <div className="text-3xl font-black text-ink">{value ?? 0}</div>
      <div className="mt-1 text-sm font-black uppercase text-gray-700">{label}</div>
    </div>
  )
}

function Home() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      const response = await getStatistics()
      setStats(response.data)
    } catch (error) {
      console.error('Error fetching stats:', error)
    } finally {
      setLoading(false)
    }
  }

  const metrics = [
    { icon: FileText, label: 'Documents', value: stats?.total_documents || 0, tone: 'bg-white' },
    { icon: Layers, label: 'Text chunks', value: stats?.total_chunks || 0, tone: 'bg-[#e8f0ff]' },
    { icon: Database, label: 'Storage MB', value: stats?.total_storage_mb || 0, tone: 'bg-[#fff3c9]' },
    { icon: BarChart3, label: 'Vectors', value: stats?.vector_db?.total_vectors || 0, tone: 'bg-[#ffe1cc]' },
  ]

  const actions = [
    { to: '/upload', icon: Upload, title: 'Upload', detail: 'Add source files' },
    { to: '/query', icon: Search, title: 'Query', detail: 'Ask the indexed set' },
    { to: '/documents', icon: FileText, title: 'Documents', detail: 'Review the library' },
  ]

  return (
    <div className="animate-fade-in space-y-8">
      <section className="grid items-center gap-8 lg:grid-cols-[minmax(0,0.9fr)_minmax(420px,1.1fr)]">
        <div className="space-y-6">
          <div className="inline-flex items-center gap-2 rounded-md border-2 border-ink bg-amber px-3 py-2 text-xs font-black uppercase shadow-[3px_3px_0_#101010]">
            <BrainCircuit size={16} strokeWidth={2.5} />
            Smart Knowledge Assistant
          </div>
          <div>
            <h1 className="max-w-3xl text-4xl font-black leading-[1.02] text-ink sm:text-5xl lg:text-6xl">
              SKA Control Desk
            </h1>
            <p className="mt-4 max-w-2xl text-lg font-semibold leading-8 text-gray-700">
              Upload documents, turn them into searchable chunks, and query the knowledge base from one crisp workspace.
            </p>
          </div>
          <div className="flex flex-col gap-3 sm:flex-row">
            <Link to="/upload" className="btn-primary">
              <Upload size={18} strokeWidth={2.5} />
              Upload documents
            </Link>
            <Link to="/query" className="btn-secondary">
              <Search size={18} strokeWidth={2.5} />
              Ask a question
              <ArrowRight size={18} strokeWidth={2.5} />
            </Link>
          </div>
        </div>
        <InterfaceIllustration />
      </section>

      <section>
        {loading ? (
          <div className="toolbar-panel p-8 text-center">
            <div className="mx-auto h-12 w-12 animate-spin rounded-full border-4 border-primary-500 border-t-transparent" />
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 xl:grid-cols-4">
            {metrics.map((metric) => (
              <MetricCard key={metric.label} {...metric} />
            ))}
          </div>
        )}
      </section>

      <section className="grid gap-5 md:grid-cols-3">
        {actions.map((action) => (
          <Link key={action.to} to={action.to} className="card group block p-6">
            <div className="mb-6 flex h-14 w-14 items-center justify-center rounded-lg border-2 border-ink bg-secondary-500 text-white group-hover:bg-primary-500 group-hover:text-ink">
              <action.icon size={28} strokeWidth={2.4} />
            </div>
            <h2 className="text-2xl font-black text-ink">{action.title}</h2>
            <p className="mt-2 font-semibold text-gray-600">{action.detail}</p>
          </Link>
        ))}
      </section>

      <section className="flat-panel overflow-hidden bg-white">
        <div className="accent-strip" />
        <div className="grid gap-6 p-6 lg:grid-cols-4">
          {[
            { step: '01', title: 'Extract', text: 'Text is pulled from PDF, Word, text, and Markdown files.' },
            { step: '02', title: 'Chunk', text: 'Content is split into focused overlapping passages.' },
            { step: '03', title: 'Embed', text: 'Vectors are stored for semantic search.' },
            { step: '04', title: 'Answer', text: 'Responses cite the most relevant source chunks.' },
          ].map((item) => (
            <div key={item.step} className="border-l-4 border-ink pl-4">
              <div className="text-sm font-black text-primary-600">{item.step}</div>
              <div className="mt-1 text-xl font-black text-ink">{item.title}</div>
              <p className="mt-2 text-sm font-semibold leading-6 text-gray-600">{item.text}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}

export default Home
