import React, { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { UserPlus, Mail, Lock, User as UserIcon, Building2 } from 'lucide-react'
import api from '../services/api'

const Register = () => {
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [role, setRole] = useState('Viewer')
  const [departmentId, setDepartmentId] = useState('')
  const [departments, setDepartments] = useState([])
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    const fetchDepartments = async () => {
      try {
        const res = await api.get('/admin/departments')
        setDepartments(res.data)
        if (res.data.length > 0) {
          setDepartmentId(res.data[0].id)
        }
      } catch (err) {
        // Fallback static departments
        const fallbackDepts = [
          { id: 'legal-id', name: 'Legal' },
          { id: 'compliance-id', name: 'Compliance' },
          { id: 'procurement-id', name: 'Procurement' },
          { id: 'engineering-id', name: 'Engineering' }
        ]
        setDepartments(fallbackDepts)
        setDepartmentId(fallbackDepts[0].id)
      }
    }
    fetchDepartments()
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess('')
    setLoading(true)

    try {
      await api.post('/auth/register', {
        email,
        password,
        full_name: fullName,
        role,
        department_id: departmentId
      })
      setSuccess('Account created successfully! Redirecting to login...')
      setTimeout(() => {
        navigate('/login')
      }, 2500)
    } catch (err) {
      setError(err.response?.data?.msg || 'Failed to request account. Please check your entries.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#0B0F19] bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-indigo-900/30 via-slate-900 to-[#0B0F19] flex items-center justify-center p-6">
      <div className="w-full max-w-lg bg-card/60 backdrop-blur-xl border border-border/80 rounded-3xl shadow-2xl p-8 flex flex-col items-center">
        
        {/* Header */}
        <div className="bg-brand w-14 h-14 rounded-2xl flex items-center justify-center text-text-primary text-2xl shadow-xl shadow-brand/35 mb-4">
          🛡️
        </div>
        <h2 className="text-2xl font-bold text-text-primary mb-1">Create Workstation Account</h2>
        <p className="text-sm text-text-secondary mb-8">Access the compliance auditing system</p>

        {/* Notifications */}
        {error && (
          <div className="w-full bg-risk-high/15 border border-risk-high/30 text-risk-high text-sm px-4 py-3 rounded-2xl mb-6">
            {error}
          </div>
        )}
        {success && (
          <div className="w-full bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 text-sm px-4 py-3 rounded-2xl mb-6 animate-pulse">
            {success}
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="w-full grid grid-cols-1 md:grid-cols-2 gap-5">
          <div className="md:col-span-2">
            <label className="text-xs font-bold uppercase tracking-wider text-text-muted mb-2 block">
              Full Name
            </label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 pl-4 flex items-center text-text-muted">
                <UserIcon className="w-5 h-5" />
              </span>
              <input
                type="text"
                required
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="w-full bg-background border border-border focus:border-brand rounded-2xl pl-12 pr-4 py-3 text-sm text-text-primary focus:ring-1 focus:ring-brand outline-none transition-all duration-200"
                placeholder="Jane Doe"
              />
            </div>
          </div>

          <div className="md:col-span-2">
            <label className="text-xs font-bold uppercase tracking-wider text-text-muted mb-2 block">
              Business Email
            </label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 pl-4 flex items-center text-text-muted">
                <Mail className="w-5 h-5" />
              </span>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-background border border-border focus:border-brand rounded-2xl pl-12 pr-4 py-3 text-sm text-text-primary focus:ring-1 focus:ring-brand outline-none transition-all duration-200"
                placeholder="jane@company.com"
              />
            </div>
          </div>

          <div className="md:col-span-2">
            <label className="text-xs font-bold uppercase tracking-wider text-text-muted mb-2 block">
              Password
            </label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 pl-4 flex items-center text-text-muted">
                <Lock className="w-5 h-5" />
              </span>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-background border border-border focus:border-brand rounded-2xl pl-12 pr-4 py-3 text-sm text-text-primary focus:ring-1 focus:ring-brand outline-none transition-all duration-200"
                placeholder="••••••••"
              />
            </div>
          </div>

          <div>
            <label className="text-xs font-bold uppercase tracking-wider text-text-muted mb-2 block">
              Auditing Role
            </label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 pl-4 flex items-center text-text-muted">
                <UserIcon className="w-5 h-5" />
              </span>
              <select
                value={role}
                onChange={(e) => setRole(e.target.value)}
                className="w-full bg-background border border-border focus:border-brand rounded-2xl pl-12 pr-4 py-3 text-sm text-text-primary outline-none transition-all duration-200"
              >
                <option value="Viewer">Viewer</option>
                <option value="Auditor">Auditor</option>
                <option value="Legal Reviewer">Legal Reviewer</option>
                <option value="Compliance Officer">Compliance Officer</option>
                <option value="Admin">Admin</option>
              </select>
            </div>
          </div>

          <div>
            <label className="text-xs font-bold uppercase tracking-wider text-text-muted mb-2 block">
              Department
            </label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 pl-4 flex items-center text-text-muted">
                <Building2 className="w-5 h-5" />
              </span>
              <select
                value={departmentId}
                onChange={(e) => setDepartmentId(e.target.value)}
                className="w-full bg-background border border-border focus:border-brand rounded-2xl pl-12 pr-4 py-3 text-sm text-text-primary outline-none transition-all duration-200"
              >
                {departments.map((dept) => (
                  <option key={dept.id} value={dept.id}>{dept.name}</option>
                ))}
              </select>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="md:col-span-2 w-full bg-brand hover:bg-brand-dark disabled:opacity-50 text-text-primary font-bold py-3.5 rounded-2xl shadow-lg shadow-brand/20 transition-all duration-200 flex items-center justify-center gap-2 mt-4"
          >
            {loading ? (
              <span className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
            ) : (
              "Submit Registration"
            )}
          </button>
        </form>

        {/* Redirect */}
        <p className="text-sm text-text-secondary mt-8">
          Already registered?{' '}
          <Link to="/login" className="text-brand-light hover:underline font-semibold">
            Sign In instead
          </Link>
        </p>
      </div>
    </div>
  )
}

export default Register
