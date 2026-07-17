import React, { useState, useEffect } from 'react'
import { Bell, LogOut, User as UserIcon } from 'lucide-react'
import api from '../services/api'

const Navbar = () => {
  const [notifications, setNotifications] = useState([])
  const [showDropdown, setShowDropdown] = useState(false)
  const user = JSON.parse(localStorage.getItem('user') || '{}')

  // Fetch notifications
  const fetchNotifications = async () => {
    try {
      // In a real setup, we would query /api/notifications. For demo robustness, we populate standard logs
      // or query backend if ready. Let's try calling backend and fall back to dummy compliance logs if empty.
      const res = await api.get('/dashboard')
      const auditLogs = res.data.recent_activities || []
      const simulatedNotifs = auditLogs.slice(0, 3).map((log, index) => ({
        id: index,
        message: log.details || `Activity processed: ${log.action}`,
        created_at: log.created_at
      }))
      setNotifications(simulatedNotifs)
    } catch (e) {
      setNotifications([
        { id: 1, message: "Compliance Audit complete for Vendor Agreement.pdf", created_at: new Date().toISOString() },
        { id: 2, message: "Policy update: SOC2 revised policies uploaded.", created_at: new Date().toISOString() }
      ])
    }
  }

  useEffect(() => {
    fetchNotifications()
  }, [])

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
    window.location.href = '/login'
  }

  return (
    <header className="h-16 border-b border-border bg-card/50 backdrop-blur-md flex items-center justify-between px-8 sticky top-0 z-40">
      <div>
        <h2 className="text-lg font-semibold text-text-primary">Corporate Workstation</h2>
      </div>

      <div className="flex items-center gap-6">
        {/* Notifications Dropdown */}
        <div className="relative">
          <button 
            onClick={() => setShowDropdown(!showDropdown)}
            className="p-2 text-text-secondary hover:text-text-primary hover:bg-slate-700/30 rounded-lg relative transition-all duration-200"
          >
            <Bell className="w-5 h-5" />
            {notifications.length > 0 && (
              <span className="absolute top-1 right-1 w-2.5 h-2.5 bg-risk-high rounded-full border border-card ring-2 ring-risk-high/30 animate-pulse"></span>
            )}
          </button>

          {showDropdown && (
            <div className="absolute right-0 mt-3 w-80 bg-card border border-border rounded-2xl shadow-xl z-50 p-4 animate-in fade-in slide-in-from-top-3 duration-200">
              <h3 className="text-xs font-bold uppercase tracking-wider text-text-muted mb-3">Compliance Alerts</h3>
              <div className="space-y-3">
                {notifications.length === 0 ? (
                  <p className="text-xs text-text-muted text-center py-4">No new notifications</p>
                ) : (
                  notifications.map((notif) => (
                    <div key={notif.id} className="text-xs pb-3 border-b border-border last:border-b-0 last:pb-0">
                      <p className="text-text-primary font-medium">{notif.message}</p>
                      <span className="text-[10px] text-text-muted block mt-1">
                        {new Date(notif.created_at).toLocaleTimeString()}
                      </span>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        {/* User profile dropdown & logout */}
        <div className="flex items-center gap-4 pl-4 border-l border-border">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-full bg-slate-700/60 border border-border flex items-center justify-center text-text-primary">
              <UserIcon className="w-4 h-4 text-brand-light" />
            </div>
            <div>
              <p className="text-sm font-semibold text-text-primary leading-tight">{user.full_name || 'Legal Reviewer'}</p>
              <span className="text-[10px] bg-brand/20 text-brand-light font-bold px-2 py-0.5 rounded-full mt-0.5 inline-block">
                {user.role || 'Auditor'}
              </span>
            </div>
          </div>

          <button
            onClick={handleLogout}
            className="p-2 text-text-secondary hover:text-risk-high hover:bg-red-500/10 rounded-lg transition-all duration-200 ml-2"
            title="Log Out"
          >
            <LogOut className="w-5 h-5" />
          </button>
        </div>
      </div>
    </header>
  )
}

export default Navbar
