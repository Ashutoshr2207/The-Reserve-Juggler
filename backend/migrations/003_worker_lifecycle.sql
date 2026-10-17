-- Durable queue, replay identity and immutable terminal evidence.
DROP TABLE schema_version;
CREATE TABLE schema_version(version INTEGER PRIMARY KEY CHECK(version = 3));
INSERT INTO schema_version VALUES(3);
ALTER TABLE runs ADD COLUMN cancel_requested INTEGER NOT NULL DEFAULT 0 CHECK(cancel_requested IN (0,1));
ALTER TABLE runs ADD COLUMN engine_version TEXT NOT NULL DEFAULT 'legacy-be03';
ALTER TABLE runs ADD COLUMN run_fingerprint TEXT;
ALTER TABLE runs ADD COLUMN provenance_json TEXT NOT NULL DEFAULT '{}';
CREATE INDEX run_queue ON runs(status, created_at);
CREATE INDEX decision_page ON decisions(workspace_id, run_id, origin, policy_id);
CREATE TABLE run_reports(
 workspace_id TEXT NOT NULL, run_id TEXT NOT NULL, policy_id TEXT NOT NULL,
 body_json TEXT NOT NULL, PRIMARY KEY(workspace_id,run_id,policy_id),
 FOREIGN KEY(workspace_id,run_id) REFERENCES runs(workspace_id,id)
);
CREATE TRIGGER run_report_no_update BEFORE UPDATE ON run_reports
 BEGIN SELECT RAISE(ABORT, 'immutable report'); END;
CREATE TRIGGER run_report_no_delete BEFORE DELETE ON run_reports
 BEGIN SELECT RAISE(ABORT, 'immutable report'); END;
CREATE TRIGGER run_report_insert_guard BEFORE INSERT ON run_reports
 WHEN (SELECT status FROM runs WHERE workspace_id=NEW.workspace_id AND id=NEW.run_id) != 'RUNNING'
 BEGIN SELECT RAISE(ABORT, 'run is not writable'); END;
DROP TRIGGER run_immutable_after_terminal;
CREATE TRIGGER run_immutable_after_terminal BEFORE UPDATE ON runs
 WHEN OLD.status IN ('COMPLETED','FAILED','CANCELLED','INTERRUPTED')
 BEGIN SELECT RAISE(ABORT, 'immutable terminal run'); END;
CREATE TRIGGER run_identity_immutable BEFORE UPDATE ON runs
 WHEN NEW.workspace_id != OLD.workspace_id OR NEW.id != OLD.id
 OR NEW.scenario_id != OLD.scenario_id OR NEW.scenario_fingerprint != OLD.scenario_fingerprint
 OR NEW.forecast_mode != OLD.forecast_mode OR NEW.adapter_artifact_id IS NOT OLD.adapter_artifact_id
 OR NEW.engine_version != OLD.engine_version OR NEW.run_fingerprint IS NOT OLD.run_fingerprint
 OR NEW.provenance_json != OLD.provenance_json OR NEW.total_hours != OLD.total_hours
 OR NEW.contract_version != OLD.contract_version OR NEW.created_at != OLD.created_at
 BEGIN SELECT RAISE(ABORT, 'immutable run identity'); END;
CREATE TRIGGER run_state_transition BEFORE UPDATE ON runs
 WHEN NOT ((OLD.status = 'QUEUED' AND NEW.status IN ('QUEUED','RUNNING','CANCELLED','INTERRUPTED'))
 OR (OLD.status = 'RUNNING' AND NEW.status IN ('RUNNING','COMPLETED','FAILED','CANCELLED','INTERRUPTED')))
 BEGIN SELECT RAISE(ABORT, 'invalid run transition'); END;
CREATE TRIGGER run_no_delete BEFORE DELETE ON runs
 BEGIN SELECT RAISE(ABORT, 'immutable run'); END;

CREATE TRIGGER run_policies_no_delete BEFORE DELETE ON run_policies
 BEGIN SELECT RAISE(ABORT, 'immutable evidence'); END;
CREATE TRIGGER run_policies_insert_guard BEFORE INSERT ON run_policies
 WHEN (SELECT status FROM runs WHERE workspace_id=NEW.workspace_id AND id=NEW.run_id) NOT IN ('QUEUED')
 BEGIN SELECT RAISE(ABORT, 'run is not writable'); END;
CREATE TRIGGER ledger_events_no_delete BEFORE DELETE ON ledger_events
 BEGIN SELECT RAISE(ABORT, 'immutable evidence'); END;
CREATE TRIGGER ledger_events_insert_guard BEFORE INSERT ON ledger_events
 WHEN (SELECT status FROM runs WHERE workspace_id=NEW.workspace_id AND id=NEW.run_id) NOT IN ('RUNNING')
 BEGIN SELECT RAISE(ABORT, 'run is not writable'); END;
CREATE TRIGGER repo_lots_no_delete BEFORE DELETE ON repo_lots
 BEGIN SELECT RAISE(ABORT, 'immutable evidence'); END;
CREATE TRIGGER repo_lots_insert_guard BEFORE INSERT ON repo_lots
 WHEN (SELECT status FROM runs WHERE workspace_id=NEW.workspace_id AND id=NEW.run_id) NOT IN ('RUNNING')
 BEGIN SELECT RAISE(ABORT, 'run is not writable'); END;
CREATE TRIGGER decisions_no_delete BEFORE DELETE ON decisions
 BEGIN SELECT RAISE(ABORT, 'immutable evidence'); END;
CREATE TRIGGER decisions_insert_guard BEFORE INSERT ON decisions
 WHEN (SELECT status FROM runs WHERE workspace_id=NEW.workspace_id AND id=NEW.run_id) NOT IN ('RUNNING')
 BEGIN SELECT RAISE(ABORT, 'run is not writable'); END;
CREATE TRIGGER metrics_no_delete BEFORE DELETE ON metrics
 BEGIN SELECT RAISE(ABORT, 'immutable evidence'); END;
CREATE TRIGGER metrics_insert_guard BEFORE INSERT ON metrics
 WHEN (SELECT status FROM runs WHERE workspace_id=NEW.workspace_id AND id=NEW.run_id) NOT IN ('RUNNING')
 BEGIN SELECT RAISE(ABORT, 'run is not writable'); END;
CREATE TRIGGER metric_sets_no_delete BEFORE DELETE ON metric_sets
 BEGIN SELECT RAISE(ABORT, 'immutable evidence'); END;
CREATE TRIGGER metric_sets_insert_guard BEFORE INSERT ON metric_sets
 WHEN (SELECT status FROM runs WHERE workspace_id=NEW.workspace_id AND id=NEW.run_id) NOT IN ('RUNNING')
 BEGIN SELECT RAISE(ABORT, 'run is not writable'); END;
CREATE TRIGGER run_policies_no_update BEFORE UPDATE ON run_policies
 BEGIN SELECT RAISE(ABORT, 'immutable evidence'); END;
CREATE TRIGGER repo_lots_no_update BEFORE UPDATE ON repo_lots
 BEGIN SELECT RAISE(ABORT, 'immutable evidence'); END;
CREATE TRIGGER metric_sets_no_update BEFORE UPDATE ON metric_sets
 BEGIN SELECT RAISE(ABORT, 'immutable evidence'); END;
