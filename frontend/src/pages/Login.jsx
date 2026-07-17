import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { ShieldCheck, Mail, Lock } from 'lucide-react'
import api from '../services/api'

const Login = () => {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const res = await api.post('/auth/login', { email, password })
      localStorage.setItem('access_token', res.data.access_token)
      localStorage.setItem('user', JSON.stringify(res.data.user))
      navigate('/')
    } catch (err) {
      setError(err.response?.data?.msg || 'Invalid credentials. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#0B0F19] bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-indigo-900/30 via-slate-900 to-[#0B0F19] flex items-center justify-center p-6">
      <div className="w-full max-w-md bg-card/60 backdrop-blur-xl border border-border/80 rounded-3xl shadow-2xl p-8 flex flex-col items-center">
        
        {/* Brand Logo */}
        <div className="bg-brand w-14 h-14 rounded-2xl flex items-center justify-center text-text-primary text-2xl shadow-xl shadow-brand/35 mb-4 animate-bounce">
          🛡️
        </div>
        <h2 className="text-2xl font-bold text-text-primary mb-1">Corporate Login</h2>
        <p className="text-sm text-text-secondary mb-8">AI Compliance & Contract Auditor</p>

        {/* Error Notification */}
        {error && (
          <div className="w-full bg-risk-high/15 border border-risk-high/30 text-risk-high text-sm px-4 py-3 rounded-2xl mb-6">
            {error}
          </div>
        )}

        {/* Login Form */}
        <form onSubmit={handleSubmit} className="w-full space-y-5">
          <div>
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
                className="w-full bg-background border border-border focus:border-brand rounded-2xl pl-12 pr-4 py-3.5 text-sm text-text-primary focus:ring-1 focus:ring-brand outline-none transition-all duration-200"
                placeholder="you@company.com"
              />
            </div>
          </div>

          <div>
            <div className="flex justify-between items-center mb-2">
              <label className="text-xs font-bold uppercase tracking-wider text-text-muted block">
                Password
              </label>
              <Link to="/forgot-password" className="text-xs font-semibold text-brand-light hover:underline">
                Forgot password?
              </Link>
            </div>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 pl-4 flex items-center text-text-muted">
                <Lock className="w-5 h-5" />
              </span>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-background border border-border focus:border-brand rounded-2xl pl-12 pr-4 py-3.5 text-sm text-text-primary focus:ring-1 focus:ring-brand outline-none transition-all duration-200"
                placeholder="••••••••"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-brand hover:bg-brand-dark disabled:opacity-50 text-text-primary font-bold py-3.5 rounded-2xl shadow-lg shadow-brand/20 transition-all duration-200 flex items-center justify-center gap-2 mt-2"
          >
            {loading ? (
              <span className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
            ) : (
              "Sign In to Workstation"
            )}
          </button>
        </form>

        {/* Redirect */}
        <p className="text-sm text-text-secondary mt-8">
          First time here?{' '}
          <Link to="/register" className="text-brand-light hover:underline font-semibold">
            Request an Account
          </Link>
        </p>
      </div>
    </div>
  )
}

export default Login
