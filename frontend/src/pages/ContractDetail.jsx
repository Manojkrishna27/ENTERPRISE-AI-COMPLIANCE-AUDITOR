import React, { useState, useEffect, useRef } from 'react'
import { useParams, Link } from 'react-router-dom'
import { 
  ArrowLeft, 
  Play, 
  FileSpreadsheet, 
  MessageSquare, 
  ShieldAlert, 
  BookOpen, 
  History,
  Send,
  AlertTriangle
} from 'lucide-react'
import api from '../services/api'
import Sidebar from '../components/Sidebar'
import Navbar from '../components/Navbar'

const ContractDetail = () => {
  const { id } = useParams()
  const [contract, setContract] = useState(null)
  const [selectedVersion, setSelectedVersion] = useState(null)
  const [chunks, setChunks] = useState([])
  const [findings, setFindings] = useState([])
  const [loading, setLoading] = useState(true)
  const [analyzing, setAnalyzing] = useState(false)
  const [generatingReport, setGeneratingReport] = useState(false)
  
  // Tabs State
  const [activeTab, setActiveTab] = useState('findings') // findings, copilot, diff
  
  // Highlight / Citation State
  const [activeFinding, setActiveFinding] = useState(null)
  const contractRefs = useRef({})
  
  // Copilot Chat State
  const [chatQuery, setChatQuery] = useState('')
  const [chatMessages, setChatMessages] = useState([])
  const [chatLoading, setChatLoading] = useState(false)

  // Version Comparison State
  const [compareVersionId, setCompareVersionId] = useState('')
  const [diffChunks, setDiffChunks] = useState([])
  const [diffLoading, setDiffLoading] = useState(false)

  const fetchContractDetails = async () => {
    try {
      const res = await api.get(`/contracts/${id}`)
      setContract(res.data)
      if (res.data.versions && res.data.versions.length > 0) {
        // Default to latest version
        const latest = res.data.versions[0]
        setSelectedVersion(latest)
        await fetchVersionChunks(latest.id)
        await fetchVersionFindings(latest.id)
      }
    } catch (err) {
      console.error('Error fetching details:', err)
    }
  }

  const fetchVersionChunks = async (verId) => {
    try {
      const res = await api.get(`/contracts/${id}/versions/${verId}`)
      setChunks(res.data.chunks || [])
    } catch (err) {
      console.error('Error fetching version chunks:', err)
    }
  }

  const fetchVersionFindings = async (verId) => {
    try {
      const res = await api.get(`/analysis/contracts/${id}/version/${verId}/findings`)
      setFindings(res.data)
    } catch (err) {
      console.error('Error fetching findings:', err)
    }
  }

  useEffect(() => {
    const init = async () => {
      setLoading(true)
      await fetchContractDetails()
      setLoading(false)
    }
    init()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id])

  const handleVersionChange = async (verId) => {
    const ver = contract.versions.find((v) => v.id === verId)
    setSelectedVersion(ver)
    setActiveFinding(null)
    setDiffChunks([])
    await fetchVersionChunks(verId)
    await fetchVersionFindings(verId)
  }

  const handleRunAnalysis = async () => {
    if (!selectedVersion) return
    setAnalyzing(true)
    try {
      await api.post(`/analysis/contracts/${id}/version/${selectedVersion.id}/analyze`)
      await fetchVersionFindings(selectedVersion.id)
      // Refetch contract details to update status
      const res = await api.get(`/contracts/${id}`)
      setContract(res.data)
      const updatedVer = res.data.versions.find((v) => v.id === selectedVersion.id)
      setSelectedVersion(updatedVer)
    } catch (err) {
      const backendErr = err.response?.data?.error;
      alert('Analysis failed: ' + (backendErr ? backendErr : (err.response?.data?.msg || err.message)))
    } finally {
      setAnalyzing(false)
    }
  }

  const handleGenerateReport = async () => {
    if (!selectedVersion) return
    setGeneratingReport(true)
    try {
      const res = await api.post(`/reports/contracts/${id}/version/${selectedVersion.id}/generate`)
      const report = res.data.report
      const token = localStorage.getItem('access_token')
      // Trigger native browser download with query string JWT token
      window.open(`/api/reports/${report.id}/download?jwt=${token}`, '_blank')
    } catch (err) {
      alert('Report generation failed: ' + (err.response?.data?.msg || err.message))
    } finally {
      setGeneratingReport(false)
    }
  }

  // Scroll and highlight active paragraph
  const scrollToParagraph = (page, para, finding) => {
    setActiveFinding(finding)
    const refKey = `page-${page}-para-${para}`
    const element = contractRefs.current[refKey]
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
  }

  // Visual Diff loader
  const handleCompareSubmit = async (e) => {
    e.preventDefault()
    if (!compareVersionId || !selectedVersion) return
    
    setDiffLoading(true)
    try {
      // In a real-world scenario, we compute the visual diff of paragraphs.
      // For this SaaS workflow, we load chunks of the compare version and do parallel lines compare.
      const resBase = await api.get(`/contracts/${id}/versions/${selectedVersion.id}`)
      const resComp = await api.get(`/contracts/${id}/versions/${compareVersionId}`)
      
      const chunksBase = resBase.data.chunks || []
      const chunksComp = resComp.data.chunks || []
      
      // Perform simple diff (match by positions, mark edits)
      const diffResult = []
      const maxLen = Math.max(chunksBase.length, chunksComp.length)
      
      for (let i = 0; i < maxLen; i++) {
        const baseC = chunksBase[i]
        const compC = chunksComp[i]
        
        if (baseC && compC) {
          if (baseC.chunk_text === compC.chunk_text) {
            diffResult.push({ type: 'unchanged', text: baseC.chunk_text, page: baseC.page_number })
          } else {
            diffResult.push({ type: 'deleted', text: baseC.chunk_text, page: baseC.page_number })
            diffResult.push({ type: 'added', text: compC.chunk_text, page: compC.page_number })
          }
        } else if (baseC) {
          diffResult.push({ type: 'deleted', text: baseC.chunk_text, page: baseC.page_number })
        } else if (compC) {
          diffResult.push({ type: 'added', text: compC.chunk_text, page: compC.page_number })
        }
      }
      setDiffChunks(diffResult)
    } catch (err) {
      console.error('Diff error:', err)
    } finally {
      setDiffLoading(false)
    }
  }

  // Copilot message submit
  const handleSendMessage = async (e) => {
    e.preventDefault()
    if (!chatQuery.trim() || !selectedVersion) return

    const userMsg = { role: 'user', text: chatQuery }
    setChatMessages((prev) => [...prev, userMsg])
    setChatQuery('')
    setChatLoading(true)

    try {
      const res = await api.post(`/analysis/contracts/${id}/version/${selectedVersion.id}/copilot`, {
        question: chatQuery
      })
      const botMsg = { role: 'assistant', text: res.data.answer }
      setChatMessages((prev) => [...prev, botMsg])
    } catch (err) {
      const errorDetail = err.response?.data?.details || err.message || "Unknown error";
      const errMsg = { role: 'assistant', text: `Error fetching answer from AI backend: ${errorDetail}` }
      setChatMessages((prev) => [...prev, errMsg])
    } finally {
      setChatLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="w-12 h-12 border-4 border-brand/30 border-t-brand rounded-full animate-spin"></div>
      </div>
    )
  }

  if (!contract) {
    return (
      <div className="flex bg-background min-h-screen text-text-primary">
        <Sidebar />
        <div className="flex-1 flex flex-col">
          <Navbar />
          <div className="p-8 text-center">Contract not found</div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex bg-background min-h-screen text-text-primary">
      <Sidebar />
      
      <div className="flex-1 flex flex-col min-w-0">
        <Navbar />
        
        {/* Top Control Bar */}
        <div className="bg-card/40 border-b border-border py-4 px-8 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <Link to="/contracts" className="p-2 bg-slate-700/30 text-text-secondary hover:text-text-primary hover:bg-slate-700/60 rounded-xl transition-all duration-200">
              <ArrowLeft className="w-4 h-4" />
            </Link>
            <div>
              <h1 className="text-md font-bold text-text-primary">{contract.name}</h1>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-[10px] text-text-muted">Status:</span>
                <span className="text-[10px] bg-brand/10 text-brand-light font-bold px-2 py-0.5 rounded-full">{selectedVersion?.status}</span>
              </div>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            {/* Version Select */}
            <select
              value={selectedVersion?.id || ''}
              onChange={(e) => handleVersionChange(e.target.value)}
              className="bg-background border border-border rounded-xl px-3 py-2 text-xs font-semibold outline-none cursor-pointer"
            >
              {contract.versions?.map((v) => (
                <option key={v.id} value={v.id}>Version {v.version_number} ({v.file_type})</option>
              ))}
            </select>

            {/* Run Analysis */}
            <button
              onClick={handleRunAnalysis}
              disabled={analyzing}
              className="bg-brand hover:bg-brand-dark disabled:opacity-50 px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-2 shadow-md shadow-brand/20 transition-all duration-200"
            >
              {analyzing ? (
                <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
              ) : (
                <Play className="w-4 h-4 fill-current" />
              )}
              <span>Run Audit</span>
            </button>

            {/* Generate PDF Report */}
            <button
              onClick={handleGenerateReport}
              disabled={generatingReport || findings.length === 0}
              className="bg-slate-700 hover:bg-slate-600 disabled:opacity-40 px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-2 transition-all duration-200"
            >
              {generatingReport ? (
                <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
              ) : (
                <FileSpreadsheet className="w-4 h-4" />
              )}
              <span>Audit PDF</span>
            </button>
          </div>
        </div>

        {/* Split Panel Workstation */}
        <div className="flex-1 flex overflow-hidden min-h-0">
          
          {/* LEFT PANEL: Contract Viewer */}
          <div className="w-1/2 border-r border-border overflow-y-auto p-8 bg-[#0B0F19]/40 space-y-8">
            <div className="flex items-center justify-between border-b border-border/60 pb-3">
              <span className="text-xs font-bold uppercase tracking-wider text-text-muted">Document Clauses</span>
              <span className="text-xs text-text-muted">Total Paragraphs: {chunks.length}</span>
            </div>

            {activeTab === 'diff' && diffChunks.length > 0 ? (
              // Visual Diff View
              <div className="space-y-4 font-mono text-xs leading-relaxed">
                {diffChunks.map((c, index) => (
                  <div 
                    key={index} 
                    className={`p-3 rounded-lg border ${
                      c.type === 'added' ? 'bg-emerald-500/10 border-emerald-500/25 text-emerald-400' :
                      c.type === 'deleted' ? 'bg-red-500/10 border-red-500/25 text-red-400 line-through' :
                      'bg-slate-700/5 border-transparent text-text-secondary'
                    }`}
                  >
                    <span className="text-[10px] text-text-muted block mb-1">
                      {c.type === 'added' ? '[+] Added' : c.type === 'deleted' ? '[-] Deleted' : 'Unchanged'}
                    </span>
                    {c.text}
                  </div>
                ))}
              </div>
            ) : (
              // Standard Document View
              <div className="space-y-6">
                {chunks.map((chunk) => {
                  const refKey = `page-${chunk.page_number}-para-${chunk.paragraph_number}`
                  const isHighlighted = activeFinding && 
                                        activeFinding.contract_page_number === chunk.page_number &&
                                        activeFinding.contract_paragraph_number === chunk.paragraph_number
                  
                  return (
                    <div
                      key={chunk.id}
                      ref={(el) => (contractRefs.current[refKey] = el)}
                      className={`p-4 rounded-2xl border transition-all duration-350 leading-relaxed ${
                        isHighlighted 
                          ? 'bg-brand/10 border-brand/50 shadow-md shadow-brand/10 text-text-primary ring-1 ring-brand/35' 
                          : 'bg-card/20 border-border/40 text-text-secondary'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-[10px] bg-slate-700/50 px-2 py-0.5 rounded text-text-muted font-bold">
                          Page {chunk.page_number} • Paragraph {chunk.paragraph_number}
                        </span>
                        {isHighlighted && (
                          <span className="text-[10px] text-brand-light font-bold uppercase tracking-wider animate-pulse">Matched Finding</span>
                        )}
                      </div>
                      <p className="text-sm font-medium">{chunk.chunk_text}</p>
                    </div>
                  )
                })}
              </div>
            )}
          </div>

          {/* RIGHT PANEL: Sidebar details (findings / chat / diff) */}
          <div className="w-1/2 flex flex-col bg-card/10 overflow-hidden min-w-0">
            
            {/* Right Panel Tabs */}
            <div className="flex border-b border-border bg-card/30">
              <button
                onClick={() => setActiveTab('findings')}
                className={`flex-1 py-3.5 text-xs font-bold uppercase tracking-wider border-b-2 flex items-center justify-center gap-2 transition-all duration-200 ${
                  activeTab === 'findings' 
                    ? 'border-brand text-brand-light bg-brand/5' 
                    : 'border-transparent text-text-secondary hover:text-text-primary'
                }`}
              >
                <ShieldAlert className="w-4 h-4" />
                <span>AI Compliance Audit</span>
              </button>
              <button
                onClick={() => setActiveTab('copilot')}
                className={`flex-1 py-3.5 text-xs font-bold uppercase tracking-wider border-b-2 flex items-center justify-center gap-2 transition-all duration-200 ${
                  activeTab === 'copilot' 
                    ? 'border-brand text-brand-light bg-brand/5' 
                    : 'border-transparent text-text-secondary hover:text-text-primary'
                }`}
              >
                <MessageSquare className="w-4 h-4" />
                <span>RAG Copilot Chat</span>
              </button>
              <button
                onClick={() => setActiveTab('diff')}
                className={`flex-1 py-3.5 text-xs font-bold uppercase tracking-wider border-b-2 flex items-center justify-center gap-2 transition-all duration-200 ${
                  activeTab === 'diff' 
                    ? 'border-brand text-brand-light bg-brand/5' 
                    : 'border-transparent text-text-secondary hover:text-text-primary'
                }`}
              >
                <History className="w-4 h-4" />
                <span>Version Diff</span>
              </button>
            </div>

            {/* Tab content area */}
            <div className="flex-1 overflow-y-auto p-6 min-h-0">
              
              {/* TAB 1: AI FINDINGS */}
              {activeTab === 'findings' && (
                <div className="space-y-6">
                  <div className="flex justify-between items-center pb-2 border-b border-border/40">
                    <span className="text-xs font-bold uppercase tracking-wider text-text-muted">Risks Identified</span>
                    <span className="text-xs text-text-muted">{findings.length} Anomalies</span>
                  </div>

                  {findings.length === 0 ? (
                    <div className="p-8 text-center border border-border/40 rounded-2xl bg-card/25 mt-4">
                      <p className="text-sm text-text-secondary">No AI findings registered.</p>
                      <p className="text-xs text-text-muted mt-1.5">Click 'Run Audit' above to trigger automated RAG analysis.</p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {findings.map((f) => {
                        const isSelected = activeFinding?.id === f.id
                        return (
                          <div
                            key={f.id}
                            onClick={() => scrollToParagraph(f.contract_page_number, f.contract_paragraph_number, f)}
                            className={`p-5 rounded-2xl border text-left cursor-pointer transition-all duration-200 hover:-translate-y-0.5 hover:border-brand/40 ${
                              isSelected 
                                ? 'bg-card border-brand/50 shadow-lg' 
                                : 'bg-card/40 border-border/60'
                            }`}
                          >
                            <div className="flex items-center justify-between mb-3">
                              <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold border ${
                                f.risk_level === 'High' ? 'bg-risk-high/15 border-risk-high/30 text-risk-high' :
                                f.risk_level === 'Medium' ? 'bg-risk-medium/15 border-risk-medium/30 text-risk-medium' :
                                'bg-risk-low/15 border-risk-low/30 text-risk-low'
                              }`}>
                                {f.risk_level} Risk
                              </span>
                              <span className="text-[10px] text-text-muted font-semibold">
                                Conf: {intToPercent(f.confidence_score)}%
                              </span>
                            </div>

                            <h4 className="text-sm font-bold text-text-primary mb-2">{f.title}</h4>
                            <p className="text-xs text-text-secondary leading-relaxed mb-3">{f.explanation}</p>

                            {/* Side-by-Side Matching Evidence Drawer */}
                            {isSelected && (
                              <div className="space-y-3 mt-4 pt-4 border-t border-border/80 text-xs animate-in slide-in-from-top-2 duration-200">
                                {f.business_impact && (
                                  <div>
                                    <span className="text-[10px] text-text-muted font-bold uppercase tracking-wider block">Business Impact</span>
                                    <p className="text-text-secondary mt-1">{f.business_impact}</p>
                                  </div>
                                )}
                                {f.recommendation && (
                                  <div>
                                    <span className="text-[10px] text-brand-light font-bold uppercase tracking-wider block">Remediation Action</span>
                                    <p className="text-text-secondary mt-1">{f.recommendation}</p>
                                  </div>
                                )}
                                {f.policy_name && (
                                  <div className="bg-slate-900/50 p-3.5 rounded-xl border border-border/80 mt-2">
                                    <div className="flex items-center gap-2 text-[10px] text-brand-light font-bold uppercase tracking-wider mb-1.5">
                                      <BookOpen className="w-3.5 h-3.5" />
                                      <span>Cited Policy: '{f.policy_name}' (P{f.policy_page_number}, Para {f.policy_paragraph_number})</span>
                                    </div>
                                    <p className="text-[11px] text-text-muted italic leading-relaxed">
                                      "{f.matching_policy_text || "Refer to Policy Document standards guidelines."}"
                                    </p>
                                  </div>
                                )}
                              </div>
                            )}
                          </div>
                        )
                      })}
                    </div>
                  )}
                </div>
              )}

              {/* TAB 2: COPILOT CHAT */}
              {activeTab === 'copilot' && (
                <div className="h-full flex flex-col min-h-0">
                  <div className="flex-1 overflow-y-auto space-y-4 pb-4 max-h-[420px]">
                    {chatMessages.length === 0 ? (
                      <div className="text-center py-10 border border-border/40 rounded-2xl bg-card/20 mt-4">
                        <MessageSquare className="w-10 h-10 text-text-muted mx-auto mb-2" />
                        <h4 className="text-sm font-bold">Ask Contract Copilot</h4>
                        <p className="text-xs text-text-muted mt-1 leading-relaxed max-w-xs mx-auto">
                          Query payment terms, liability caps, or GDPR guidelines. Precise page and paragraph citations will be attached.
                        </p>
                      </div>
                    ) : (
                      chatMessages.map((msg, index) => (
                        <div 
                          key={index} 
                          className={`p-4 rounded-2xl max-w-[85%] text-xs leading-relaxed ${
                            msg.role === 'user' 
                              ? 'bg-brand text-text-primary self-end ml-auto' 
                              : 'bg-card border border-border text-text-secondary self-start'
                          }`}
                        >
                          <span className="text-[10px] text-text-muted font-bold block mb-1">
                            {msg.role === 'user' ? 'You' : 'Copilot AI'}
                          </span>
                          <div className="whitespace-pre-line font-medium">{msg.text}</div>
                        </div>
                      ))
                    )}
                    {chatLoading && (
                      <div className="bg-card border border-border p-4 rounded-2xl self-start w-24 flex items-center justify-center">
                        <span className="w-4 h-4 border-2 border-brand/30 border-t-brand rounded-full animate-spin"></span>
                      </div>
                    )}
                  </div>

                  {/* Chat Input */}
                  <form onSubmit={handleSendMessage} className="flex gap-2 mt-4 pt-4 border-t border-border/60">
                    <input
                      type="text"
                      value={chatQuery}
                      onChange={(e) => setChatQuery(e.target.value)}
                      className="flex-1 bg-background border border-border focus:border-brand rounded-xl px-4 py-2.5 text-xs text-text-primary outline-none"
                      placeholder="Ask copilot about the contract terms..."
                    />
                    <button 
                      type="submit"
                      disabled={chatLoading}
                      className="p-3 bg-brand hover:bg-brand-dark rounded-xl text-text-primary flex items-center justify-center shadow-lg shadow-brand/20 transition-all duration-200"
                    >
                      <Send className="w-4 h-4" />
                    </button>
                  </form>
                </div>
              )}

              {/* TAB 3: VERSION DIFF */}
              {activeTab === 'diff' && (
                <div className="space-y-6">
                  <div className="pb-2 border-b border-border/40">
                    <span className="text-xs font-bold uppercase tracking-wider text-text-muted">Compare Versions</span>
                  </div>

                  <form onSubmit={handleCompareSubmit} className="bg-card/40 p-4 border border-border/60 rounded-2xl space-y-4">
                    <div>
                      <label className="text-[10px] font-bold uppercase tracking-wider text-text-muted mb-2 block">
                        Base Version
                      </label>
                      <div className="bg-background border border-border rounded-xl px-4 py-2 text-xs text-text-secondary font-semibold">
                        Version {selectedVersion?.version_number} (Current)
                      </div>
                    </div>

                    <div>
                      <label className="text-[10px] font-bold uppercase tracking-wider text-text-muted mb-2 block">
                        Compare with Version
                      </label>
                      <select
                        value={compareVersionId}
                        onChange={(e) => setCompareVersionId(e.target.value)}
                        required
                        className="w-full bg-background border border-border rounded-xl px-4 py-2.5 text-xs text-text-secondary font-semibold outline-none cursor-pointer"
                      >
                        <option value="">Select version...</option>
                        {contract.versions
                          ?.filter((v) => v.id !== selectedVersion?.id)
                          ?.map((v) => (
                            <option key={v.id} value={v.id}>Version {v.version_number}</option>
                          ))}
                      </select>
                    </div>

                    <button
                      type="submit"
                      disabled={diffLoading || !compareVersionId}
                      className="w-full bg-brand hover:bg-brand-dark text-text-primary text-xs font-bold py-2.5 rounded-xl shadow-lg shadow-brand/20 transition-all duration-200"
                    >
                      {diffLoading ? "Generating Diff..." : "Generate Side-by-Side Diff"}
                    </button>
                  </form>

                  {/* Diff Summary */}
                  {diffChunks.length > 0 && (
                    <div className="bg-slate-900/50 p-4 border border-border rounded-2xl">
                      <span className="text-[10px] text-text-muted font-bold uppercase tracking-wider block mb-3">Risk Delta Estimator</span>
                      <div className="space-y-2 text-xs font-medium text-text-secondary">
                        <p className="flex justify-between items-center">
                          <span>Added Clauses:</span>
                          <span className="text-emerald-400 font-bold">{diffChunks.filter(c => c.type === 'added').length}</span>
                        </p>
                        <p className="flex justify-between items-center">
                          <span>Deleted Clauses:</span>
                          <span className="text-red-400 font-bold">{diffChunks.filter(c => c.type === 'deleted').length}</span>
                        </p>
                        <div className="bg-amber-500/10 border border-amber-500/20 text-[11px] text-amber-400 p-3 rounded-xl flex gap-2.5 mt-4">
                          <AlertTriangle className="w-5 h-5 shrink-0" />
                          <p className="leading-relaxed">Re-run compliance auditing on the new base version to evaluate new risk profiles.</p>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}

            </div>
          </div>

        </div>

      </div>
    </div>
  )
}

// Helpers
const intToPercent = (val) => {
  if (!val) return 100
  if (val <= 1.0) return Math.round(val * 100)
  return val
}

export default ContractDetail
