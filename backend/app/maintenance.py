"""Offline backup/restore. Operator paths stay in backend/work; never overwrite."""
import argparse
import hashlib
import json
import re
import shutil
import sqlite3
from contextlib import closing
from pathlib import Path

from app.api.contracts import ROOT, canonical
from app.services.worker import RuntimeLease


def local_path(value):
    path = Path(value).resolve()
    if not path.is_relative_to((ROOT / 'work').resolve()) or path == (ROOT / 'work').resolve():
        raise ValueError('Maintenance paths must be below backend/work')
    return path


def verify_runtime(root):
    root = local_path(root)
    database = root / 'metadata.sqlite3'
    with closing(sqlite3.connect(database.as_uri() + '?mode=ro', uri=True)) as db:
        if db.execute('PRAGMA integrity_check').fetchone()[0] != 'ok' or db.execute('PRAGMA foreign_key_check').fetchall():
            raise ValueError('Database integrity failed')
        if db.execute('SELECT version FROM schema_version').fetchone()[0] not in (1, 2, 3):
            raise ValueError('Unsupported snapshot schema')
        files = {'metadata.sqlite3': hashlib.sha256(database.read_bytes()).hexdigest()}
        for workspace, digest, filename in db.execute('SELECT workspace_id,sha256,source_name FROM datasets'):
            if not re.fullmatch(r'ws_[0-9a-f]{32}', workspace) or not re.fullmatch(r'[0-9a-f]{64}', digest) or filename != digest + '.csv':
                raise ValueError('Unsafe source reference')
            name = f'{workspace}/raw/{filename}'
            actual = hashlib.sha256((root / name).read_bytes()).hexdigest()
            if actual != digest:
                raise ValueError('Source integrity failed')
            files[name] = actual
    return files


def snapshot(source, target, restore=False):
    source, target = local_path(source), local_path(target)
    if target.exists() or target.is_relative_to(source) or source.is_relative_to(target):
        raise ValueError('Use a new, separate destination; existing files are never overwritten')
    lease = RuntimeLease(source)
    lease.acquire()
    try:
        files = verify_runtime(source)
        if restore:
            expected = json.loads((source / 'snapshot_manifest.json').read_text())['files_sha256']
            if files != expected:
                raise ValueError('Snapshot manifest integrity failed')
        target.mkdir(parents=True)
        for name in files:
            output = target / name
            output.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source / name, output)
        (target / 'snapshot_manifest.json').write_text(canonical({'files_sha256': files,
            'note': 'Local offline snapshot; retain matching source and requirements.lock; backups retain data.'}), encoding='utf-8')
        if verify_runtime(target) != files:
            raise ValueError('Copied snapshot failed verification; preserve destination for diagnosis')
        return {'files': len(files), 'verified': True}
    finally:
        lease.release()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['backup', 'restore', 'verify'])
    parser.add_argument('source')
    parser.add_argument('destination', nargs='?')
    args = parser.parse_args()
    if args.action == 'verify':
        lease = RuntimeLease(local_path(args.source))
        lease.acquire()
        try:
            result = {'files': len(verify_runtime(args.source)), 'verified': True}
        finally:
            lease.release()
    else:
        if args.destination is None:
            parser.error('A new destination is required')
        result = snapshot(args.source, args.destination, restore=args.action == 'restore')
    print(json.dumps(result, indent=2))
