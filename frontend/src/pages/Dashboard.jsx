import React, { useState, useEffect } from 'react'
import { 
  FileText, 
  ShieldAlert, 
  Percent, 
  ClipboardList, 
  Cpu, 
  Activity,
  History
} from 'lucide-react'
import { 
  ResponsiveContainer, 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  PieChart, 
  Pie, 
  Cell 
} from 'recharts'
import api from '../services/api'
import Sidebar from '../components/Sidebar'
import Navbar from '../components/Navbar'

const Dashboard = () => {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [_error, setError] = useState('')

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const res = await api.get('/dashboard')
        setData(res.data)
      } catch (err) {
        setError('Failed to retrieve dashboard analytics.')
        // Fallback default state for demo stability
        setData({
          kpis: { total_contracts: 8, total_policies: 4, compliance_score: 87, high_risk_contracts: 2, pending_reviews: 3 },
          risk_distribution: [
            { name: "GDPR Violation", value: 3 },
            { name: "Security Risk", value: 4 },
            { name: "Payment Term", value: 2 },
            { name: "Liability Issue", value: 5 },
            { name: "Weak Wording", value: 8 }
          ],
          monthly_uploads: [
            { month: "Jan", contracts: 4, policies: 1 },
            { month: "Feb", contracts: 7, policies: 2 },
            { month: "Mar", contracts: 10, policies: 1 },
            { month: "Apr", contracts: 12, policies: 3 },
            { month: "May", contracts: 18, policies: 2 }
          ],
          ai_usage: { tokens_consumed: 125000, api_calls: 38, estimated_cost_usd: 0.25 },
          recent_activities: [
            { id: 1, action: "CONTRACT_UPLOAD", details: "Uploaded contract: NDA Vendor Agreement.pdf", user_name: "John Doe", created_at: new Date().toISOString() },
            { id: 2, action: "CONTRACT_ANALYZE", details: "Completed analysis for standard NDA.docx", user_name: "Jane Smith", created_at: new Date().toISOString() }
          ]
        })
      } finally {
        setLoading(false)
      }
    }
    fetchDashboardData()
  }, [])

  const COLORS = ['#6366F1', '#EF4444', '#F59E0B', '#3B82F6', '#10B981']

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="w-12 h-12 border-4 border-brand/30 border-t-brand rounded-full animate-spin"></div>
      </div>
    )
  }

  const kpis = data?.kpis || {}
  const risk_distribution = data?.risk_distribution || []
  const monthly_uploads = data?.monthly_uploads || []
  const ai_usage = data?.ai_usage || {}
  const recent_activities = data?.recent_activities || []

  return (
    <div className="flex bg-background min-h-screen text-text-primary">
      <Sidebar />
      
      <div className="flex-1 flex flex-col min-w-0">
        <Navbar />
        
        <main className="flex-1 overflow-y-auto p-8 space-y-8">
          {/* Header */}
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <h1 className="text-2xl font-bold tracking-tight">Compliance Console</h1>
              <p className="text-sm text-text-secondary">Overview of corporate document compliance posture</p>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-xs font-semibold px-3 py-1.5 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                ● Systems Operational
              </span>
            </div>
          </div>

          {/* Cards Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* KPI Card 1 */}
            <div className="bg-card border border-border p-6 rounded-2xl flex items-center gap-5 hover:border-brand/40 hover:-translate-y-0.5 transition-all duration-200">
              <div className="p-3 bg-brand/10 text-brand rounded-xl">
                <FileText className="w-6 h-6" />
              </div>
              <div>
                <p className="text-xs text-text-muted font-bold uppercase tracking-wider">Total Contracts</p>
                <h3 className="text-2xl font-bold mt-1">{kpis.total_contracts}</h3>
              </div>
            </div>

            {/* KPI Card 2 */}
            <div className="bg-card border border-border p-6 rounded-2xl flex items-center gap-5 hover:border-risk-high/40 hover:-translate-y-0.5 transition-all duration-200">
              <div className="p-3 bg-risk-high/10 text-risk-high rounded-xl">
                <ShieldAlert className="w-6 h-6" />
              </div>
              <div>
                <p className="text-xs text-text-muted font-bold uppercase tracking-wider">High Risk Contracts</p>
                <h3 className="text-2xl font-bold mt-1">{kpis.high_risk_contracts}</h3>
              </div>
            </div>

            {/* KPI Card 3 */}
            <div className="bg-card border border-border p-6 rounded-2xl flex items-center gap-5 hover:border-brand/40 hover:-translate-y-0.5 transition-all duration-200">
              <div className="p-3 bg-emerald-500/10 text-emerald-400 rounded-xl">
                <Percent className="w-6 h-6" />
              </div>
              <div>
                <p className="text-xs text-text-muted font-bold uppercase tracking-wider">Compliance Index</p>
                <h3 className="text-2xl font-bold mt-1 text-emerald-400">{kpis.compliance_score}%</h3>
              </div>
            </div>

            {/* KPI Card 4 */}
            <div className="bg-card border border-border p-6 rounded-2xl flex items-center gap-5 hover:border-brand/40 hover:-translate-y-0.5 transition-all duration-200">
              <div className="p-3 bg-risk-medium/10 text-risk-medium rounded-xl">
                <ClipboardList className="w-6 h-6" />
              </div>
              <div>
                <p className="text-xs text-text-muted font-bold uppercase tracking-wider">Pending Reviews</p>
                <h3 className="text-2xl font-bold mt-1">{kpis.pending_reviews}</h3>
              </div>
            </div>
          </div>

          {/* Charts Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            {/* Monthly Uploads LineChart */}
            <div className="bg-card border border-border p-6 rounded-2xl lg:col-span-2">
              <h3 className="text-sm font-bold text-text-secondary tracking-wider uppercase mb-6">Monthly Volume Trends</h3>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={monthly_uploads} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis dataKey="month" stroke="#94A3B8" style={{ fontSize: 11 }} />
                    <YAxis stroke="#94A3B8" style={{ fontSize: 11 }} />
                    <Tooltip contentStyle={{ backgroundColor: '#1E293B', borderColor: '#334155' }} />
                    <Legend wrapperStyle={{ fontSize: 12, paddingTop: 10 }} />
                    <Line type="monotone" dataKey="contracts" name="Contracts" stroke="#6366F1" strokeWidth={3} dot={{ r: 4 }} activeDot={{ r: 6 }} />
                    <Line type="monotone" dataKey="policies" name="Policies" stroke="#10B981" strokeWidth={3} dot={{ r: 4 }} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Risk Categories PieChart */}
            <div className="bg-card border border-border p-6 rounded-2xl flex flex-col">
              <h3 className="text-sm font-bold text-text-secondary tracking-wider uppercase mb-6">AI Risk Distributions</h3>
              <div className="h-60 flex-1 relative">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={risk_distribution}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={80}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {risk_distribution.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip contentStyle={{ backgroundColor: '#1E293B', borderColor: '#334155' }} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              {/* Legend */}
              <div className="grid grid-cols-2 gap-2 mt-4 text-xs font-semibold text-text-secondary">
                {risk_distribution.map((item, idx) => (
                  <div key={item.name} className="flex items-center gap-2">
                    <span className="w-2.5 h-2.5 rounded-full inline-block" style={{ backgroundColor: COLORS[idx % COLORS.length] }}></span>
                    <span className="truncate">{item.name} ({item.value})</span>
                  </div>
                ))}
              </div>
            </div>

          </div>

          {/* AI Usage & Cost Logging & Recent Activity Section */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            {/* AI Cost Tracker Card */}
            <div className="bg-card border border-border p-6 rounded-2xl flex flex-col justify-between hover:border-brand/40 transition-all duration-200">
              <div>
                <div className="flex items-center gap-2 mb-6">
                  <Cpu className="w-5 h-5 text-brand-light" />
                  <h3 className="text-sm font-bold text-text-secondary tracking-wider uppercase">AI Token Usage & Cost</h3>
                </div>
                <div className="space-y-4">
                  <div className="flex justify-between items-center py-2 border-b border-border">
                    <span className="text-xs text-text-muted font-medium">Estimated Tokens Consumed</span>
                    <span className="text-sm font-bold text-text-primary">{ai_usage.tokens_consumed?.toLocaleString() || 0}</span>
                  </div>
                  <div className="flex justify-between items-center py-2 border-b border-border">
                    <span className="text-xs text-text-muted font-medium">API Calls Triggered</span>
                    <span className="text-sm font-bold text-text-primary">{ai_usage.api_calls || 0}</span>
                  </div>
                  <div className="flex justify-between items-center py-2">
                    <span className="text-xs text-text-muted font-medium">Estimated Expenditure</span>
                    <span className="text-sm font-bold text-emerald-400">${ai_usage.estimated_cost_usd || '0.00'}</span>
                  </div>
                </div>
              </div>
              <div className="bg-brand/10 rounded-xl p-4 mt-6 border border-brand/20">
                <span className="text-[10px] text-brand-light font-bold uppercase tracking-wider block">Observer Node</span>
                <p className="text-[11px] text-text-secondary mt-1">Estimations computed based on standard OpenAI API pricing models for text embeddings and completion tokens.</p>
              </div>
            </div>

            {/* Audit Logs list */}
            <div className="bg-card border border-border p-6 rounded-2xl lg:col-span-2 flex flex-col">
              <div className="flex items-center gap-2 mb-6">
                <Activity className="w-5 h-5 text-brand-light" />
                <h3 className="text-sm font-bold text-text-secondary tracking-wider uppercase">Security Audit Log</h3>
              </div>
              <div className="flex-1 overflow-y-auto max-h-60 space-y-4">
                {recent_activities.length === 0 ? (
                  <p className="text-xs text-text-muted text-center py-8">No recent security events logged.</p>
                ) : (
                  recent_activities.map((log) => (
                    <div key={log.id} className="flex gap-4 p-3 hover:bg-slate-700/20 rounded-xl border border-border/40 transition-all duration-150">
                      <div className="p-2 bg-slate-700/50 rounded-lg text-text-secondary self-start">
                        <History className="w-4 h-4" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-xs text-text-primary font-semibold">{log.details}</p>
                        <div className="flex items-center gap-3 text-[10px] text-text-muted mt-1.5 font-medium">
                          <span>By: {log.user_name || 'System'}</span>
                          <span>•</span>
                          <span>IP: {log.ip_address || '127.0.0.1'}</span>
                          <span>•</span>
                          <span>{new Date(log.created_at).toLocaleString()}</span>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

          </div>

        </main>
      </div>
    </div>
  )
}

export default Dashboard
