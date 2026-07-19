import React, { useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';

const Landing = () => {
  const navigate = useNavigate();

  useEffect(() => {
    // Redirect if already authenticated
    const token = localStorage.getItem('access_token');
    if (token) {
      navigate('/dashboard');
    }
  }, [navigate]);

  return (
    <div className="min-h-screen bg-background text-text-primary font-sans overflow-x-hidden selection:bg-brand selection:text-white">
      {/* Navigation */}
      <nav className="fixed top-0 w-full z-50 border-b border-border bg-background/80 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-2">
              <span className="text-xl">🛡️</span>
              <span className="font-bold text-lg tracking-wider uppercase text-text-primary">LexGuard AI</span>
            </div>
            <div className="hidden md:block">
              <div className="ml-10 flex items-baseline space-x-8">
                <a href="#features" className="text-text-secondary hover:text-text-primary transition-colors text-sm font-medium">Features</a>
                <a href="#workflow" className="text-text-secondary hover:text-text-primary transition-colors text-sm font-medium">Workflow</a>
                <a href="#architecture" className="text-text-secondary hover:text-text-primary transition-colors text-sm font-medium">Architecture</a>
              </div>
            </div>
            <div className="flex space-x-4">
              <a href="https://github.com" target="_blank" rel="noopener noreferrer" className="text-text-secondary hover:text-text-primary px-3 py-2 text-sm font-medium transition-colors">
                GitHub
              </a>
              <Link to="/login" className="bg-brand hover:bg-brand-dark text-white px-5 py-2 rounded-md text-sm font-medium transition-colors shadow-[0_0_15px_rgba(99,102,241,0.3)]">
                Login
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 sm:pt-40 sm:pb-24 lg:pb-32 relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-brand-dark/20 via-background to-background pointer-events-none"></div>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 text-center">
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight mb-6">
            Enterprise AI-powered <br className="hidden sm:block" />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-light to-brand">Compliance Platform</span>
          </h1>
          <p className="mt-4 text-xl text-text-secondary max-w-3xl mx-auto mb-10 font-light">
            Automate your contract auditing with Retrieval-Augmented Generation (RAG) and Semantic Search. Validate legal agreements against internal policies instantly.
          </p>
          <div className="flex justify-center space-x-4">
            <Link to="/login" className="bg-brand hover:bg-brand-dark text-white px-8 py-3 rounded-md text-base font-medium transition-colors shadow-[0_0_20px_rgba(99,102,241,0.4)]">
              Get Started
            </Link>
            <a href="#workflow" className="bg-card hover:bg-border border border-border text-text-primary px-8 py-3 rounded-md text-base font-medium transition-colors">
              View Workflow
            </a>
          </div>
        </div>
      </section>

      {/* Problem vs Solution */}
      <section className="py-20 bg-card/30 border-y border-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold">The Compliance Bottleneck</h2>
            <p className="mt-4 text-text-secondary max-w-2xl mx-auto">Traditional contract reviews are slow, expensive, and error-prone. Comparing dense legal text against GDPR, ISO 27001, or custom vendor guidelines manually doesn't scale.</p>
          </div>
          <div className="grid md:grid-cols-2 gap-8">
            <div className="bg-background border border-border rounded-xl p-8 relative overflow-hidden">
              <div className="absolute top-0 right-0 w-32 h-32 bg-risk-high/10 rounded-bl-full"></div>
              <h3 className="text-xl font-bold mb-4 flex items-center"><span className="text-risk-high mr-3">✕</span> Legacy Approach</h3>
              <ul className="space-y-4 text-text-secondary">
                <li className="flex items-start"><span className="text-risk-high mr-2 mt-1">•</span> Weeks of manual legal review cycles.</li>
                <li className="flex items-start"><span className="text-risk-high mr-2 mt-1">•</span> High risk of missing subtle liability clauses.</li>
                <li className="flex items-start"><span className="text-risk-high mr-2 mt-1">•</span> Inconsistent application of internal policies.</li>
              </ul>
            </div>
            <div className="bg-background border border-border rounded-xl p-8 relative overflow-hidden">
              <div className="absolute top-0 right-0 w-32 h-32 bg-brand/10 rounded-bl-full"></div>
              <h3 className="text-xl font-bold mb-4 flex items-center"><span className="text-brand mr-3">✓</span> LexGuard AI</h3>
              <ul className="space-y-4 text-text-secondary">
                <li className="flex items-start"><span className="text-brand mr-2 mt-1">•</span> Sub-second semantic analysis of hundreds of pages.</li>
                <li className="flex items-start"><span className="text-brand mr-2 mt-1">•</span> Automated highlighting of high-risk clauses.</li>
                <li className="flex items-start"><span className="text-brand mr-2 mt-1">•</span> Deterministic compliance scoring using RAG.</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Workflow Section */}
      <section id="workflow" className="py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold">Intelligent Audit Workflow</h2>
            <p className="mt-4 text-text-secondary max-w-2xl mx-auto">How our AI transforms a raw PDF into an actionable compliance report.</p>
          </div>
          
          <div className="flex flex-col md:flex-row items-center justify-between bg-card border border-border rounded-2xl p-8 md:p-12 relative overflow-hidden">
            <div className="z-10 flex flex-col items-center mb-8 md:mb-0">
              <div className="w-16 h-16 bg-background border border-border rounded-xl flex items-center justify-center text-2xl shadow-lg">📄</div>
              <span className="mt-4 text-sm font-medium text-text-secondary">Upload PDF</span>
            </div>
            
            <div className="hidden md:block w-full h-[1px] bg-gradient-to-r from-transparent via-border to-transparent relative mx-4">
              <div className="absolute top-1/2 left-1/2 transform -translate-y-1/2 -translate-x-1/2 bg-card px-2 text-text-muted text-xs">PyMuPDF / Chunking</div>
            </div>
            
            <div className="z-10 flex flex-col items-center mb-8 md:mb-0">
              <div className="w-16 h-16 bg-background border border-brand/50 rounded-xl flex items-center justify-center text-2xl shadow-[0_0_15px_rgba(99,102,241,0.2)]">🔍</div>
              <span className="mt-4 text-sm font-medium text-text-secondary">Qdrant Vector Search</span>
            </div>
            
            <div className="hidden md:block w-full h-[1px] bg-gradient-to-r from-transparent via-border to-transparent relative mx-4">
              <div className="absolute top-1/2 left-1/2 transform -translate-y-1/2 -translate-x-1/2 bg-card px-2 text-text-muted text-xs">Context Retrieval (RAG)</div>
            </div>

            <div className="z-10 flex flex-col items-center mb-8 md:mb-0">
              <div className="w-16 h-16 bg-background border border-border rounded-xl flex items-center justify-center text-2xl shadow-lg">🧠</div>
              <span className="mt-4 text-sm font-medium text-text-secondary">LLM Analysis</span>
            </div>

            <div className="hidden md:block w-full h-[1px] bg-gradient-to-r from-transparent via-border to-transparent relative mx-4">
              <div className="absolute top-1/2 left-1/2 transform -translate-y-1/2 -translate-x-1/2 bg-card px-2 text-text-muted text-xs">Risk Generation</div>
            </div>
            
            <div className="z-10 flex flex-col items-center">
              <div className="w-16 h-16 bg-brand text-white rounded-xl flex items-center justify-center text-2xl shadow-[0_0_20px_rgba(99,102,241,0.5)]">📊</div>
              <span className="mt-4 text-sm font-medium text-text-primary">Compliance Report</span>
            </div>
          </div>
        </div>
      </section>

      {/* Dashboard Preview */}
      <section className="py-12 bg-background">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
           <div className="rounded-2xl border border-border overflow-hidden bg-card shadow-2xl relative group">
              <div className="h-10 border-b border-border bg-background/50 flex items-center px-4 space-x-2">
                 <div className="w-3 h-3 rounded-full bg-risk-high"></div>
                 <div className="w-3 h-3 rounded-full bg-risk-medium"></div>
                 <div className="w-3 h-3 rounded-full bg-risk-low"></div>
              </div>
              <div className="aspect-[16/9] w-full bg-background relative overflow-hidden">
                <img 
                  src="https://images.unsplash.com/photo-1551288049-bebda4e38f71?q=80&w=2070&auto=format&fit=crop" 
                  alt="Enterprise Dashboard Interface" 
                  className="object-cover w-full h-full opacity-60 mix-blend-luminosity hover:mix-blend-normal transition-all duration-700 hover:opacity-100 cursor-pointer"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-background via-transparent to-transparent pointer-events-none"></div>
                <div className="absolute bottom-8 left-8">
                   <h3 className="text-2xl font-bold">Executive Dashboard</h3>
                   <p className="text-text-secondary mt-2">Real-time risk distribution across all corporate agreements.</p>
                </div>
              </div>
           </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-24 bg-card/30 border-y border-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold">Enterprise-Grade Features</h2>
            <p className="mt-4 text-text-secondary max-w-2xl mx-auto">Built for security, scale, and uncompromising accuracy.</p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-6">
            {[
              { title: 'Citation Highlighting', desc: 'Every AI claim is directly linked back to the exact paragraph in the source contract.' },
              { title: 'Role-Based Access', desc: 'Granular RBAC for Legal, Compliance, Procurement, and Executive teams.' },
              { title: 'Policy Library', desc: 'Centralized repository for corporate policies used as the ground-truth for RAG.' },
              { title: 'Audit Logs', desc: 'Immutable audit trails of every document upload, analysis, and download.' },
              { title: 'PDF Reporting', desc: 'Export beautifully formatted, executive-ready PDF compliance reports.' },
              { title: 'Semantic Search', desc: 'Search across thousands of contracts based on meaning, not just keywords.' },
            ].map((feature, idx) => (
              <div key={idx} className="bg-background border border-border rounded-xl p-6 hover:border-brand/50 transition-colors">
                <h3 className="text-lg font-bold mb-2 text-text-primary">{feature.title}</h3>
                <p className="text-text-secondary text-sm leading-relaxed">{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Architecture & Tech Stack */}
      <section id="architecture" className="py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <div>
              <h2 className="text-3xl font-bold mb-6">Robust Architecture</h2>
              <p className="text-text-secondary mb-8 leading-relaxed">
                Deployed using Docker containers for maximum portability across AWS, Azure, or on-premise environments. 
                Utilizing state-of-the-art vector databases for millisecond retrieval times and secure caching layers.
              </p>
              
              <div className="grid grid-cols-2 gap-4">
                {[
                  { name: 'React + Vite', type: 'Frontend' },
                  { name: 'Flask + Python', type: 'Backend API' },
                  { name: 'PostgreSQL', type: 'Relational DB' },
                  { name: 'Qdrant', type: 'Vector DB' },
                  { name: 'Redis', type: 'Caching/Tasks' },
                  { name: 'Docker', type: 'Infrastructure' },
                ].map((tech, idx) => (
                  <div key={idx} className="border border-border bg-card/50 rounded-lg p-4 flex flex-col">
                    <span className="text-xs text-brand font-semibold tracking-wider uppercase mb-1">{tech.type}</span>
                    <span className="font-medium text-text-primary">{tech.name}</span>
                  </div>
                ))}
              </div>
            </div>
            
            <div className="bg-card border border-border rounded-2xl p-8 relative">
                <div className="absolute top-0 right-0 w-64 h-64 bg-brand/5 rounded-full blur-3xl -z-10"></div>
                <h3 className="text-xl font-bold mb-6 border-b border-border pb-4">Data Flow</h3>
                
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 bg-background border border-border rounded-lg">
                    <span className="font-medium">Client</span>
                    <span className="text-xs text-text-muted">React SPA</span>
                  </div>
                  <div className="flex justify-center text-border">↓</div>
                  <div className="flex items-center justify-between p-4 bg-background border border-brand/30 shadow-[0_0_15px_rgba(99,102,241,0.1)] rounded-lg">
                    <span className="font-medium">Flask API Gateway</span>
                    <span className="text-xs text-brand">Auth & Logic</span>
                  </div>
                  <div className="flex justify-between px-8 text-border">
                    <span>↙</span>
                    <span>↓</span>
                    <span>↘</span>
                  </div>
                  <div className="grid grid-cols-3 gap-2">
                    <div className="p-3 bg-background border border-border rounded-lg text-center text-sm font-medium">Postgres</div>
                    <div className="p-3 bg-background border border-border rounded-lg text-center text-sm font-medium">Redis</div>
                    <div className="p-3 bg-background border border-border rounded-lg text-center text-sm font-medium">Qdrant</div>
                  </div>
                  <div className="flex justify-center text-border">↓</div>
                  <div className="flex items-center justify-between p-4 bg-card border border-border rounded-lg">
                    <span className="font-medium">LLM Provider</span>
                    <span className="text-xs text-text-muted">OpenAI</span>
                  </div>
                </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 bg-brand relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-white/10 to-transparent pointer-events-none"></div>
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative z-10">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">Ready to secure your compliance posture?</h2>
          <p className="text-brand-light text-lg mb-10 max-w-2xl mx-auto">
            Reduce manual review times by up to 80% while dramatically decreasing your organizational legal risk.
          </p>
          <div className="flex justify-center space-x-4">
            <Link to="/login" className="bg-white text-brand px-8 py-3 rounded-md text-base font-bold hover:bg-slate-50 transition-colors shadow-lg">
              Launch Application
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-background border-t border-border py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row justify-between items-center">
          <div className="flex items-center space-x-2 mb-4 md:mb-0">
            <span className="text-xl">🛡️</span>
            <span className="font-bold text-lg tracking-wider uppercase text-text-primary">LexGuard AI</span>
          </div>
          <div className="text-sm text-text-muted">
            Enterprise AI Compliance & Contract Auditor
          </div>
          <div className="flex space-x-6 mt-4 md:mt-0">
            <a href="#" className="text-text-muted hover:text-text-primary transition-colors">GitHub</a>
            <a href="#" className="text-text-muted hover:text-text-primary transition-colors">Documentation</a>
            <a href="#" className="text-text-muted hover:text-text-primary transition-colors">License</a>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Landing;
