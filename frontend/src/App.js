import React, { useState, useCallback } from 'react';
import axios from 'axios';
import LiveData        from './components/LiveData';
import ValuationChart  from './components/ValuationChart';
import ScenarioExplorer from './components/ScenarioExplorer';
import SentimentFeed   from './components/SentimentFeed';
import MLSignal        from './components/MLSignal';

const API = 'http://localhost:8000/api';

const TABS = [
  { id:'live',      label:'📊 Live Data'    },
  { id:'valuation', label:'🎯 Valuation'    },
  { id:'scenarios', label:'⚡ Scenarios'    },
  { id:'sentiment', label:'📰 Sentiment'    },
  { id:'ml',        label:'🤖 ML Signal'    },
];

const EXAMPLES = ['RELIANCE.NS','INFY.NS','HDFCBANK.NS','ZOMATO.NS'];

export default function App() {
  const [active,    setActive]    = useState('live');
  const [ticker,    setTicker]    = useState('RELIANCE.NS');
  const [input,     setInput]     = useState('');
  const [loading,   setLoading]   = useState(false);
  const [error,     setError]     = useState(null);

  const [financial, setFinancial] = useState(null);
  const [valuation, setValuation] = useState(null);
  const [scenarios, setScenarios] = useState(null);
  const [sentiment, setSentiment] = useState(null);
  const [ml,        setMl]        = useState(null);

  const analyse = useCallback(async (t) => {
    const tk = (t || input).trim().toUpperCase();
    if (!tk) return;
    const finalTicker = tk.endsWith('.NS') || tk.endsWith('.BO') ? tk : tk + '.NS';

    setLoading(true);
    setError(null);
    setTicker(finalTicker);
    setFinancial(null); setValuation(null);
    setScenarios(null); setSentiment(null); setMl(null);

    try {
      const [fin, val, scen, sent, mlData] = await Promise.all([
        axios.get(`${API}/financials/${finalTicker}`),
        axios.get(`${API}/valuation/${finalTicker}`),
        axios.get(`${API}/scenarios/${finalTicker}`),
        axios.get(`${API}/sentiment/${finalTicker}`),
        axios.get(`${API}/ml/${finalTicker}`),
      ]);
      setFinancial(fin.data);
      setValuation(val.data);
      setScenarios(scen.data);
      setSentiment(sent.data);
      setMl(mlData.data);
    } catch (e) {
      setError(`Failed to analyse ${finalTicker}. Check ticker and try again.`);
    } finally {
      setLoading(false);
    }
  }, [input]);

  const currentPrice = financial?.info?.current_price;

  return (
    <div style={{ minHeight:'100vh', background:'#0a0e1a' }}>
      {/* Header */}
      <div style={{ background:'#111827', borderBottom:'1px solid #1f2937',
                    padding:'14px 32px', display:'flex',
                    alignItems:'center', gap:16, flexWrap:'wrap' }}>
        <div>
          <div style={{ fontSize:18, fontWeight:800, color:'#f1f5f9' }}>
            FinSight
          </div>
          <div style={{ fontSize:11, color:'#4b5563' }}>
            AI-Powered Equity Research · Any NSE Listed Company
          </div>
        </div>

        {/* Ticker input */}
        <div style={{ display:'flex', gap:8, marginLeft:'auto',
                      alignItems:'center', flexWrap:'wrap' }}>
          <input
            className="ticker-input"
            value={input}
            onChange={e => setInput(e.target.value.toUpperCase())}
            onKeyDown={e => e.key === 'Enter' && analyse()}
            placeholder="e.g. INFY.NS"
          />
          <button className="analyse-btn" onClick={() => analyse()}
                  disabled={loading}>
            {loading ? 'Analysing...' : 'Analyse'}
          </button>
        </div>

        {/* Company name */}
        {financial?.info?.name && (
          <div style={{ fontSize:13, color:'#6b7280', width:'100%' }}>
            {financial.info.name} · {financial.info.sector}
            {financial.info.current_price && (
              <span style={{ color:'#10b981', marginLeft:12, fontWeight:600 }}>
                ₹{financial.info.current_price?.toLocaleString('en-IN')}
              </span>
            )}
          </div>
        )}
      </div>

      {/* Example tickers */}
      <div style={{ background:'#0f172a', padding:'8px 32px',
                    display:'flex', gap:8, alignItems:'center',
                    borderBottom:'1px solid #1f2937', flexWrap:'wrap' }}>
        <span style={{ fontSize:11, color:'#4b5563' }}>Try:</span>
        {EXAMPLES.map(ex => (
          <button key={ex} onClick={() => { setInput(ex); analyse(ex); }}
            style={{ background:'none', border:'1px solid #1f2937',
                     borderRadius:6, color:'#6b7280', cursor:'pointer',
                     fontSize:11, padding:'3px 10px',
                     transition:'all 0.15s' }}
            onMouseEnter={e => e.target.style.borderColor='#3b82f6'}
            onMouseLeave={e => e.target.style.borderColor='#1f2937'}>
            {ex}
          </button>
        ))}
      </div>

      {financial && (
  <a href={`http://localhost:8000/api/report/${ticker}`}
     target="_blank" rel="noreferrer"
     style={{ background:'#065f46', border:'none', borderRadius:8,
              color:'#10b981', cursor:'pointer', fontSize:14,
              fontWeight:600, padding:'10px 20px', textDecoration:'none',
              display:'inline-block' }}>
    ⬇ Download Report
  </a>
)}

      {/* Tabs */}
      <div style={{ background:'#111827', borderBottom:'1px solid #1f2937',
                    padding:'0 32px', display:'flex', gap:4 }}>
        {TABS.map(t => (
          <button key={t.id} onClick={() => setActive(t.id)}
            style={{
              padding:'12px 18px', border:'none', cursor:'pointer',
              background:'transparent', fontSize:13, fontWeight:500,
              color: active===t.id ? '#3b82f6' : '#6b7280',
              borderBottom: active===t.id
                ? '2px solid #3b82f6' : '2px solid transparent',
              transition:'all 0.15s',
            }}>
            {t.label}
          </button>
        ))}
      </div>

      {/* Content */}
      <div style={{ maxWidth:1200, margin:'0 auto', padding:'28px 32px' }}>
        {error && (
          <div style={{ background:'#450a0a', border:'1px solid #ef4444',
                        borderRadius:8, padding:'12px 16px', marginBottom:16,
                        color:'#ef4444', fontSize:13 }}>
            {error}
          </div>
        )}

        {loading && (
          <div className="loading" style={{ height:300 }}>
            ⏳ Fetching data, running models, analysing sentiment...
          </div>
        )}

       {!loading && !financial && !error && (
          <div style={{ display:'flex', flexDirection:'column',
                        alignItems:'center', justifyContent:'center',
                        height:400, gap:16, textAlign:'center' }}>
            <div style={{ fontSize:48 }}>📈</div>
            <div style={{ fontSize:22, fontWeight:700, color:'#f1f5f9' }}>
              Enter a company ticker to begin
            </div>
            <div style={{ fontSize:14, color:'#6b7280', maxWidth:420 }}>
              Type any NSE listed company ticker above and click Analyse.
              The platform fetches live data, runs financial projections,
              LSTM forecasting, and FinBERT sentiment analysis automatically.
            </div>
            <div style={{ display:'flex', gap:8, flexWrap:'wrap',
                          justifyContent:'center', marginTop:8 }}>
              {EXAMPLES.map(ex => (
                <button key={ex} onClick={() => { setInput(ex); analyse(ex); }}
                  style={{ background:'#1f2937', border:'1px solid #374151',
                           borderRadius:8, color:'#9ca3af', cursor:'pointer',
                           fontSize:13, padding:'8px 16px', fontWeight:500 }}
                  onMouseEnter={e => {
                    e.target.style.borderColor='#3b82f6';
                    e.target.style.color='#f1f5f9';
                  }}
                  onMouseLeave={e => {
                    e.target.style.borderColor='#374151';
                    e.target.style.color='#9ca3af';
                  }}>
                  {ex}
                </button>
              ))}
            </div>
          </div>
        )}

        {!loading && financial && (
          <>
            {active === 'live'      && <LiveData data={financial} />}
            {active === 'valuation' && <ValuationChart data={valuation}
                                          currentPrice={currentPrice} />}
            {active === 'scenarios' && <ScenarioExplorer data={scenarios}
                                          currentPrice={currentPrice} />}
            {active === 'sentiment' && <SentimentFeed data={sentiment} />}
            {active === 'ml'        && <MLSignal data={ml} />}
          </>
        )}
      </div>
    </div>
  );
}