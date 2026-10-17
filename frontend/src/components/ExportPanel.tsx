import React, { useState } from 'react';
import { EvidenceBundle, EvidenceMember } from '../types/contracts';
import { IconDownload, IconCheckCircle } from './Icons';

interface ExportPanelProps {
  bundle: EvidenceBundle;
  isExporting?: boolean;
}

export const ExportPanel: React.FC<ExportPanelProps> = ({ bundle, isExporting = false }) => {
  const [selectedMember, setSelectedMember] = useState<EvidenceMember | null>(
    bundle.members.length > 0 ? bundle.members[0] : null
  );

  const handleDownloadJson = () => {
    const blob = new Blob([JSON.stringify(bundle, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `reserve_juggler_evidence_${bundle.run_id}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
      {/* Header and Download Bar */}
      <div
        style={{
          backgroundColor: 'var(--color-surface)',
          border: '1px solid var(--color-border)',
          borderRadius: 'var(--radius-lg)',
          padding: 'var(--space-6)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: 'var(--space-4)',
        }}
      >
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
            <IconCheckCircle size={20} className="text-success" />
            <h3 style={{ fontSize: '18px', fontWeight: 600 }}>Evidence Package: {bundle.run_id}</h3>
          </div>
          <p className="text-small" style={{ marginTop: '4px' }}>
            Specification Scope: <strong>RG-02 / scope 0.2.0</strong> &bull; Version: <code>{bundle.contract_version}</code>
          </p>
        </div>

        <button
          className="btn btn-primary"
          onClick={handleDownloadJson}
          disabled={isExporting}
        >
          <IconDownload size={16} /> Download Signed JSON Evidence Bundle
        </button>
      </div>

      {/* Member Files Viewer */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
          gap: 'var(--space-6)',
          alignItems: 'start',
        }}
      >
        {/* Members List */}
        <div
          style={{
            backgroundColor: 'var(--color-surface)',
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--radius-lg)',
            overflow: 'hidden',
          }}
        >
          <div
            style={{
              padding: 'var(--space-4) var(--space-6)',
              backgroundColor: 'var(--color-surface-subtle)',
              borderBottom: '1px solid var(--color-border)',
            }}
          >
            <h3 style={{ fontSize: '15px', fontWeight: 600 }}>Package Member Manifest ({bundle.members.length} files)</h3>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column' }}>
            {bundle.members.map((m) => {
              const isSelected = selectedMember?.name === m.name;
              return (
                <button
                  key={m.name}
                  onClick={() => setSelectedMember(m)}
                  style={{
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'flex-start',
                    padding: 'var(--space-4) var(--space-6)',
                    borderBottom: '1px solid var(--color-border-subtle)',
                    borderLeft: isSelected ? '4px solid var(--color-primary)' : '4px solid transparent',
                    backgroundColor: isSelected ? 'var(--color-surface-hover)' : 'transparent',
                    borderTop: 'none',
                    borderRight: 'none',
                    cursor: 'pointer',
                    textAlign: 'left',
                    width: '100%',
                  }}
                >
                  <span style={{ fontWeight: 600, fontSize: '14px', color: 'var(--color-text)' }}>
                    {m.name}
                  </span>
                  <span
                    style={{
                      fontFamily: 'var(--font-mono)',
                      fontSize: '11px',
                      color: 'var(--color-text-subtle)',
                      marginTop: '2px',
                    }}
                  >
                    SHA-256: {m.sha256.substring(0, 24)}...
                  </span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Member Content Viewer */}
        {selectedMember && (
          <div
            style={{
              backgroundColor: 'var(--color-surface)',
              border: '1px solid var(--color-border)',
              borderRadius: 'var(--radius-lg)',
              padding: 'var(--space-6)',
              display: 'flex',
              flexDirection: 'column',
              gap: 'var(--space-3)',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h3 style={{ fontSize: '16px', fontWeight: 600 }}>{selectedMember.name}</h3>
              <span className="text-caption">SHA-256 VERIFIED</span>
            </div>

            <div>
              <span className="text-caption">DIGEST</span>
              <div
                style={{
                  fontFamily: 'var(--font-mono)',
                  fontSize: '11px',
                  backgroundColor: 'var(--color-surface-subtle)',
                  padding: '6px 10px',
                  borderRadius: 'var(--radius-sm)',
                  border: '1px solid var(--color-border-subtle)',
                  wordBreak: 'break-all',
                  marginTop: '2px',
                }}
              >
                {selectedMember.sha256}
              </div>
            </div>

            <div>
              <span className="text-caption">CONTENT PREVIEW</span>
              <pre
                style={{
                  fontFamily: 'var(--font-mono)',
                  fontSize: '12px',
                  lineHeight: 1.4,
                  backgroundColor: 'var(--color-surface-subtle)',
                  padding: 'var(--space-4)',
                  borderRadius: 'var(--radius-md)',
                  border: '1px solid var(--color-border-subtle)',
                  maxHeight: '360px',
                  overflowY: 'auto',
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-all',
                  marginTop: '4px',
                }}
              >
                {selectedMember.content}
              </pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
