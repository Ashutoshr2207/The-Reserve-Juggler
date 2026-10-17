CREATE TABLE schema_version(version INTEGER PRIMARY KEY CHECK(version = 1));
INSERT INTO schema_version VALUES(1);
CREATE TABLE workspaces(id TEXT PRIMARY KEY);
CREATE TABLE datasets(
 workspace_id TEXT NOT NULL REFERENCES workspaces(id), id TEXT NOT NULL,
 sha256 TEXT NOT NULL, source_name TEXT NOT NULL, profile_json TEXT NOT NULL,
 PRIMARY KEY(workspace_id,id), UNIQUE(workspace_id,sha256)
);
CREATE TABLE scenarios(
 workspace_id TEXT NOT NULL, id TEXT NOT NULL, dataset_id TEXT NOT NULL,
 fingerprint TEXT NOT NULL, body_json TEXT NOT NULL, status TEXT NOT NULL CHECK(status IN ('DRAFT','REVIEWED')),
 PRIMARY KEY(workspace_id,id), FOREIGN KEY(workspace_id,dataset_id) REFERENCES datasets(workspace_id,id)
);
CREATE TABLE reviews(
 workspace_id TEXT NOT NULL, scenario_id TEXT NOT NULL, fingerprint TEXT NOT NULL,
 actor_label TEXT NOT NULL, mode TEXT NOT NULL CHECK(mode IN ('self_review','local_reviewer')),
 reviewed_at TEXT NOT NULL, PRIMARY KEY(workspace_id,scenario_id),
 FOREIGN KEY(workspace_id,scenario_id) REFERENCES scenarios(workspace_id,id)
);
CREATE TABLE idempotency(
 workspace_id TEXT NOT NULL REFERENCES workspaces(id), operation TEXT NOT NULL, key TEXT NOT NULL,
 payload_hash TEXT NOT NULL, response_json TEXT, response_status INTEGER, headers_json TEXT,
 expires_at REAL NOT NULL, PRIMARY KEY(workspace_id,operation,key)
);
CREATE TRIGGER dataset_immutable BEFORE UPDATE ON datasets BEGIN SELECT RAISE(ABORT,'immutable dataset'); END;
CREATE TRIGGER scenario_immutable BEFORE UPDATE ON scenarios
 WHEN NEW.workspace_id != OLD.workspace_id OR NEW.id != OLD.id OR NEW.dataset_id != OLD.dataset_id
 OR NEW.fingerprint != OLD.fingerprint OR NEW.body_json != OLD.body_json
 OR NOT (OLD.status = 'DRAFT' AND NEW.status = 'REVIEWED')
 BEGIN SELECT RAISE(ABORT,'immutable scenario'); END;
CREATE TRIGGER review_immutable BEFORE UPDATE ON reviews BEGIN SELECT RAISE(ABORT,'immutable review'); END;
