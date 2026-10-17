export function money(cents: string | null | undefined, symbol = true): string {
  if (cents == null) return 'Unavailable';
  if (!/^-?\d+$/.test(cents)) return 'Unavailable';
  const n = BigInt(cents), abs = n < 0n ? -n : n;
  return `${n < 0n ? '−' : ''}${symbol ? '$' : ''}${(abs / 100n).toLocaleString('en-US')}.${String(abs % 100n).padStart(2, '0')}`;
}
export function toCents(dollars: string): string {
  if (!/^(0|[1-9]\d*)(\.\d{1,2})?$/.test(dollars.trim())) throw new Error('Enter a non-negative USD amount with up to two decimal places.');
  const [whole, fraction = ''] = dollars.trim().split('.');
  const n = BigInt(whole) * 100n + BigInt(fraction.padEnd(2, '0'));
  if (n > 9223372036854775807n) throw new Error('This amount exceeds the supported range.');
  return n.toString();
}
export function dollars(cents: string) { return money(cents, false).replaceAll(',', '').replace('−', '-'); }
export const policyName = (id: string) => id === 'cash_only' ? 'Cash only' : id === 'fixed_repo' ? 'Cash + overnight repo' : id;
export const humanize = (s: string) => s.toLowerCase().replaceAll('_', ' ').replace(/^./, c => c.toUpperCase());
export function download(name: string, content: string, type = 'application/json') { const url = URL.createObjectURL(new Blob([content], { type })); const a = document.createElement('a'); a.href = url; a.download = name; a.click(); setTimeout(() => URL.revokeObjectURL(url), 1000); }
