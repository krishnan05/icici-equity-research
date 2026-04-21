import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip,
         ReferenceLine, ResponsiveContainer, Cell } from 'recharts';

export default function ValuationChart({ data, currentPrice }) {
  if (!data) return <div className="loading">⏳ Computing valuation...</div>;

  const targets  = data.targets || [];
  const chartData = targets.map(t => ({
    name:     t.index || t.Scenario,
    DCF:      t['DCF (₹)'],
    EVEBITDA: t['EV/EBITDA (₹)'],
    PE:       t['P/E (₹)'],
    Weighted: t['Weighted (₹)'],
    upside:   t['Upside (%)'],
    rating:   t['Rating'],
  }));

  const ratingColor = r =>
    r?.includes('BUY')  ? '#10b981' :
    r?.includes('HOLD') ? '#f59e0b' : '#ef4444';

  const ratingBadge = r =>
    r?.includes('BUY')  ? 'badge-buy'  :
    r?.includes('HOLD') ? 'badge-hold' : 'badge-sell';

  return (
    <div>
      <div style={{ fontSize:11, color:'#4b5563', marginBottom:16 }}>
        Ke = {data.ke}% (CAPM) · Weights: DCF 35% · EV/EBITDA 40% · P/E 25%
      </div>

      {/* Rating cards */}
      <div className="grid-3" style={{ marginBottom:16 }}>
        {chartData.map((d, i) => (
          <div key={i} className="card" style={{ textAlign:'center' }}>
            <div style={{ fontSize:18, marginBottom:8 }}>{d.name?.split(' ')[0]}</div>
            <div style={{ fontSize:26, fontWeight:800,
                          color: ratingColor(d.rating) }}>
              ₹{d.Weighted?.toLocaleString('en-IN')}
            </div>
            <div style={{ fontSize:11, color:'#6b7280', margin:'4px 0 8px' }}>
              Weighted Target
            </div>
            <span className={`badge ${ratingBadge(d.rating)}`}>{d.rating}</span>
            <div style={{ fontSize:12, marginTop:8,
              color: d.upside > 0 ? '#10b981' : '#ef4444' }}>
              {d.upside > 0 ? '+' : ''}{d.upside}% vs CMP
            </div>
          </div>
        ))}
      </div>

      {/* Bar chart */}
      <div className="card">
        <div className="card-title">Price Target Breakdown (₹)</div>
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={chartData} margin={{ top:10, right:20, bottom:10, left:10 }}>
            <XAxis dataKey="name" tick={{ fill:'#6b7280', fontSize:12 }} />
            <YAxis tick={{ fill:'#6b7280', fontSize:11 }}
                   tickFormatter={v => `₹${v.toLocaleString('en-IN')}`} />
            <Tooltip
              contentStyle={{ background:'#1f2937', border:'1px solid #374151',
                              borderRadius:8, fontSize:12 }}
              formatter={(v, n) => [`₹${v?.toLocaleString('en-IN')}`, n]} />
            {currentPrice && (
              <ReferenceLine y={currentPrice} stroke="#f59e0b"
                             strokeDasharray="4 4"
                             label={{ value:`CMP ₹${currentPrice?.toLocaleString('en-IN')}`,
                                      fill:'#f59e0b', fontSize:11 }} />
            )}
            <Bar dataKey="DCF"      fill="#6366f1" radius={[4,4,0,0]} />
            <Bar dataKey="EVEBITDA" fill="#3b82f6" radius={[4,4,0,0]} />
            <Bar dataKey="PE"       fill="#8b5cf6" radius={[4,4,0,0]} />
            <Bar dataKey="Weighted" radius={[4,4,0,0]}>
              {chartData.map((d, i) => (
                <Cell key={i} fill={ratingColor(d.rating)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
        <div style={{ display:'flex', gap:16, marginTop:12,
                      justifyContent:'center', fontSize:11, color:'#6b7280' }}>
          {[['#6366f1','DCF'],['#3b82f6','EV/EBITDA'],
            ['#8b5cf6','P/E'],['#10b981','Weighted']].map(([c,l]) => (
            <span key={l} style={{ display:'flex', alignItems:'center', gap:4 }}>
              <span style={{ width:10, height:10, borderRadius:2,
                             background:c, display:'inline-block' }} />
              {l}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}