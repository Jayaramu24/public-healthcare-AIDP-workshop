#!/usr/bin/env python3
"""Package the inspected, exported SMML source for importing a private model copy.
This writes a local ZIP only. It does not connect to OAC or deploy anything.
"""
from pathlib import Path
import zipfile

root = Path(__file__).resolve().parents[1]
source = root / 'checkpoints/industry-semantic-model'
target = root.parent / 'MPHA_Claims_Semantic_Demo_Industry_Reset.zip'
files = sorted(source.rglob('*.json'))
if not files:
    raise SystemExit('Exported model source is missing')
if target.exists():
    raise SystemExit(f'Rename or move the existing archive first: {target}')
with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as archive:
    for path in files:
        archive.write(path, path.relative_to(source).as_posix())
print(target)
print('Import as a NEW private model; verify the existing semmodel connection and consistency.')
