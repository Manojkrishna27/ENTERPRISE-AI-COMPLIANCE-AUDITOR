import React, { useState, useEffect } from 'react'
import { 
  FileSpreadsheet, 
  Download, 
  Search,
  Calendar,
  FileText
} from 'lucide-react'
import api from '../services/api'
import Sidebar from '../components/Sidebar'
import Navbar from '../components/Navbar'

const Reports = () => {
  const [reports, setReports] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')

  const fetchReports = async () => {
    try {
      const res = await api.get('/reports')
      setReports(res.data)
    } catch (err) {
      console.error('Error fetching reports:', err)
    }
  }



  useEffect(() => {
    const init = async () => {
      setLoading(true)
      await fetchReports()
      setLoading(false)
    }
    init()
  }, [])

  const filteredReports = reports.filter((r) => 
    r.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (r.contract_name && r.contract_name.toLowerCase().includes(searchQuery.toLowerCase()))
  )

  return (
    <div className="flex bg-background min-h-screen text-text-primary">
      <Sidebar />
      
      <div className="flex-1 flex flex-col min-w-0">
        <Navbar />
        
        <main className="flex-1 overflow-y-auto p-8 space-y-6">
          {/* Header */}
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-text-primary">Compliance Audit Reports</h1>
            <p className="text-sm text-text-secondary">Download legally formatted executive compliance reports</p>
          </div>

          {/* Search bar */}
          <div className="bg-card border border-border p-4 rounded-2xl flex items-center max-w-md">
            <span className="text-text-muted mr-3">
              <Search className="w-4 h-4" />
            </span>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-transparent text-xs text-text-primary outline-none"
              placeholder="Filter reports by contract name..."
            />
          </div>

          {/* List / Cards */}
          {loading ? (
            <div className="flex items-center justify-center py-20">
              <div className="w-10 h-10 border-4 border-brand/30 border-t-brand rounded-full animate-spin"></div>
            </div>
          ) : filteredReports.length === 0 ? (
            <div className="bg-card border border-border rounded-2xl p-16 text-center">
              <div className="w-16 h-16 bg-slate-700/35 text-text-secondary rounded-2xl flex items-center justify-center mx-auto mb-4">
                <FileSpreadsheet className="w-8 h-8" />
              </div>
              <h3 className="text-lg font-bold">No reports generated yet</h3>
              <p className="text-sm text-text-muted mt-1">Open a contract agreement and select 'Audit PDF' to trigger a compilation.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredReports.map((report) => (
                <div 
                   key={report.id} 
                  className="bg-card border border-border p-5 rounded-2xl flex flex-col justify-between hover:border-brand/40 transition-all duration-200"
                >
                  <div>
                    <div className="flex items-center gap-3 mb-4">
                      <div className="w-10 h-10 bg-brand/10 text-brand rounded-xl flex items-center justify-center">
                        <FileSpreadsheet className="w-5 h-5" />
                      </div>
                      <div className="min-w-0">
                        <h4 className="text-xs font-bold text-text-primary truncate">{report.name}</h4>
                        <span className="text-[9px] bg-slate-700/60 text-text-secondary font-bold px-2 py-0.5 rounded-full inline-block mt-1">
                          {report.report_type}
                        </span>
                      </div>
                    </div>

                    <div className="space-y-2.5 text-xs text-text-secondary font-medium mt-6">
                      <div className="flex items-center gap-2 text-text-muted">
                        <Calendar className="w-4 h-4" />
                        <span>Generated: {new Date(report.created_at).toLocaleDateString()}</span>
                      </div>
                      <div className="flex items-center gap-2 text-text-muted">
                        <FileText className="w-4 h-4" />
                        <span>Ref Contract ID: {report.contract_id?.substring(0, 8)}...</span>
                      </div>
                    </div>
                  </div>

                  <a
                    href={`/api/reports/${report.id}/download?jwt=${localStorage.getItem('access_token')}`}
                    download
                    className="w-full bg-slate-700 hover:bg-slate-600 text-text-primary text-xs font-bold py-2.5 rounded-xl flex items-center justify-center gap-2 mt-6 transition-all duration-150"
                  >
                    <Download className="w-4 h-4" />
                    <span>Download PDF</span>
                  </a>
                </div>
              ))}
            </div>
          )}

        </main>
      </div>
    </div>
  )
}

export default Reports
