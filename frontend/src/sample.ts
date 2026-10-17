// Newly authored fictional sample. Not D07 and not observed bank data.
export function sampleCSV() {
  const columns = ['timestamp','deposits_usd','withdrawals_usd','net_flow_usd','repo_sweep_window_open','repo_sweep_mature','tier1_repo_rate_apy','tier2_bond_yield_pct','tier2_bond_price_index','tier2_bond_mod_duration','tier3_stock_index_price','tier3_stock_volatility_pct','tier1_early_redemption_haircut_pct','tier2_bond_liquidation_haircut_pct','tier3_stock_liquidation_haircut_pct','emergency_overdraft_penalty_apr_pct'];
  const rows = Array.from({ length: 168 }, (_, i) => {
    const hour = i % 24, day = Math.floor(i / 24);
    const deposits = hour >= 8 && hour <= 16 ? 18500 + (i % 5) * 1200 : 1000;
    const withdrawals = hour >= 9 && hour <= 17 ? 17000 + (i % 7) * 850 : 800;
    return [`2026-01-${String(day + 1).padStart(2,'0')} ${String(hour).padStart(2,'0')}:00:00`,deposits,withdrawals,deposits-withdrawals,hour===17?'True':'False',hour===8?'True':'False','4.0','3.5','100','4','5000','15','0.5','2','5','12'].join(',');
  });
  return [columns.join(','), ...rows].join('\r\n') + '\r\n';
}
