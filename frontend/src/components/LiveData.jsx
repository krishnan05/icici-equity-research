import React from 'react';

const Metric = ({ label, value, sub, color }) => (
  <div className="card" style={{ padding:'16px' }}>
    <div className="card-title" style={{ marginBottom:6 }}>{label}</div>
    <div style={{ fontSize:20, fontWeight:700,
                  color: color || '#f1f5f9' }}>{value ?? '—'}</div>
    {sub && <div style={{ fontSize:11, color:'#6b7280', marginTop:3 }}>{sub}</div>}
  </div>
);

export default function LiveData({ data }) {
  if (!data) return <div className="loading">⏳ Fetching live data...</div>;

  const { info, projections, ratios } = data;
  const price = info.current_price;
  const high  = info['52w_high'];
  const low   = info['52w_low'];
  const pctFromHigh = high ? (((price - high) / high) * 100).toFixed(1) : null;

  return (
    <div>
      {/* Price hero */}
      <div className="card" style={{ marginBottom:16, padding:'20px 24px',
           background:'linear-gradient(135deg,#1e3a5f,#111827)',
           borderColor:'#2563eb' }}>
        <div style={{ display:'flex', justifyContent:'space-between',
                      alignItems:'center', flexWrap:'wrap', gap:12 }}>
          <div>
            <div style={{ fontSize:13, color:'#6b7280' }}>{info.sector} · {info.industry}</div>
            <div style={{ fontSize:34, fontWeight:800, color:'#f1f5f9', marginTop:4 }}>
              ₹{price?.toLocaleString('en-IN')}
            </div>
            <div style={{ fontSize:12, color:'#6b7280', marginTop:4 }}>Current Market Price</div>
          </div>
          <div style={{ textAlign:'right' }}>
            <div style={{ fontSize:12, color:'#6b7280' }}>52-Week Range</div>
            <div style={{ fontSize:13, marginTop:4 }}>
              <span className="negative">₹{low?.toLocaleString('en-IN')}</span>
              <span style={{ color:'#4b5563', margin:'0 6px' }}>—</span>
              <span className="positive">₹{high?.toLocaleString('en-IN')}</span>
            </div>
            {pctFromHigh && (
              <div style={{ fontSize:11, color:'#6b7280', marginTop:4 }}>
                {pctFromHigh}% from 52w high
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Key metrics */}
      <div className="grid-4" style={{ marginBottom:16 }}>
        <Metric label="P/E Ratio"    value={info.pe_ratio?.toFixed(1)+'x'}   sub="Trailing" />
        <Metric label="EV/EBITDA"    value={info.ev_ebitda?.toFixed(1)+'x'}  sub="Enterprise value" />
        <Metric label="EPS (TTM)"    value={`₹${info.eps_ttm?.toFixed(1)}`}  color="#10b981" />
        <Metric label="ROE"          value={`${((info.roe||0)*100).toFixed(1)}%`}
                color={info.roe > 0.15 ? '#10b981' : '#f59e0b'} />
        <Metric label="Market Cap"   value={`₹${(info.market_cap_cr/100000)?.toFixed(1)}L cr`} />
        <Metric label="Net Debt"     value={`₹${info.net_debt_cr?.toLocaleString('en-IN')} cr`}
                color={info.net_debt_cr < 0 ? '#10b981' : '#f1f5f9'} />
        <Metric label="P/BV"         value={info.pb_ratio?.toFixed(2)+'x'} />
        <Metric label="Free CF"      value={`₹${info.free_cashflow?.toLocaleString('en-IN')} cr`}
                color="#10b981" />
      </div>

      {/* Projections */}
      <div className="card">
        <div className="card-title">3-Year Projections (₹ crore)</div>
        <table>
          <thead>
            <tr>
              {['Metric', ...(projections?.map(r => r.Year) || ['FY2025E','FY2026E','FY2027E'])].map((h, i) => (
                <th key={h} style={{ textAlign: i===0?'left':'right' }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {[
              ['Revenue (₹ cr)',   row => row.Revenue?.toLocaleString('en-IN'), null],
              ['EBITDA (₹ cr)',    row => row.EBITDA?.toLocaleString('en-IN'),  null],
              ['PAT (₹ cr)',       row => row.PAT?.toLocaleString('en-IN'),     null],
              ['FCF (₹ cr)',       row => row.FCF?.toLocaleString('en-IN'),     row => row.FCF > 0 ? '#10b981' : '#ef4444'],
              ['EPS (₹)',          row => `₹${row['EPS (₹)']?.toFixed(1)}`,    () => '#10b981'],
              ['EBITDA Margin',    row => `${row['EBITDA Margin']}%`,           null],
            ].map(([label, valueFn, colorFn]) => (
              <tr key={label}>
                <td style={{ color:'#9ca3af' }}>{label}</td>
                {projections?.map((row, i) => (
                  <td key={i} style={{ textAlign:'right',
                                       color: colorFn ? colorFn(row) : '#e2e8f0',
                                       fontWeight: label==='EPS (₹)' ? 600 : 400 }}>
                    {valueFn(row) ?? '—'}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Ratios */}
      <div className="card" style={{ marginTop:16 }}>
        <div className="card-title">Key Ratios</div>
        <table>
          <thead>
            <tr>
              {['Ratio', ...(ratios?.map(r => r.Year) || ['FY2025E','FY2026E','FY2027E'])].map((h, i) => (
                <th key={h} style={{ textAlign: i===0?'left':'right' }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {[
              ['EBITDA Margin', 'EBITDA Margin (%)', '%'],
              ['PAT Margin',    'PAT Margin (%)',    '%'],
              ['FCF Margin',    'FCF Margin (%)',    '%'],
              ['FCF/EBITDA',    'FCF/EBITDA (%)',    '%'],
              ['Net Debt/EBITDA','Net Debt/EBITDA',  'x'],
              ['EPS (₹)',       'EPS (₹)',           ''],
            ].map(([label, key, suffix]) => (
              <tr key={label}>
                <td style={{ color:'#9ca3af' }}>{label}</td>
                {ratios?.map((row, i) => (
                  <td key={i} style={{ textAlign:'right' }}>
                    {row[key] != null ? `${row[key]}${suffix}` : '—'}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}