import React, { useState, useEffect } from 'react'
import { 
  Users, 
  Building2, 
  History, 
  ShieldAlert,
  Plus
} from 'lucide-react'
import api from '../services/api'
import Sidebar from '../components/Sidebar'
import Navbar from '../components/Navbar'

const AdminPanel = () => {
  const [users, setUsers] = useState([])
  const [departments, setDepartments] = useState([])
  const [auditLogs, setAuditLogs] = useState([])
  const [loading, setLoading] = useState(true)
  
  // Tab State
  const [activeTab, setActiveTab] = useState('users') // users, departments, logs
  
  // Department Creation State
  const [newDeptName, setNewDeptName] = useState('')
  const [newDeptDesc, setNewDeptDesc] = useState('')
  const [deptSuccess, setDeptSuccess] = useState('')
  const [deptError, setDeptError] = useState('')
  const [deptLoading, setDeptLoading] = useState(false)

  const user = JSON.parse(localStorage.getItem('user') || '{}')
  const isAdmin = user.role === 'Admin'

  const fetchData = async () => {
    try {
      setLoading(true)
      const [resUsers, resDepts, resLogs] = await Promise.all([
        api.get('/admin/users'),
        api.get('/admin/departments'),
        api.get('/admin/audit-logs')
      ])
      setUsers(resUsers.data)
      setDepartments(resDepts.data)
      setAuditLogs(resLogs.data)
    } catch (err) {
      console.error('Error fetching admin data:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (isAdmin) {
      fetchData()
    }
  }, [isAdmin])

  const handleRoleChange = async (targetUserId, newRole) => {
    try {
      await api.put(`/admin/users/${targetUserId}/role`, { role: newRole })
      await fetchData()
    } catch (err) {
      alert(err.response?.data?.msg || 'Failed to update user role')
    }
  }

  const handleCreateDept = async (e) => {
    e.preventDefault()
    setDeptError('')
    setDeptSuccess('')
    setDeptLoading(true)
    try {
      await api.post('/admin/departments', {
        name: newDeptName,
        description: newDeptDesc
      })
      setDeptSuccess('Department created successfully!')
      setNewDeptName('')
      setNewDeptDesc('')
      await fetchData()
    } catch (err) {
      setDeptError(err.response?.data?.msg || 'Failed to create department')
    } finally {
      setDeptLoading(false)
    }
  }

  if (!isAdmin) {
    return (
      <div className="flex bg-background min-h-screen text-text-primary">
        <Sidebar />
        <div className="flex-1 flex flex-col">
          <Navbar />
          <main className="flex-1 flex items-center justify-center p-8">
            <div className="bg-card border border-border p-8 rounded-2xl max-w-md text-center">
              <ShieldAlert className="w-12 h-12 text-risk-high mx-auto mb-4" />
              <h3 className="text-lg font-bold">Access Denied</h3>
              <p className="text-sm text-text-secondary mt-1">
                You do not have administrative privileges to access this console. Please contact system administrators if you believe this is in error.
              </p>
            </div>
          </main>
        </div>
      </div>
    )
  }

  return (
    <div className="flex bg-background min-h-screen text-text-primary">
      <Sidebar />
      
      <div className="flex-1 flex flex-col min-w-0">
        <Navbar />
        
        <main className="flex-1 overflow-y-auto p-8 space-y-6">
          {/* Header */}
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-text-primary">Administration Console</h1>
            <p className="text-sm text-text-secondary">Control authorization policies, manage departments, and audit security events</p>
          </div>

          {/* Admin Tabs */}
          <div className="flex border-b border-border bg-card/25 rounded-xl p-1 gap-2 max-w-md">
            <button
              onClick={() => setActiveTab('users')}
              className={`px-4 py-2 text-xs font-semibold rounded-lg flex items-center gap-2 transition-all duration-200 ${
                activeTab === 'users' ? 'bg-brand text-text-primary' : 'text-text-secondary hover:text-text-primary'
              }`}
            >
              <Users className="w-4 h-4" />
              <span>Users</span>
            </button>
            <button
              onClick={() => setActiveTab('departments')}
              className={`px-4 py-2 text-xs font-semibold rounded-lg flex items-center gap-2 transition-all duration-200 ${
                activeTab === 'departments' ? 'bg-brand text-text-primary' : 'text-text-secondary hover:text-text-primary'
              }`}
            >
              <Building2 className="w-4 h-4" />
              <span>Departments</span>
            </button>
            <button
              onClick={() => setActiveTab('logs')}
              className={`px-4 py-2 text-xs font-semibold rounded-lg flex items-center gap-2 transition-all duration-200 ${
                activeTab === 'logs' ? 'bg-brand text-text-primary' : 'text-text-secondary hover:text-text-primary'
              }`}
            >
              <History className="w-4 h-4" />
              <span>Audit Logs</span>
            </button>
          </div>

          {/* Tab Content */}
          {loading ? (
            <div className="flex items-center justify-center py-20">
              <div className="w-10 h-10 border-4 border-brand/30 border-t-brand rounded-full animate-spin"></div>
            </div>
          ) : (
            <div className="space-y-6">
              
              {/* TAB 1: USERS */}
              {activeTab === 'users' && (
                <div className="bg-card border border-border rounded-2xl overflow-hidden shadow-xl">
                  <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse">
                      <thead>
                        <tr className="bg-slate-700/25 border-b border-border text-xs font-bold uppercase tracking-wider text-text-secondary">
                          <th className="py-4 px-6">User Name</th>
                          <th className="py-4 px-6">Email</th>
                          <th className="py-4 px-6">Department</th>
                          <th className="py-4 px-6">Role</th>
                          <th className="py-4 px-6">Member Since</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-border/60 text-sm font-medium">
                        {users.map((u) => (
                          <tr key={u.id} className="hover:bg-slate-700/10 transition-colors duration-150">
                            <td className="py-4 px-6 text-text-primary">{u.full_name}</td>
                            <td className="py-4 px-6 text-text-secondary">{u.email}</td>
                            <td className="py-4 px-6 text-text-secondary">{u.department_name || 'N/A'}</td>
                            <td className="py-4 px-6">
                              <select
                                value={u.role}
                                onChange={(e) => handleRoleChange(u.id, e.target.value)}
                                className="bg-background border border-border rounded-lg px-2 py-1 text-xs font-semibold outline-none cursor-pointer"
                              >
                                <option value="Viewer">Viewer</option>
                                <option value="Auditor">Auditor</option>
                                <option value="Legal Reviewer">Legal Reviewer</option>
                                <option value="Compliance Officer">Compliance Officer</option>
                                <option value="Admin">Admin</option>
                              </select>
                            </td>
                            <td className="py-4 px-6 text-text-muted text-xs">{new Date(u.created_at).toLocaleDateString()}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* TAB 2: DEPARTMENTS */}
              {activeTab === 'departments' && (
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  
                  {/* Create Department Form */}
                  <div className="bg-card border border-border p-6 rounded-2xl flex flex-col shadow-xl self-start">
                    <div className="flex items-center gap-2 mb-6">
                      <Building2 className="w-5 h-5 text-brand" />
                      <h3 className="text-sm font-bold uppercase tracking-wider text-text-secondary">Provision Department</h3>
                    </div>

                    {deptError && (
                      <div className="bg-risk-high/15 border border-risk-high/30 text-risk-high text-xs px-4 py-2.5 rounded-xl mb-4">
                        {deptError}
                      </div>
                    )}
                    {deptSuccess && (
                      <div className="bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 text-xs px-4 py-2.5 rounded-xl mb-4">
                        {deptSuccess}
                      </div>
                    )}

                    <form onSubmit={handleCreateDept} className="space-y-4">
                      <div>
                        <label className="text-xs font-bold uppercase tracking-wider text-text-muted mb-2 block">Name</label>
                        <input
                          type="text"
                          required
                          value={newDeptName}
                          onChange={(e) => setNewDeptName(e.target.value)}
                          className="w-full bg-background border border-border focus:border-brand rounded-xl px-4 py-2 text-xs outline-none"
                          placeholder="e.g. Procurement Division"
                        />
                      </div>
                      <div>
                        <label className="text-xs font-bold uppercase tracking-wider text-text-muted mb-2 block">Description</label>
                        <textarea
                          value={newDeptDesc}
                          onChange={(e) => setNewDeptDesc(e.target.value)}
                          className="w-full bg-background border border-border focus:border-brand rounded-xl px-4 py-2 text-xs outline-none"
                          placeholder="Purpose / Scope..."
                          rows="3"
                        />
                      </div>

                      <button
                        type="submit"
                        disabled={deptLoading}
                        className="w-full bg-brand hover:bg-brand-dark text-text-primary text-xs font-bold py-2.5 rounded-xl shadow-lg flex items-center justify-center gap-2"
                      >
                        <Plus className="w-4 h-4" />
                        <span>Add Department</span>
                      </button>
                    </form>
                  </div>

                  {/* Departments List */}
                  <div className="bg-card border border-border rounded-2xl overflow-hidden shadow-xl lg:col-span-2">
                    <div className="overflow-x-auto">
                      <table className="w-full text-left border-collapse">
                        <thead>
                          <tr className="bg-slate-700/25 border-b border-border text-xs font-bold uppercase tracking-wider text-text-secondary">
                            <th className="py-4 px-6">Department Name</th>
                            <th className="py-4 px-6">Description</th>
                            <th className="py-4 px-6">User Count</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-border/60 text-sm font-medium">
                          {departments.map((dept) => (
                            <tr key={dept.id} className="hover:bg-slate-700/10 transition-colors duration-150">
                              <td className="py-4 px-6 text-text-primary">{dept.name}</td>
                              <td className="py-4 px-6 text-text-secondary">{dept.description || 'N/A'}</td>
                              <td className="py-4 px-6 text-text-muted">{dept.user_count || 0} Members</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>

                </div>
              )}

              {/* TAB 3: AUDIT LOGS */}
              {activeTab === 'logs' && (
                <div className="bg-card border border-border rounded-2xl overflow-hidden shadow-xl">
                  <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse">
                      <thead>
                        <tr className="bg-slate-700/25 border-b border-border text-xs font-bold uppercase tracking-wider text-text-secondary">
                          <th className="py-4 px-6">Timestamp</th>
                          <th className="py-4 px-6">Triggered By</th>
                          <th className="py-4 px-6">Action Category</th>
                          <th className="py-4 px-6">Details</th>
                          <th className="py-4 px-6">IP Address</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-border/60 text-xs font-semibold text-text-secondary">
                        {auditLogs.map((log) => (
                          <tr key={log.id} className="hover:bg-slate-700/10 transition-colors duration-150">
                            <td className="py-4 px-6 text-text-muted">{new Date(log.created_at).toLocaleString()}</td>
                            <td className="py-4 px-6 text-text-primary">{log.user_name || 'System'}</td>
                            <td className="py-4 px-6">
                              <span className="inline-flex items-center px-2 py-0.5 rounded bg-slate-700/40 border border-border/80 text-[9px] font-bold text-text-muted">
                                {log.action}
                              </span>
                            </td>
                            <td className="py-4 px-6 text-text-primary">{log.details}</td>
                            <td className="py-4 px-6 text-text-muted font-mono">{log.ip_address || '127.0.0.1'}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

            </div>
          )}

        </main>
      </div>
    </div>
  )
}

export default AdminPanel
