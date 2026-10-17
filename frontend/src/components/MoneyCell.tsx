import React from 'react';
import { formatMoneyCents } from '../client/api';

interface MoneyCellProps {
  cents: string | null | undefined;
  showSignColor?: boolean;
  className?: string;
}

export const MoneyCell: React.FC<MoneyCellProps> = ({ cents, showSignColor = true, className = '' }) => {
  const formatted = formatMoneyCents(cents);
  const isNegative = (cents || '').startsWith('-');
  const isZero = cents === '0' || cents === '00';

  let colorStyle: React.CSSProperties = {
    fontVariantNumeric: 'tabular-nums',
    fontWeight: 500,
  };

  if (showSignColor) {
    if (isNegative) {
      colorStyle.color = 'var(--color-danger)';
    } else if (!isZero && cents) {
      colorStyle.color = 'var(--color-text)';
    } else {
      colorStyle.color = 'var(--color-text-muted)';
    }
  }

  return (
    <span className={`money-cell ${className}`} style={colorStyle} title={cents ? `${cents} cents` : 'Unavailable'}>
      {formatted}
    </span>
  );
};
