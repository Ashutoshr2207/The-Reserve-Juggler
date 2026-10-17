"""Verify unsigned export member integrity without extracting or executing content."""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.api.contracts import validate


def verify(bundle):
    validate('EvidenceBundle', bundle, output=True)
    allowed = {'manifest.json', 'metrics.json', 'decisions.json', 'ledger_events.json',
               'comparison.json', 'scenario.json', 'dataset_profile.json', 'review.json',
               'provenance.json', 'repo_lots.json', 'accounting.json'}
    members = {}
    for member in bundle['members']:
        name = member['name']
        if name not in allowed or name in members:
            raise ValueError('Unexpected or duplicate bundle member')
        digest = hashlib.sha256(member['content'].encode('utf-8')).hexdigest()
        if digest != member['sha256']:
            raise ValueError('Member digest mismatch')
        members[name] = member
    if set(members) != allowed:
        raise ValueError('Required replay members are missing')
    manifest = json.loads(members['manifest.json']['content'])
    actual = {name: member['sha256'] for name, member in members.items() if name != 'manifest.json'}
    if manifest['members_sha256'] != actual or manifest['run_id'] != bundle['run_id']:
        raise ValueError('Manifest does not match bundle')
    return {'run_id': bundle['run_id'], 'verified_members': len(members),
            'integrity_only': True, 'digitally_signed': False}


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Usage: python tools/verify_export.py <export.json>')
    print(json.dumps(verify(json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))), indent=2))
