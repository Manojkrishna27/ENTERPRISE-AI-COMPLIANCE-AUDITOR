import React, { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { UserPlus, Mail, Lock, User as UserIcon, Building2, ArrowRight, ChevronLeft, ShieldCheck } from 'lucide-react'
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
    <div className="min-h-screen w-full flex bg-[#09090b] text-slate-100 overflow-hidden font-sans">
      
      {/* Left side: Register Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 sm:p-12 relative z-10 overflow-y-auto">
        
        {/* Mobile Logo */}
        <div className="absolute top-8 left-8 flex items-center gap-3 lg:hidden">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-blue-600 flex items-center justify-center">
              <ShieldCheck className="text-white w-5 h-5" />
            </div>
            <span className="text-lg font-bold tracking-tight text-white">TrustGuard AI</span>
        </div>

        <div className="w-full max-w-lg space-y-8 py-10">
          <div className="text-center sm:text-left">
            <h2 className="text-3xl font-bold tracking-tight text-white mb-2">Request Access</h2>
            <p className="text-slate-400 text-sm">Join your team's compliance workspace</p>
          </div>

          {error && (
            <div className="bg-red-500/10 border border-red-500/20 text-red-400 text-sm px-4 py-3 rounded-xl flex items-center gap-3 animate-in fade-in slide-in-from-top-2">
              <div className="w-1.5 h-1.5 rounded-full bg-red-400"></div>
              {error}
            </div>
          )}
          {success && (
            <div className="bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-sm px-4 py-3 rounded-xl flex items-center gap-3 animate-in fade-in slide-in-from-top-2">
              <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></div>
              {success}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              
              <div className="space-y-1.5 md:col-span-2">
                <label className="text-sm font-medium text-slate-300">
                  Full Name
                </label>
                <div className="relative group">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500 group-focus-within:text-indigo-400 transition-colors">
                    <UserIcon className="w-5 h-5" />
                  </div>
                  <input
                    type="text"
                    required
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    className="w-full bg-white/5 border border-white/10 text-white rounded-xl pl-11 pr-4 py-3 text-sm focus:bg-white/10 focus:border-indigo-500/50 focus:ring-2 focus:ring-indigo-500/20 outline-none transition-all placeholder:text-slate-600"
                    placeholder="Jane Doe"
                  />
                </div>
              </div>

              <div className="space-y-1.5 md:col-span-2">
                <label className="text-sm font-medium text-slate-300">
                  Business Email
                </label>
                <div className="relative group">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500 group-focus-within:text-indigo-400 transition-colors">
                    <Mail className="w-5 h-5" />
                  </div>
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full bg-white/5 border border-white/10 text-white rounded-xl pl-11 pr-4 py-3 text-sm focus:bg-white/10 focus:border-indigo-500/50 focus:ring-2 focus:ring-indigo-500/20 outline-none transition-all placeholder:text-slate-600"
                    placeholder="name@company.com"
                  />
                </div>
              </div>

              <div className="space-y-1.5 md:col-span-2">
                <label className="text-sm font-medium text-slate-300">
                  Password
                </label>
                <div className="relative group">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500 group-focus-within:text-indigo-400 transition-colors">
                    <Lock className="w-5 h-5" />
                  </div>
                  <input
                    type="password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full bg-white/5 border border-white/10 text-white rounded-xl pl-11 pr-4 py-3 text-sm focus:bg-white/10 focus:border-indigo-500/50 focus:ring-2 focus:ring-indigo-500/20 outline-none transition-all placeholder:text-slate-600"
                    placeholder="••••••••"
                  />
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-sm font-medium text-slate-300">
                  Auditing Role
                </label>
                <div className="relative group">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500 group-focus-within:text-indigo-400 transition-colors">
                    <UserPlus className="w-5 h-5" />
                  </div>
                  <select
                    value={role}
                    onChange={(e) => setRole(e.target.value)}
                    className="w-full bg-white/5 border border-white/10 text-white rounded-xl pl-11 pr-4 py-3 text-sm focus:bg-white/10 focus:border-indigo-500/50 focus:ring-2 focus:ring-indigo-500/20 outline-none transition-all appearance-none cursor-pointer"
                  >
                    <option value="Viewer" className="bg-[#0f172a]">Viewer</option>
                    <option value="Auditor" className="bg-[#0f172a]">Auditor</option>
                    <option value="Legal Reviewer" className="bg-[#0f172a]">Legal Reviewer</option>
                    <option value="Compliance Officer" className="bg-[#0f172a]">Compliance Officer</option>
                    <option value="Admin" className="bg-[#0f172a]">Admin</option>
                  </select>
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-sm font-medium text-slate-300">
                  Department
                </label>
                <div className="relative group">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500 group-focus-within:text-indigo-400 transition-colors">
                    <Building2 className="w-5 h-5" />
                  </div>
                  <select
                    value={departmentId}
                    onChange={(e) => setDepartmentId(e.target.value)}
                    className="w-full bg-white/5 border border-white/10 text-white rounded-xl pl-11 pr-4 py-3 text-sm focus:bg-white/10 focus:border-indigo-500/50 focus:ring-2 focus:ring-indigo-500/20 outline-none transition-all appearance-none cursor-pointer"
                  >
                    {departments.map((dept) => (
                      <option key={dept.id} value={dept.id} className="bg-[#0f172a]">{dept.name}</option>
                    ))}
                  </select>
                </div>
              </div>

            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full relative group overflow-hidden rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-medium py-3 text-sm transition-all duration-300 disabled:opacity-70 disabled:cursor-not-allowed mt-2"
            >
              <div className="absolute inset-0 w-full h-full bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover:animate-[shimmer_1.5s_infinite]"></div>
              <div className="relative flex items-center justify-center gap-2">
                {loading ? (
                  <span className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                ) : (
                  <>
                    Submit Registration
                    <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                  </>
                )}
              </div>
            </button>
          </form>

          <div className="mt-8 pt-8 border-t border-white/5 text-center">
            <p className="text-sm text-slate-400">
              Already have an account?{' '}
              <Link to="/login" className="text-white font-medium hover:text-indigo-400 inline-flex items-center transition-colors">
                <ChevronLeft className="w-4 h-4 mr-0.5" /> Back to sign in
              </Link>
            </p>
          </div>
        </div>
      </div>

      {/* Right side: Premium Branding & Visuals (mirrored from login) */}
      <div className="hidden lg:flex lg:w-1/2 relative flex-col justify-between p-12 overflow-hidden border-l border-white/5 bg-[#0a0a0f]">
        
        {/* Animated Background Gradients */}
        <div className="absolute bottom-[-20%] right-[-10%] w-[70%] h-[70%] bg-blue-600/20 rounded-full blur-[120px] mix-blend-screen animate-pulse"></div>
        <div className="absolute top-[-10%] left-[-10%] w-[60%] h-[60%] bg-indigo-600/20 rounded-full blur-[100px] mix-blend-screen" style={{ animationDelay: '1s', animationDuration: '8s' }}></div>
        
        {/* Grid Pattern Overlay */}
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 brightness-100 contrast-150"></div>
        <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:40px_40px] [mask-image:radial-gradient(ellipse_80%_80%_at_50%_50%,#000_20%,transparent_100%)]"></div>

        <div className="relative z-10 self-end">
          <div className="flex items-center gap-3">
            <span className="text-xl font-bold tracking-tight text-white">TrustGuard AI</span>
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-blue-600 flex items-center justify-center shadow-lg shadow-indigo-500/20">
              <ShieldCheck className="text-white w-6 h-6" />
            </div>
          </div>
        </div>
        
        <div className="relative z-10 mb-20">
          <h1 className="text-5xl font-extrabold tracking-tight mb-6 leading-tight">
            Built for <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-cyan-400">scale.</span><br />
            Designed for <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-blue-400">security.</span>
          </h1>
          <p className="text-lg text-slate-400 max-w-md font-light leading-relaxed">
            Join thousands of legal and compliance professionals relying on TrustGuard AI for automated contract intelligence.
          </p>
          
          <div className="mt-12 flex gap-4">
             <div className="flex items-center gap-2 text-sm text-slate-400 bg-white/5 backdrop-blur-md px-4 py-2 rounded-full border border-white/5">
                <UserPlus className="w-4 h-4 text-indigo-400" /> RBAC Support
             </div>
             <div className="flex items-center gap-2 text-sm text-slate-400 bg-white/5 backdrop-blur-md px-4 py-2 rounded-full border border-white/5">
                <Building2 className="w-4 h-4 text-emerald-400" /> Multi-Tenant
             </div>
          </div>
        </div>
      </div>

    </div>
  )
}

export default Register
