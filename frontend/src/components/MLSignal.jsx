import React from 'react';

export default function MLSignal({ data }) {
  if (!data) return <div className="loading">⏳ Running ML models...</div>;

  const { lstm, ensemble } = data;

  const scoreColor = s =>
    s >= 0.1  ? '#10b981' :
    s <= -0.1 ? '#ef4444' : '#f59e0b';

  const barLen   = 30;
  const zeroPos  = barLen / 2;
  const scorePos = Math.round(zeroPos + (ensemble?.ensemble_score || 0) * zeroPos);
  const clamped  = Math.max(0, Math.min(barLen - 1, scorePos));
  const bar      = Array(barLen).fill('─');
  bar[Math.floor(zeroPos)] = '│';
  bar[clamped] = '●';

  return (
    <div>
      {/* LSTM */}
      <div className="card" style={{ marginBottom:16 }}>
        <div className="card-title">LSTM Financial Forecast</div>
        {lstm ? (
          <>
            <div style={{ fontSize:11, color:'#6b7280', marginBottom:12 }}>
              2-layer LSTM · Hidden 64 · Monte Carlo Dropout (100 passes) · MAE ₹{lstm.mae?.toLocaleString('en-IN')} cr
            </div>
            <table>
              <thead>
                <tr>
                  {['Quarter','Forecast PAT','Lower (–1σ)','Upper (+1σ)'].map(h => (
                    <th key={h} style={{ textAlign: h==='Quarter'?'left':'right' }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {lstm.quarters?.map((q, i) => (
                  <tr key={i}>
                    <td style={{ color:'#9ca3af' }}>{q}</td>
                    <td style={{ textAlign:'right', color:'#10b981', fontWeight:600 }}>
                      ₹{lstm.forecast?.[i]?.toLocaleString('en-IN')} cr
                    </td>
                    <td style={{ textAlign:'right', color:'#6b7280' }}>
                      ₹{lstm.lower?.[i]?.toLocaleString('en-IN')} cr
                    </td>
                    <td style={{ textAlign:'right', color:'#6b7280' }}>
                      ₹{lstm.upper?.[i]?.toLocaleString('en-IN')} cr
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            <div style={{ marginTop:12, fontSize:13, color:'#9ca3af' }}>
              Annual PAT FY2026E:
              <span style={{ color:'#10b981', fontWeight:700, marginLeft:8 }}>
                ₹{lstm.annual_pat?.toLocaleString('en-IN')} cr
              </span>
            </div>
          </>
        ) : (
          <div style={{ color:'#6b7280', fontSize:13 }}>
            LSTM skipped — insufficient quarterly data for this ticker.
            Model requires minimum 6 quarters of financial history.
          </div>
        )}
      </div>

      {/* Ensemble */}
      {ensemble && (
        <div className="card">
          <div className="card-title">Ensemble Signal</div>
          <div style={{ fontSize:11, color:'#6b7280', marginBottom:16 }}>
            Weighted combination of 3 independent signals
          </div>

          {/* Signal breakdown */}
          <table style={{ marginBottom:16 }}>
            <thead>
              <tr>
                {['Signal','Score','Weight','Contribution','Basis'].map(h => (
                  <th key={h} style={{ textAlign: h==='Signal'||h==='Basis'?'left':'right' }}>
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {[
                ['Fundamental (DCF)', ensemble.val_score,  0.50, 'Base case target vs CMP'],
                ['LSTM Forecast',     ensemble.lstm_score, 0.25, 'ML PAT vs manual projection'],
                ['FinBERT Sentiment', ensemble.sent_score, 0.25, 'News flow score'],
              ].map(([name, score, weight, basis], i) => {
                const contrib = (score * weight).toFixed(3);
                const color   = scoreColor(score);
                return (
                  <tr key={i}>
                    <td style={{ color:'#9ca3af' }}>{name}</td>
                    <td style={{ textAlign:'right', color, fontWeight:600 }}>
                      {score > 0 ? '+' : ''}{score?.toFixed(3)}
                    </td>
                    <td style={{ textAlign:'right', color:'#6b7280' }}>
                      {(weight*100).toFixed(0)}%
                    </td>
                    <td style={{ textAlign:'right',
                                 color: scoreColor(parseFloat(contrib)) }}>
                      {parseFloat(contrib) > 0 ? '+' : ''}{contrib}
                    </td>
                    <td style={{ color:'#6b7280', fontSize:11 }}>{basis}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>

          {/* Score bar */}
          <div style={{ fontFamily:'monospace', fontSize:13,
                        color:'#6b7280', marginBottom:8 }}>
            Bearish [{bar.join('')}] Bullish
          </div>

          {/* Final verdict */}
          <div style={{ display:'flex', alignItems:'center', gap:16,
                        padding:'16px', borderRadius:8, background:'#0f172a',
                        marginTop:8 }}>
            <div>
              <div style={{ fontSize:11, color:'#6b7280' }}>Ensemble Score</div>
              <div style={{ fontSize:24, fontWeight:800,
                            color: scoreColor(ensemble.ensemble_score) }}>
                {ensemble.ensemble_score > 0 ? '+' : ''}
                {ensemble.ensemble_score?.toFixed(3)}
              </div>
            </div>
            <div style={{ width:1, height:40, background:'#1f2937' }} />
            <div>
              <div style={{ fontSize:11, color:'#6b7280' }}>Rating</div>
              <div style={{ fontSize:18, fontWeight:700,
                            color: scoreColor(ensemble.ensemble_score) }}>
                {ensemble.rating}
              </div>
            </div>
            <div style={{ width:1, height:40, background:'#1f2937' }} />
            <div>
              <div style={{ fontSize:11, color:'#6b7280' }}>Confidence</div>
              <div style={{ fontSize:16, fontWeight:600, color:'#9ca3af' }}>
                {ensemble.confidence}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}