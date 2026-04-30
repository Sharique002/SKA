import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Menu, X, Home, Upload, Search, FileText, BarChart3, AlertCircle, CheckCircle, BrainCircuit } from 'lucide-react'

function Layout({ children, backendOnline }) {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const location = useLocation()

  const navItems = [
    { path: '/', icon: Home, label: 'Home' },
    { path: '/upload', icon: Upload, label: 'Upload' },
    { path: '/query', icon: Search, label: 'Query' },
    { path: '/documents', icon: FileText, label: 'Documents' },
    { path: '/statistics', icon: BarChart3, label: 'Statistics' },
  ]

  const isActive = (path) => location.pathname === path

  return (
    <div className="flex min-h-screen">
      {/* Sidebar */}
      <div className={`fixed inset-y-0 left-0 z-50 w-72 border-r-2 border-ink bg-paper transform transition-transform duration-300 lg:transform-none lg:translate-x-0 ${
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      }`}>
        {/* Header */}
        <div className="h-24 flex items-center justify-between px-5 border-b-2 border-ink">
          <div className="flex items-center gap-3">
            <div className="relative flex h-14 w-14 items-center justify-center rounded-lg border-2 border-ink bg-secondary-500 text-white shadow-[4px_4px_0_#101010]">
              <BrainCircuit size={28} strokeWidth={2.4} />
              <span className="absolute -bottom-2 -right-2 h-5 w-5 rounded-sm border-2 border-ink bg-primary-500" />
            </div>
            <div>
              <h1 className="text-2xl font-black leading-none text-ink">SKA</h1>
              <p className="text-xs font-black uppercase text-gray-600">Knowledge OS</p>
            </div>
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            className="btn-secondary h-10 w-10 p-0 lg:hidden"
            aria-label="Close navigation"
          >
            <X size={20} />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-4 py-6 space-y-3">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              onClick={() => setSidebarOpen(false)}
              className={`flex items-center gap-3 rounded-lg border-2 border-ink px-4 py-3 font-black transition-all ${
                isActive(item.path)
                  ? 'translate-x-1 translate-y-1 bg-primary-500 text-ink shadow-[2px_2px_0_#101010]'
                  : 'bg-white text-gray-800 shadow-[4px_4px_0_#101010] hover:translate-x-1 hover:translate-y-1 hover:bg-amber hover:shadow-[2px_2px_0_#101010]'
              }`}
            >
              <item.icon size={20} strokeWidth={2.5} />
              <span>{item.label}</span>
            </Link>
          ))}
        </nav>

        {/* Status Footer */}
        <div className="p-4 border-t-2 border-ink">
          <div className={`flex items-center gap-3 rounded-lg border-2 border-ink px-4 py-3 font-black ${
            backendOnline ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
          }`}>
            {backendOnline ? (
              <>
                <CheckCircle size={18} />
                <span className="text-sm">Backend online</span>
              </>
            ) : (
              <>
                <AlertCircle size={18} />
                <span className="text-sm">Backend offline</span>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 lg:ml-72">
        {/* Top Bar */}
        <div className="sticky top-0 z-40 border-b-2 border-ink bg-white">
          <div className="flex h-16 items-center justify-between px-4 lg:px-8">
            <button
              onClick={() => setSidebarOpen(true)}
              className="btn-secondary h-10 w-10 p-0 lg:hidden"
              aria-label="Open navigation"
            >
              <Menu size={24} />
            </button>
            <div className="hidden items-center gap-3 sm:flex">
              <span className="h-3 w-3 rounded-full border-2 border-ink bg-primary-500" />
              <span className="h-3 w-3 rounded-full border-2 border-ink bg-amber" />
              <span className="h-3 w-3 rounded-full border-2 border-ink bg-secondary-500" />
              <span className="ml-2 text-sm font-black uppercase text-gray-700">Smart Knowledge Assistant</span>
            </div>
            <div className="text-right">
              <p className="text-xs font-black uppercase text-gray-500">v1.0.0</p>
            </div>
          </div>
        </div>

        {/* Page Content */}
        <main className="p-4 lg:p-8">
          {!backendOnline && (
            <div className="mb-6 flex items-start gap-3 rounded-lg border-2 border-ink bg-red-100 p-4 shadow-[4px_4px_0_#101010]">
              <AlertCircle className="mt-0.5 flex-shrink-0 text-red-700" />
              <div>
                <h3 className="font-black text-red-950">Backend offline</h3>
                <p className="text-sm font-medium text-red-800">Make sure Flask backend is running on port 5000.</p>
              </div>
            </div>
          )}
          {children}
        </main>
      </div>
    </div>
  )
}

export default Layout
