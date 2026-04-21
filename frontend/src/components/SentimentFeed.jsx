import React from 'react';

export default function SentimentFeed({ data }) {
  if (!data) return <div className="loading">⏳ Analysing sentiment...</div>;
  if (data.error) return <div className="loading">{data.error}</div>;

  const { summary, articles, adjusted_target, note, base_target } = data;

  const scoreColor = s =>
    s >= 0.05 ? '#10b981' : s <= -0.05 ? '#ef4444' : '#f59e0b';

  return (
    <div>
      {/* Summary card */}
      <div className="card" style={{ marginBottom:16,
           background:'linear-gradient(135deg,#1c1a0f,#111827)',
           borderColor:'#854d0e' }}>
        <div style={{ display:'flex', justifyContent:'space-between',
                      alignItems:'center', flexWrap:'wrap', gap:12 }}>
          <div>
            <div style={{ fontSize:11, color:'#6b7280', marginBottom:4 }}>
              FinBERT · ProsusAI/finbert · Financial domain NLP
            </div>
            <div style={{ fontSize:16, fontWeight:700,
                          color:'#f59e0b' }}>{summary?.signal}</div>
            <div style={{ fontSize:12, color:'#6b7280', marginTop:4 }}>{note}</div>
          </div>
          <div style={{ textAlign:'right' }}>
            <div style={{ fontSize:11, color:'#6b7280' }}>Sentiment-Adjusted Target</div>
            <div style={{ fontSize:28, fontWeight:800,
                          color:'#10b981' }}>
              ₹{adjusted_target?.toLocaleString('en-IN')}
            </div>
            <div style={{ fontSize:11, color:'#6b7280', marginTop:2 }}>
              Base ₹{base_target?.toLocaleString('en-IN')} · Score {summary?.avg_score > 0 ? '+' : ''}
              {summary?.avg_score?.toFixed(3)}
            </div>
          </div>
        </div>

        {/* Breakdown */}
        <div style={{ display:'flex', gap:16, marginTop:12,
                      fontSize:12 }}>
          <span className="positive">✓ {summary?.positive} Positive</span>
          <span style={{ color:'#4b5563' }}>·</span>
          <span className="negative">✗ {summary?.negative} Negative</span>
          <span style={{ color:'#4b5563' }}>·</span>
          <span className="neutral">– {summary?.neutral} Neutral</span>
        </div>

        {/* Bar */}
        <div style={{ height:5, background:'#1f2937',
                      borderRadius:3, overflow:'hidden', marginTop:8 }}>
          <div style={{
            height:'100%',
            width:`${(summary?.positive/summary?.total)*100}%`,
            background:'linear-gradient(90deg,#10b981,#059669)',
            borderRadius:3
          }} />
        </div>
      </div>

      {/* Articles */}
      <div className="card">
        <div className="card-title">Headlines ({articles?.length} scored)</div>
        <div style={{ display:'flex', flexDirection:'column', gap:8 }}>
          {articles?.map((a, i) => (
            <div key={i} style={{
              display:'flex', alignItems:'flex-start', gap:10,
              padding:'10px 12px', borderRadius:8, background:'#0f172a',
              borderLeft:`3px solid ${scoreColor(a.score)}`
            }}>
              <div style={{ flex:1, fontSize:13, color:'#e2e8f0',
                            lineHeight:1.4 }}>{a.title}</div>
              <div style={{ fontSize:12, fontWeight:700, flexShrink:0,
                            color: scoreColor(a.score) }}>
                {a.score > 0 ? '+' : ''}{a.score?.toFixed(3)}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}