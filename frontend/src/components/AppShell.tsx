import React, { useState } from 'react';
import { Workspace } from '../types/contracts';
import {
  IconDataset,
  IconScenario,
  IconReview,
  IconCompare,
  IconDecision,
  IconEvidence,
} from './Icons';
import { WorkspaceBadge } from './WorkspaceBadge';
import { LiveApiStatusBadge } from './SyntheticModeNotice';
import { LegalModal } from './LegalModals';

export type ScreenId = 'S1' | 'S2' | 'S3' | 'S4' | 'S5' | 'S6';

interface AppShellProps {
  currentScreen: ScreenId;
  onSelectScreen: (screen: ScreenId) => void;
  workspace: Workspace | null;
  isFixtureMode: boolean;
  children: React.ReactNode;
}

export const AppShell: React.FC<AppShellProps> = ({
  currentScreen,
  onSelectScreen,
  workspace,
  isFixtureMode,
  children,
}) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [legalModalType, setLegalModalType] = useState<'terms' | 'privacy' | null>(null);

  const navItems: Array<{ id: ScreenId; label: string; code: string; icon: React.ReactNode }> = [
    { id: 'S1', label: 'Data Intake', code: 'S1 Data', icon: <IconDataset size={18} /> },
    { id: 'S2', label: 'Scenario Policy', code: 'S2 Scenario', icon: <IconScenario size={18} /> },
    { id: 'S3', label: 'Review & Commit', code: 'S3 Review', icon: <IconReview size={18} /> },
    { id: 'S4', label: 'Policy Compare', code: 'S4 Compare', icon: <IconCompare size={18} /> },
    { id: 'S5', label: 'Decision Inspector', code: 'S5 Decision', icon: <IconDecision size={18} /> },
    { id: 'S6', label: 'Audit Evidence', code: 'S6 Evidence', icon: <IconEvidence size={18} /> },
  ];

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <a href="#main-content" className="skip-link">
        Skip to main content
      </a>

      {/* Top Application Bar */}
      <header
        style={{
          height: '60px',
          backgroundColor: 'var(--color-surface)',
          borderBottom: '1px solid var(--color-border)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0 var(--space-6)',
          position: 'sticky',
          top: 0,
          zIndex: 100,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-4)' }}>
          {/* Mobile hamburger */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Toggle navigation menu"
            style={{
              display: 'none',
              background: 'transparent',
              border: 'none',
              cursor: 'pointer',
              padding: '6px',
            }}
            className="mobile-menu-btn"
          >
            <span style={{ fontSize: '20px', lineHeight: 1 }}>☰</span>
          </button>

          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
            <div
              style={{
                width: '32px',
                height: '32px',
                borderRadius: '6px',
                backgroundColor: 'var(--color-primary)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#FFFFFF',
                fontWeight: 700,
                fontSize: '16px',
              }}
            >
              RJ
            </div>
            <div>
              <div style={{ fontWeight: 700, fontSize: '16px', color: 'var(--color-text)', letterSpacing: '-0.2px' }}>
                Reserve Juggler
              </div>
              <div className="text-caption" style={{ fontSize: '11px' }}>
                Treasury Policy Simulator &bull; Scope 0.2.0
              </div>
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
          <LiveApiStatusBadge isFixtureMode={isFixtureMode} />
          <WorkspaceBadge workspace={workspace} />
        </div>
      </header>

      {/* Main Body with Sidebar */}
      <div style={{ display: 'flex', flex: 1, minHeight: 'calc(100vh - 60px)' }}>
        {/* Sidebar Nav */}
        <nav
          aria-label="Primary Workflow Navigation"
          style={{
            width: 'var(--nav-width)',
            backgroundColor: 'var(--color-surface)',
            borderRight: '1px solid var(--color-border)',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between',
            padding: 'var(--space-4) 0',
          }}
          className={`sidebar-nav ${mobileMenuOpen ? 'mobile-open' : ''}`}
        >
          <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
            <div
              style={{
                padding: 'var(--space-2) var(--space-4)',
                fontSize: '11px',
                fontWeight: 700,
                color: 'var(--color-text-subtle)',
                textTransform: 'uppercase',
                letterSpacing: '0.6px',
              }}
            >
              Workflow Pipeline
            </div>

            {navItems.map((item) => {
              const isActive = currentScreen === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => {
                    onSelectScreen(item.id);
                    setMobileMenuOpen(false);
                  }}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 'var(--space-3)',
                    padding: '10px var(--space-4)',
                    backgroundColor: isActive ? 'var(--color-primary-light)' : 'transparent',
                    color: isActive ? 'var(--color-primary)' : 'var(--color-text)',
                    border: 'none',
                    borderLeft: isActive ? '3px solid var(--color-primary)' : '3px solid transparent',
                    cursor: 'pointer',
                    textAlign: 'left',
                    fontWeight: isActive ? 600 : 500,
                    fontSize: '14px',
                    transition: 'background-color 0.15s ease',
                  }}
                >
                  <span style={{ color: isActive ? 'var(--color-primary)' : 'var(--color-text-muted)' }}>
                    {item.icon}
                  </span>
                  <span>{item.code}</span>
                </button>
              );
            })}
          </div>

          {/* Sidebar Footer with Legal / Scope links */}
          <div
            style={{
              padding: 'var(--space-4)',
              borderTop: '1px solid var(--color-border)',
              display: 'flex',
              flexDirection: 'column',
              gap: '6px',
              fontSize: '12px',
            }}
          >
            <div style={{ color: 'var(--color-text-subtle)', marginBottom: '4px' }}>
              Local OS Boundary
            </div>
            <button
              onClick={() => setLegalModalType('terms')}
              style={{
                background: 'transparent',
                border: 'none',
                color: 'var(--color-primary)',
                cursor: 'pointer',
                textAlign: 'left',
                padding: 0,
                fontSize: '12px',
              }}
            >
              Terms of Simulation
            </button>
            <button
              onClick={() => setLegalModalType('privacy')}
              style={{
                background: 'transparent',
                border: 'none',
                color: 'var(--color-primary)',
                cursor: 'pointer',
                textAlign: 'left',
                padding: 0,
                fontSize: '12px',
              }}
            >
              Local Privacy Policy
            </button>
          </div>
        </nav>

        {/* Main Content Area */}
        <main
          id="main-content"
          style={{
            flex: 1,
            backgroundColor: 'var(--color-canvas)',
            padding: 'var(--space-6)',
            maxWidth: 'calc(100vw - var(--nav-width))',
          }}
        >
          <div style={{ maxWidth: 'var(--content-max-width)', margin: '0 auto' }}>
            {children}
          </div>
        </main>
      </div>

      <LegalModal
        isOpen={legalModalType !== null}
        type={legalModalType}
        onClose={() => setLegalModalType(null)}
      />
    </div>
  );
};
