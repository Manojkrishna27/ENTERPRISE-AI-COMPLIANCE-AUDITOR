import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { 
  Search as SearchIcon, 
  FileText, 
  ShieldCheck, 
  Database,
  ArrowRight,
  TrendingUp
} from 'lucide-react'
import api from '../services/api'
import Sidebar from '../components/Sidebar'
import Navbar from '../components/Navbar'

const Search = () => {
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState({
    contracts: [],
    policies: [],
    semantic_policy_matches: []
  })
  
  // Tab control
  const [activeSubTab, setActiveSubTab] = useState('semantic') // semantic, contracts, policies

  const handleSearchSubmit = async (e) => {
    e.preventDefault()
    if (!query.trim()) return

    setLoading(true)
    try {
      const res = await api.get(`/search?q=${encodeURIComponent(query)}`)
      setResults(res.data)
      // Pick active tab based on what returned
      if (res.data.semantic_policy_matches?.length > 0) {
        setActiveSubTab('semantic')
      } else if (res.data.contracts?.length > 0) {
        setActiveSubTab('contracts')
      } else {
        setActiveSubTab('policies')
      }
    } catch (err) {
      console.error('Search failed:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex bg-background min-h-screen text-text-primary">
      <Sidebar />
      
      <div className="flex-1 flex flex-col min-w-0">
        <Navbar />
        
        <main className="flex-1 overflow-y-auto p-8 space-y-6">
          {/* Header */}
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-text-primary">Compliance Hybrid Search</h1>
            <p className="text-sm text-text-secondary">Execute keyword searches or semantic vectors across all indexed agreements and guidelines</p>
          </div>

          {/* Search Box */}
          <form onSubmit={handleSearchSubmit} className="bg-card border border-border p-4 rounded-2xl flex items-center gap-4 max-w-2xl shadow-xl">
            <span className="text-text-muted">
              <SearchIcon className="w-5 h-5" />
            </span>
            <input
              type="text"
              required
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="flex-1 bg-transparent text-sm text-text-primary outline-none"
              placeholder="e.g. Find GDPR clauses regarding user data retention..."
            />
            <button
              type="submit"
              disabled={loading}
              className="bg-brand hover:bg-brand-dark px-5 py-2 rounded-xl text-xs font-bold transition-all duration-150"
            >
              {loading ? "Searching..." : "Execute Search"}
            </button>
          </form>

          {/* Results Area */}
          {(results.contracts.length > 0 || results.policies.length > 0 || results.semantic_policy_matches.length > 0) ? (
            <div className="space-y-6">
              
              {/* Tab headers */}
              <div className="flex border-b border-border gap-6 text-sm font-bold uppercase tracking-wider text-text-secondary pb-1">
                <button
                  onClick={() => setActiveSubTab('semantic')}
                  className={`pb-2 border-b-2 flex items-center gap-2 transition-all duration-150 ${
                    activeSubTab === 'semantic' ? 'border-brand text-brand-light' : 'border-transparent hover:text-text-primary'
                  }`}
                >
                  <Database className="w-4 h-4" />
                  <span>Semantic policy Matches ({results.semantic_policy_matches.length})</span>
                </button>
                <button
                  onClick={() => setActiveSubTab('contracts')}
                  className={`pb-2 border-b-2 flex items-center gap-2 transition-all duration-150 ${
                    activeSubTab === 'contracts' ? 'border-brand text-brand-light' : 'border-transparent hover:text-text-primary'
                  }`}
                >
                  <FileText className="w-4 h-4" />
                  <span>Contracts ({results.contracts.length})</span>
                </button>
                <button
                  onClick={() => setActiveSubTab('policies')}
                  className={`pb-2 border-b-2 flex items-center gap-2 transition-all duration-150 ${
                    activeSubTab === 'policies' ? 'border-brand text-brand-light' : 'border-transparent hover:text-text-primary'
                  }`}
                >
                  <ShieldCheck className="w-4 h-4" />
                  <span>Policies ({results.policies.length})</span>
                </button>
              </div>

              {/* TAB 1: SEMANTIC POLICY MATCHES */}
              {activeSubTab === 'semantic' && (
                <div className="space-y-4">
                  {results.semantic_policy_matches.length === 0 ? (
                    <p className="text-sm text-text-muted">No semantic vectors matched your query.</p>
                  ) : (
                    results.semantic_policy_matches.map((match, idx) => (
                      <div key={idx} className="bg-card border border-border p-5 rounded-2xl space-y-3">
                        <div className="flex items-center justify-between">
                          <span className="text-xs bg-brand/10 text-brand-light font-bold px-2.5 py-0.5 rounded-full border border-brand/20">
                            Category: {match.policy_category || 'Reference'}
                          </span>
                          <span className="text-xs text-emerald-400 font-bold flex items-center gap-1">
                            <TrendingUp className="w-4 h-4" />
                            Match Score: {Math.round(match.score * 100)}%
                          </span>
                        </div>
                        <h4 className="text-sm font-bold text-text-primary">Policy Document: '{match.policy_name}'</h4>
                        <p className="text-xs text-text-secondary leading-relaxed bg-[#0B0F19]/30 p-3.5 rounded-xl border border-border/40 font-medium">
                          "{match.text}"
                        </p>
                        <span className="text-[10px] text-text-muted block font-semibold">
                          Reference: Page {match.page_number}, Paragraph {match.paragraph_number}
                        </span>
                      </div>
                    ))
                  )}
                </div>
              )}

              {/* TAB 2: CONTRACT MATCHES */}
              {activeSubTab === 'contracts' && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {results.contracts.length === 0 ? (
                    <p className="text-sm text-text-muted">No contracts matched.</p>
                  ) : (
                    results.contracts.map((c) => (
                      <Link 
                        key={c.id} 
                        to={`/contracts/${c.id}`} 
                        className="bg-card border border-border p-5 rounded-2xl hover:border-brand/40 flex flex-col justify-between group transition-all duration-200"
                      >
                        <div className="flex items-center gap-3">
                          <div className="w-9 h-9 bg-brand/10 text-brand rounded-lg flex items-center justify-center">
                            <FileText className="w-5 h-5" />
                          </div>
                          <div>
                            <h4 className="text-xs font-bold text-text-primary group-hover:text-brand-light">{c.name}</h4>
                            <span className="text-[10px] text-text-muted block mt-1">Status: {c.status}</span>
                          </div>
                        </div>
                        <div className="flex items-center justify-between text-[11px] text-text-muted mt-6 font-semibold border-t border-border/50 pt-3">
                          <span>Owner: {c.owner_name || 'Legal Team'}</span>
                          <span className="flex items-center gap-1 text-brand-light">
                            Open Audit <ArrowRight className="w-3.5 h-3.5" />
                          </span>
                        </div>
                      </Link>
                    ))
                  )}
                </div>
              )}

              {/* TAB 3: POLICY MATCHES */}
              {activeSubTab === 'policies' && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {results.policies.length === 0 ? (
                    <p className="text-sm text-text-muted">No policies matched.</p>
                  ) : (
                    results.policies.map((p) => (
                      <div key={p.id} className="bg-card border border-border p-5 rounded-2xl flex flex-col justify-between">
                        <div className="flex items-center gap-3">
                          <div className="w-9 h-9 bg-emerald-500/10 text-emerald-400 rounded-lg flex items-center justify-center">
                            <ShieldCheck className="w-5 h-5" />
                          </div>
                          <div>
                            <h4 className="text-xs font-bold text-text-primary">{p.name}</h4>
                            <span className="text-[10px] text-text-muted block mt-1">Category: {p.category}</span>
                          </div>
                        </div>
                        <p className="text-xs text-text-secondary mt-3 leading-relaxed">{p.description || 'No description provided.'}</p>
                      </div>
                    ))
                  )}
                </div>
              )}

            </div>
          ) : (
            query.trim() && !loading && (
              <div className="text-center py-20 bg-card border border-border rounded-2xl">
                <p className="text-sm text-text-secondary">No results matched your search term.</p>
                <p className="text-xs text-text-muted mt-1">Try keywords like 'GDPR', 'liability', 'indemnity', or specific agreement names.</p>
              </div>
            )
          )}

        </main>
      </div>
    </div>
  )
}

export default Search
