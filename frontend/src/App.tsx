import React, { useState, useEffect } from 'react';
import { Workspace, Dataset, Scenario, Run } from './types/contracts';
import { api } from './client/api';
import { AppShell, ScreenId } from './components/AppShell';
import { ScreenData } from './screens/ScreenData';
import { ScreenScenario } from './screens/ScreenScenario';
import { ScreenReview } from './screens/ScreenReview';
import { ScreenCompare } from './screens/ScreenCompare';
import { ScreenDecision } from './screens/ScreenDecision';
import { ScreenEvidence } from './screens/ScreenEvidence';

export const App: React.FC = () => {
  const [workspace, setWorkspace] = useState<Workspace | null>(null);
  const [dataset, setDataset] = useState<Dataset | null>(null);
  const [scenario, setScenario] = useState<Scenario | null>(null);
  const [activeRun, setActiveRun] = useState<Run | null>(null);
  const [currentScreen, setCurrentScreen] = useState<ScreenId>('S1');
  const [isFixtureMode, setIsFixtureMode] = useState(false);

  useEffect(() => {
    async function init() {
      const ws = await api.getWorkspace();
      setWorkspace(ws);
      setIsFixtureMode(api.getIsFixtureMode());
      // Clean empty state per FLOW.md and DESIGN.md; no auto-loaded completed runs.
    }
    init();
  }, []);

  const currentRole = workspace?.role_mode || 'maker';

  return (
    <AppShell
      currentScreen={currentScreen}
      onSelectScreen={setCurrentScreen}
      workspace={workspace}
      isFixtureMode={isFixtureMode}
    >
      {currentScreen === 'S1' && (
        <ScreenData
          dataset={dataset}
          roleMode={currentRole}
          onDatasetLoaded={(ds) => {
            setDataset(ds);
            setIsFixtureMode(api.getIsFixtureMode());
          }}
          onNavigateNext={() => setCurrentScreen('S2')}
        />
      )}

      {currentScreen === 'S2' && (
        <ScreenScenario
          dataset={dataset}
          scenario={scenario}
          roleMode={currentRole}
          onScenarioSaved={(sc) => setScenario(sc)}
          onNavigateNext={() => setCurrentScreen('S3')}
        />
      )}

      {currentScreen === 'S3' && (
        <ScreenReview
          scenario={scenario}
          roleMode={currentRole}
          onScenarioReviewed={(sc) => setScenario(sc)}
          onReturnToDraft={() => setCurrentScreen('S2')}
          onNavigateNext={() => setCurrentScreen('S4')}
        />
      )}

      {currentScreen === 'S4' && (
        <ScreenCompare
          scenario={scenario}
          activeRun={activeRun}
          roleMode={currentRole}
          onRunCreated={(run) => setActiveRun(run)}
          onNavigateDecisions={() => setCurrentScreen('S5')}
        />
      )}

      {currentScreen === 'S5' && (
        <ScreenDecision
          activeRun={activeRun}
          onNavigateEvidence={() => setCurrentScreen('S6')}
        />
      )}

      {currentScreen === 'S6' && (
        <ScreenEvidence activeRun={activeRun} />
      )}
    </AppShell>
  );
};
