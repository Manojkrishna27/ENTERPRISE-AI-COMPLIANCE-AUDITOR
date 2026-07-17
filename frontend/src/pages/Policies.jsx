import React, { useState, useEffect } from 'react'
import { 
  ShieldCheck, 
  Upload, 
  Trash2, 
  Search,
  Plus
} from 'lucide-react'
import api from '../services/api'
import Sidebar from '../components/Sidebar'
import Navbar from '../components/Navbar'

const Policies = () => {
  const [policies, setPolicies] = useState([])
  const [loading, setLoading] = useState(true)
  const user = JSON.parse(localStorage.getItem('user') || '{}')
  const canModify = user.role === 'Admin' || user.role === 'Compliance Officer'
  
  // Search & Filter State
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('')
  
  // Upload State
  const [showUploadModal, setShowUploadModal] = useState(false)
  const [uploadName, setUploadName] = useState('')
  const [uploadDesc, setUploadDesc] = useState('')
  const [uploadCategory, setUploadCategory] = useState('GDPR')
  const [uploadFile, setUploadFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const fetchPolicies = async () => {
    try {
      const res = await api.get('/policies')
      setPolicies(res.data)
    } catch (err) {
      console.error('Error fetching policies:', err)
    }
  }

  useEffect(() => {
    const init = async () => {
      setLoading(true)
      await fetchPolicies()
      setLoading(false)
    }
    init()
  }, [])

  const handleUploadSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess('')
    if (!uploadFile) {
      setError('Please select a file to upload')
      return
    }

    const formData = new FormData()
    formData.append('file', uploadFile)
    formData.append('name', uploadName)
    formData.append('description', uploadDesc)
    formData.append('category', uploadCategory)

    setUploading(true)
    try {
      await api.post('/policies', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      setSuccess('Policy standard uploaded and vector-indexed successfully!')
      setUploadName('')
      setUploadDesc('')
      setUploadFile(null)
      await fetchPolicies()
      setTimeout(() => {
        setShowUploadModal(false)
        setSuccess('')
      }, 1500)
    } catch (err) {
      setError(err.response?.data?.msg || 'Failed to upload policy standard')
    } finally {
      setUploading(false)
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to permanently delete this policy and remove all indexed vector chunks from Qdrant?")) return
    try {
      await api.delete(`/policies/${id}`)
      await fetchPolicies()
    } catch (err) {
      console.error('Error deleting policy:', err)
    }
  }

  // Filter logic
  const filteredPolicies = policies.filter((p) => {
    const matchesSearch = p.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
                          (p.description && p.description.toLowerCase().includes(searchQuery.toLowerCase()))
    const matchesCategory = selectedCategory === '' || p.category === selectedCategory
    
    return matchesSearch && matchesCategory
  })

  return (
    <div className="flex bg-background min-h-screen text-text-primary">
      <Sidebar />
      
      <div className="flex-1 flex flex-col min-w-0">
        <Navbar />
        
        <main className="flex-1 overflow-y-auto p-8 space-y-6">
          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h1 className="text-2xl font-bold tracking-tight">Policy Standards Library</h1>
              <p className="text-sm text-text-secondary">Manage regulations and company frameworks parsed for RAG compliance auditing</p>
            </div>
            {canModify && (
              <button
                onClick={() => setShowUploadModal(true)}
                className="bg-brand hover:bg-brand-dark px-4 py-2.5 rounded-xl font-semibold text-sm flex items-center justify-center gap-2 shadow-lg shadow-brand/20 transition-all duration-200"
              >
                <Plus className="w-5 h-5" />
                <span>Upload Policy</span>
              </button>
            )}
          </div>

          {/* Filters Bar */}
          <div className="bg-card border border-border p-4 rounded-2xl flex flex-wrap items-center gap-4">
            <div className="flex-1 min-w-[200px] relative">
              <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center text-text-muted">
                <Search className="w-4 h-4" />
              </span>
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-background border border-border focus:border-brand rounded-xl pl-10 pr-4 py-2 text-sm text-text-primary outline-none transition-colors duration-200"
                placeholder="Search policies by name..."
              />
            </div>
            
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="bg-background border border-border rounded-xl px-4 py-2 text-sm outline-none cursor-pointer"
            >
              <option value="">All Categories</option>
              <option value="GDPR">GDPR</option>
              <option value="ISO27001">ISO 27001</option>
              <option value="SOC2">SOC 2</option>
              <option value="Internal">Internal Guidelines</option>
              <option value="Vendor">Vendor Standards</option>
              <option value="Custom">Custom Regulations</option>
            </select>
          </div>

          {/* Table */}
          {loading ? (
            <div className="flex items-center justify-center py-20">
              <div className="w-10 h-10 border-4 border-brand/30 border-t-brand rounded-full animate-spin"></div>
            </div>
          ) : filteredPolicies.length === 0 ? (
            <div className="bg-card border border-border rounded-2xl p-16 text-center">
              <div className="w-16 h-16 bg-slate-700/35 text-text-secondary rounded-2xl flex items-center justify-center mx-auto mb-4">
                <ShieldCheck className="w-8 h-8" />
              </div>
              <h3 className="text-lg font-bold">No policies found</h3>
              <p className="text-sm text-text-muted mt-1">Get started by uploading compliance frameworks to activate semantic RAG checking.</p>
            </div>
          ) : (
            <div className="bg-card border border-border rounded-2xl overflow-hidden shadow-xl">
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="bg-slate-700/25 border-b border-border text-xs font-bold uppercase tracking-wider text-text-secondary">
                      <th className="py-4 px-6">Policy Name</th>
                      <th className="py-4 px-6">Category</th>
                      <th className="py-4 px-6">Status</th>
                      <th className="py-4 px-6">Upload Date</th>
                      {canModify && <th className="py-4 px-6 text-right">Actions</th>}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border/60 text-sm font-medium">
                    {filteredPolicies.map((p) => (
                      <tr key={p.id} className="hover:bg-slate-700/10 transition-colors duration-150">
                        <td className="py-4 px-6">
                          <div className="flex items-center gap-3">
                            <div className="w-9 h-9 bg-brand/10 text-brand rounded-lg flex items-center justify-center">
                              <ShieldCheck className="w-5 h-5" />
                            </div>
                            <div>
                              <span className="text-text-primary transition-colors duration-150 block">{p.name}</span>
                              <span className="text-xs text-text-muted font-normal block max-w-xs truncate">{p.description || 'No description'}</span>
                            </div>
                          </div>
                        </td>
                        <td className="py-4 px-6">
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-brand/10 text-brand-light border border-brand/20">
                            {p.category}
                          </span>
                        </td>
                        <td className="py-4 px-6">
                          <span className="inline-flex items-center gap-1.5 text-xs text-emerald-400 font-semibold">
                            <span className="w-2 h-2 bg-emerald-400 rounded-full"></span>
                            Active & Indexed
                          </span>
                        </td>
                        <td className="py-4 px-6 text-text-muted text-xs">{new Date(p.created_at).toLocaleDateString()}</td>
                        {canModify && (
                          <td className="py-4 px-6 text-right">
                            <button
                              onClick={() => handleDelete(p.id)}
                              className="p-2 bg-risk-high/10 text-risk-high hover:bg-risk-high hover:text-text-primary rounded-lg transition-colors duration-150"
                              title="Delete"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </td>
                        )}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Upload Modal */}
          {showUploadModal && (
            <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 animate-in fade-in duration-200">
              <div className="bg-card border border-border w-full max-w-lg rounded-3xl shadow-2xl overflow-hidden p-6 animate-in zoom-in-95 duration-250">
                <div className="flex justify-between items-center mb-6">
                  <h3 className="text-lg font-bold text-text-primary">Upload Compliance Standard</h3>
                  <button 
                    onClick={() => setShowUploadModal(false)}
                    className="text-text-muted hover:text-text-primary text-sm font-semibold"
                  >
                    Cancel
                  </button>
                </div>

                {error && (
                  <div className="bg-risk-high/15 border border-risk-high/30 text-risk-high text-xs px-4 py-3 rounded-2xl mb-4">
                    {error}
                  </div>
                )}
                {success && (
                  <div className="bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 text-xs px-4 py-3 rounded-2xl mb-4">
                    {success}
                  </div>
                )}

                <form onSubmit={handleUploadSubmit} className="space-y-4">
                  <div>
                    <label className="text-xs font-bold uppercase tracking-wider text-text-muted mb-2 block">Standard Name</label>
                    <input
                      type="text"
                      required
                      value={uploadName}
                      onChange={(e) => setUploadName(e.target.value)}
                      className="w-full bg-background border border-border focus:border-brand rounded-xl px-4 py-2.5 text-sm outline-none"
                      placeholder="e.g. SOC2 Trust Security Principles"
                    />
                  </div>

                  <div>
                    <label className="text-xs font-bold uppercase tracking-wider text-text-muted mb-2 block">Description</label>
                    <textarea
                      value={uploadDesc}
                      onChange={(e) => setUploadDesc(e.target.value)}
                      className="w-full bg-background border border-border focus:border-brand rounded-xl px-4 py-2.5 text-sm outline-none"
                      placeholder="Details about the policy content..."
                      rows="3"
                    />
                  </div>

                  <div>
                    <label className="text-xs font-bold uppercase tracking-wider text-text-muted mb-2 block">Policy Category</label>
                    <select
                      value={uploadCategory}
                      onChange={(e) => setUploadCategory(e.target.value)}
                      className="w-full bg-background border border-border rounded-xl px-4 py-2.5 text-sm outline-none"
                    >
                      <option value="GDPR">GDPR</option>
                      <option value="ISO27001">ISO 27001</option>
                      <option value="SOC2">SOC 2</option>
                      <option value="Internal">Internal Guidelines</option>
                      <option value="Vendor">Vendor Standards</option>
                      <option value="Custom">Custom Regulations</option>
                    </select>
                  </div>

                  <div>
                    <label className="text-xs font-bold uppercase tracking-wider text-text-muted mb-2 block">Upload Reference Document (PDF / DOCX)</label>
                    <div className="border-2 border-dashed border-border/80 hover:border-brand/50 rounded-2xl p-6 text-center cursor-pointer relative bg-background/50 group transition-all duration-200">
                      <input
                        type="file"
                        required
                        accept=".pdf,.docx"
                        onChange={(e) => setUploadFile(e.target.files[0])}
                        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                      />
                      <Upload className="w-8 h-8 text-text-muted group-hover:text-brand mx-auto mb-2 transition-colors duration-200" />
                      <span className="text-sm font-semibold text-text-secondary block">
                        {uploadFile ? uploadFile.name : "Click or drag file here"}
                      </span>
                      <span className="text-xs text-text-muted block mt-1">Files are parsed and vector-indexed instantly</span>
                    </div>
                  </div>

                  <button
                    type="submit"
                    disabled={uploading}
                    className="w-full bg-brand hover:bg-brand-dark disabled:opacity-50 text-text-primary font-bold py-3 rounded-xl flex items-center justify-center gap-2 mt-4"
                  >
                    {uploading ? (
                      <span className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                    ) : (
                      "Index Framework"
                    )}
                  </button>
                </form>
              </div>
            </div>
          )}

        </main>
      </div>
    </div>
  )
}

export default Policies
