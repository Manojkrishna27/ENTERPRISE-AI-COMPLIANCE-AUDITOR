import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { 
  FileText, 
  Upload, 
  Trash2, 
  Archive, 
  RotateCcw,
  Search,
  Plus
} from 'lucide-react'
import api from '../services/api'
import Sidebar from '../components/Sidebar'
import Navbar from '../components/Navbar'

const Contracts = () => {
  const [contracts, setContracts] = useState([])
  const [departments, setDepartments] = useState([])
  const [loading, setLoading] = useState(true)
  
  // Search & Filter State
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedDept, setSelectedDept] = useState('')
  const [selectedStatus, setSelectedStatus] = useState('')
  
  // Upload Modal State
  const [showUploadModal, setShowUploadModal] = useState(false)
  const [uploadName, setUploadName] = useState('')
  const [uploadDesc, setUploadDesc] = useState('')
  const [uploadDept, setUploadDept] = useState('')
  const [uploadFile, setUploadFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const fetchContracts = async () => {
    try {
      const res = await api.get('/contracts')
      setContracts(res.data)
    } catch (err) {
      console.error('Error fetching contracts:', err)
    }
  }

  const fetchDependencies = async () => {
    try {
      const res = await api.get('/admin/departments')
      setDepartments(res.data)
      if (res.data.length > 0) {
        setUploadDept(res.data[0].id)
      }
    } catch (err) {
      console.error('Error fetching departments:', err)
    }
  }

  useEffect(() => {
    const init = async () => {
      setLoading(true)
      await Promise.all([fetchContracts(), fetchDependencies()])
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
    formData.append('department_id', uploadDept)

    setUploading(true)
    try {
      await api.post('/contracts', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      setSuccess('Contract uploaded successfully!')
      setUploadName('')
      setUploadDesc('')
      setUploadFile(null)
      await fetchContracts()
      setTimeout(() => {
        setShowUploadModal(false)
        setSuccess('')
      }, 1500)
    } catch (err) {
      setError(err.response?.data?.msg || 'Failed to upload contract')
    } finally {
      setUploading(false)
    }
  }

  const handleArchive = async (id) => {
    try {
      await api.post(`/contracts/${id}/archive`)
      await fetchContracts()
    } catch (err) {
      console.error('Error archiving contract:', err)
    }
  }

  const handleRestore = async (id) => {
    try {
      await api.post(`/contracts/${id}/restore`)
      await fetchContracts()
    } catch (err) {
      console.error('Error restoring contract:', err)
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to permanently delete this contract and all its version history?")) return
    try {
      await api.delete(`/contracts/${id}`)
      await fetchContracts()
    } catch (err) {
      console.error('Error deleting contract:', err)
    }
  }

  // Filter logic
  const filteredContracts = contracts.filter((c) => {
    const matchesSearch = c.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
                          (c.description && c.description.toLowerCase().includes(searchQuery.toLowerCase()))
    const matchesDept = selectedDept === '' || c.department_id === selectedDept
    const matchesStatus = selectedStatus === '' || c.status === selectedStatus
    
    return matchesSearch && matchesDept && matchesStatus
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
              <h1 className="text-2xl font-bold tracking-tight">Contract Documents</h1>
              <p className="text-sm text-text-secondary">Upload, audit, and manage standard business agreements</p>
            </div>
            <button
              onClick={() => setShowUploadModal(true)}
              className="bg-brand hover:bg-brand-dark px-4 py-2.5 rounded-xl font-semibold text-sm flex items-center justify-center gap-2 shadow-lg shadow-brand/20 transition-all duration-200"
            >
              <Plus className="w-5 h-5" />
              <span>Upload Contract</span>
            </button>
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
                placeholder="Search contracts by name..."
              />
            </div>
            
            <select
              value={selectedDept}
              onChange={(e) => setSelectedDept(e.target.value)}
              className="bg-background border border-border rounded-xl px-4 py-2 text-sm outline-none cursor-pointer"
            >
              <option value="">All Departments</option>
              {departments.map((dept) => (
                <option key={dept.id} value={dept.id}>{dept.name}</option>
              ))}
            </select>

            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="bg-background border border-border rounded-xl px-4 py-2 text-sm outline-none cursor-pointer"
            >
              <option value="">All Statuses</option>
              <option value="Draft">Draft</option>
              <option value="Pending Review">Pending Review</option>
              <option value="Approved">Approved</option>
              <option value="Archived">Archived</option>
            </select>
          </div>

          {/* Contracts Table */}
          {loading ? (
            <div className="flex items-center justify-center py-20">
              <div className="w-10 h-10 border-4 border-brand/30 border-t-brand rounded-full animate-spin"></div>
            </div>
          ) : filteredContracts.length === 0 ? (
            <div className="bg-card border border-border rounded-2xl p-16 text-center">
              <div className="w-16 h-16 bg-slate-700/35 text-text-secondary rounded-2xl flex items-center justify-center mx-auto mb-4">
                <FileText className="w-8 h-8" />
              </div>
              <h3 className="text-lg font-bold">No contracts found</h3>
              <p className="text-sm text-text-muted mt-1">Get started by uploading a new contract for compliance analysis.</p>
            </div>
          ) : (
            <div className="bg-card border border-border rounded-2xl overflow-hidden shadow-xl">
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="bg-slate-700/25 border-b border-border text-xs font-bold uppercase tracking-wider text-text-secondary">
                      <th className="py-4 px-6">Contract Name</th>
                      <th className="py-4 px-6">Department</th>
                      <th className="py-4 px-6">Status</th>
                      <th className="py-4 px-6">Current Version</th>
                      <th className="py-4 px-6">Last Updated</th>
                      <th className="py-4 px-6 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border/60 text-sm font-medium">
                    {filteredContracts.map((c) => (
                      <tr key={c.id} className="hover:bg-slate-700/10 transition-colors duration-150">
                        <td className="py-4 px-6">
                          <Link to={`/contracts/${c.id}`} className="flex items-center gap-3 group">
                            <div className="w-9 h-9 bg-brand/10 text-brand rounded-lg flex items-center justify-center">
                              <FileText className="w-5 h-5" />
                            </div>
                            <div>
                              <span className="text-text-primary group-hover:text-brand-light transition-colors duration-150 block">{c.name}</span>
                              <span className="text-xs text-text-muted font-normal block max-w-xs truncate">{c.description || 'No description'}</span>
                            </div>
                          </Link>
                        </td>
                        <td className="py-4 px-6 text-text-secondary">{c.department_name || 'N/A'}</td>
                        <td className="py-4 px-6">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold ${
                            c.status === 'Approved' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
                            c.status === 'Pending Review' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' :
                            c.status === 'Archived' ? 'bg-slate-500/10 text-slate-400 border border-slate-500/20' :
                            'bg-blue-500/10 text-blue-400 border border-blue-500/20'
                          }`}>
                            {c.status}
                          </span>
                        </td>
                        <td className="py-4 px-6 text-text-secondary">v{c.current_version}</td>
                        <td className="py-4 px-6 text-text-muted text-xs">{new Date(c.updated_at).toLocaleDateString()}</td>
                        <td className="py-4 px-6 text-right space-x-2">
                          {c.status === 'Archived' ? (
                            <button
                              onClick={() => handleRestore(c.id)}
                              className="p-2 bg-slate-700/40 text-text-secondary hover:text-text-primary hover:bg-slate-700 rounded-lg transition-colors duration-150"
                              title="Restore"
                            >
                              <RotateCcw className="w-4 h-4" />
                            </button>
                          ) : (
                            <button
                              onClick={() => handleArchive(c.id)}
                              className="p-2 bg-slate-700/40 text-text-secondary hover:text-text-primary hover:bg-slate-700 rounded-lg transition-colors duration-150"
                              title="Archive"
                            >
                              <Archive className="w-4 h-4" />
                            </button>
                          )}
                          <button
                            onClick={() => handleDelete(c.id)}
                            className="p-2 bg-risk-high/10 text-risk-high hover:bg-risk-high hover:text-text-primary rounded-lg transition-colors duration-150"
                            title="Delete"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </td>
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
                  <h3 className="text-lg font-bold text-text-primary">Upload Contract Agreement</h3>
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
                    <label className="text-xs font-bold uppercase tracking-wider text-text-muted mb-2 block">Contract Name</label>
                    <input
                      type="text"
                      required
                      value={uploadName}
                      onChange={(e) => setUploadName(e.target.value)}
                      className="w-full bg-background border border-border focus:border-brand rounded-xl px-4 py-2.5 text-sm outline-none"
                      placeholder="e.g. Acme Services Agreement"
                    />
                  </div>

                  <div>
                    <label className="text-xs font-bold uppercase tracking-wider text-text-muted mb-2 block">Description</label>
                    <textarea
                      value={uploadDesc}
                      onChange={(e) => setUploadDesc(e.target.value)}
                      className="w-full bg-background border border-border focus:border-brand rounded-xl px-4 py-2.5 text-sm outline-none"
                      placeholder="Brief notes about the document..."
                      rows="3"
                    />
                  </div>

                  <div>
                    <label className="text-xs font-bold uppercase tracking-wider text-text-muted mb-2 block">Department Owner</label>
                    <select
                      value={uploadDept}
                      onChange={(e) => setUploadDept(e.target.value)}
                      className="w-full bg-background border border-border rounded-xl px-4 py-2.5 text-sm outline-none"
                    >
                      {departments.map((dept) => (
                        <option key={dept.id} value={dept.id}>{dept.name}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="text-xs font-bold uppercase tracking-wider text-text-muted mb-2 block">Upload File (PDF / DOCX)</label>
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
                      <span className="text-xs text-text-muted block mt-1">Maximum upload size 50MB</span>
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
                      "Upload and Parse"
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

export default Contracts
