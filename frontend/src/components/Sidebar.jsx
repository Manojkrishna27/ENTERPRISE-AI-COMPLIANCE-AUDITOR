import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { 
  LayoutDashboard, 
  FileText, 
  ShieldCheck, 
  FileSpreadsheet, 
  Search, 
  Settings 
} from 'lucide-react'

const Sidebar = () => {
  const location = useLocation()
  const user = JSON.parse(localStorage.getItem('user') || '{}')
  const isAdmin = user.role === 'Admin'
  
  const navItems = [
    { name: 'Dashboard', path: '/', icon: LayoutDashboard },
    { name: 'Contracts', path: '/contracts', icon: FileText },
    { name: 'Policy Library', path: '/policies', icon: ShieldCheck },
    { name: 'Compliance Search', path: '/search', icon: Search },
    { name: 'Audit Reports', path: '/reports', icon: FileSpreadsheet },
  ]

  if (isAdmin) {
    navItems.push({ name: 'Admin Console', path: '/admin', icon: Settings })
  }

  return (
    <aside className="w-64 bg-card border-r border-border min-h-screen flex flex-col transition-all duration-300">
      {/* Brand Header */}
      <div className="h-16 flex items-center px-6 border-b border-border bg-[#0B0F19]">
        <div className="flex items-center gap-3">
          <div className="bg-brand w-8 h-8 rounded-lg flex items-center justify-center text-text-primary font-bold shadow-lg shadow-brand/20">
            🛡️
          </div>
          <div>
            <h1 className="text-sm font-bold tracking-wider uppercase text-text-primary leading-none">LexGuard AI</h1>
            <span className="text-[10px] text-text-muted font-medium">Compliance Auditor</span>
          </div>
        </div>
      </div>

      {/* Navigation list */}
      <nav className="flex-1 py-6 px-4 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon
          const isActive = location.pathname === item.path
          
          return (
            <Link
              key={item.name}
              to={item.path}
              className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-250 group ${
                isActive 
                  ? 'bg-brand text-text-primary shadow-md shadow-brand/25' 
                  : 'text-text-secondary hover:bg-slate-700/50 hover:text-text-primary'
              }`}
            >
              <Icon className={`w-5 h-5 transition-transform duration-200 group-hover:scale-105 ${
                isActive ? 'text-text-primary' : 'text-text-muted group-hover:text-brand-light'
              }`} />
              <span>{item.name}</span>
            </Link>
          )
        })}
      </nav>
      
      {/* Footer Info */}
      <div className="p-4 border-t border-border bg-[#0B0F19]/40 text-center">
        <span className="text-[10px] text-text-muted">Enterprise SaaS v1.0.0</span>
      </div>
    </aside>
  )
}

export default Sidebar
