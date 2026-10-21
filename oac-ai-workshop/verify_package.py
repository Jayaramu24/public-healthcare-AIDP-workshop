#!/usr/bin/env python3
"""Offline structural and data checks. Does not test OAC access or AI services."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
from decimal import Decimal
import csv
import hashlib
import json
import re
import struct

ROOT = Path(__file__).resolve().parent
errors = []
def check(condition, message):
    if not condition:
        errors.append(message)

class HTML(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.ids, self.remote_assets = [], set(), []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get('id'):
            self.ids.add(a['id'])
        for attr in ('href', 'src'):
            if a.get(attr):
                self.links.append(a[attr])
        if tag in ('script', 'img', 'iframe', 'link', 'source'):
            target = a.get('src', a.get('href', ''))
            if urlsplit(target).scheme in ('http', 'https') or target.startswith('//'):
                self.remote_assets.append(target)

def jpeg_size(path):
    data = path.read_bytes()
    check(data[:2] == b'\xff\xd8', f'Not a JPEG: {path.name}')
    i = 2
    while i < len(data):
        if data[i] != 255:
            i += 1
            continue
        while i < len(data) and data[i] == 255:
            i += 1
        marker = data[i]
        i += 1
        if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
            continue
        length = struct.unpack('>H', data[i:i+2])[0]
        if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
                      0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
            h, w = struct.unpack('>HH', data[i+3:i+7])
            return w, h
        i += length
    raise ValueError(f'JPEG dimensions missing: {path}')

parsed = HTML()
parsed.feed((ROOT/'index.html').read_text())
check(not parsed.remote_assets, f'External runtime assets: {parsed.remote_assets}')
refs = [(ROOT/'index.html', value) for value in parsed.links]
for md in ROOT.rglob('*.md'):
    for value in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)', md.read_text()):
        refs.append((md, value))
for origin, value in refs:
    target = urlsplit(value)
    if target.scheme or value.startswith('//'):
        continue
    path = (origin.parent/unquote(target.path)).resolve() if target.path else origin
    check(path.is_relative_to(ROOT), f'Link escapes package: {origin.name}: {value}')
    check(path.exists(), f'Missing link: {origin.name}: {value}')
    if path.name == 'index.html' and target.fragment:
        check(target.fragment in parsed.ids, f'Missing HTML anchor: {value}')

agenda = json.loads((ROOT/'agenda.json').read_text())
check(len(agenda) == 12, 'Agenda must contain 12 blocks including break and MCP lab')
check(sum(x['minutes'] for x in agenda) == 180, 'Agenda must total 180 minutes')
for item in agenda:
    check((ROOT/'labs'/f"{item['lab']}.md").exists(), f"Missing lab: {item['lab']}")

screenshots = json.loads((ROOT/'screenshots.json').read_text())
listed = {x['file'] for x in screenshots}
actual = {str(p.relative_to(ROOT)) for p in (ROOT/'images').rglob('*') if p.is_file()}
check(listed == actual, f'Image/manifest mismatch: {listed ^ actual}')
for item in screenshots:
    path = ROOT/item['file']
    check(path.exists(), f'Missing image: {path.name}')
    if not path.exists():
        continue
    actual_size=jpeg_size(path)
    check(actual_size == (item['width'],item['height']), f'Manifest dimensions mismatch: {path.name}')
    expected_size=(2400,1600) if item['source']=='Native Claude Desktop screenshot' else (1920,1080)
    check(actual_size == expected_size, f'Wrong image size: {path.name}')
    check(hashlib.sha256(path.read_bytes()).hexdigest() == item['sha256'],
          f'Image hash mismatch: {path.name}')
    check(item['edited'] is False, f'Unexpected edited image flag: {path.name}')
    check(bool(item['usage']), f'No image usage: {path.name}')

with (ROOT/'checkpoints/MPHA_Claims_Rollup_Seed.csv').open(newline='') as f:
    reader = csv.DictReader(f)
    rows = list(reader)
    columns = reader.fieldnames
check(len(rows) == 30 and len(columns) == 10, 'CSV shape must be 30 x 10')
check(len({(r['Service Month'], r['District Name']) for r in rows}) == 30,
      'Duplicate district-month grains')
expected = {'Claims Submitted Sum': '1400', 'Approved Claims Sum': '1214',
            'Denied Claims Sum': '121', 'Pending Claims Sum': '65',
            'Total Paid Amount Sum': '896370.39',
            'Processing Days Total Approx Sum': '19025.2'}
for key, value in expected.items():
    check(sum(Decimal(r[key]) for r in rows) == Decimal(value), f'Total mismatch: {key}')
for i, row in enumerate(rows, 1):
    n = Decimal(row['Claims Submitted Sum'])
    check(n > 0, f'Unexpected zero denominator: row {i}')
    check(n == sum(Decimal(row[k]) for k in
                  ('Approved Claims Sum', 'Denied Claims Sum', 'Pending Claims Sum')),
          f'Status counts mismatch: row {i}')
    if n:
        for output, numerator in (
                ('Claims Denial Ratio', 'Denied Claims Sum'),
                ('Weighted Processing Days Approx', 'Processing Days Total Approx Sum')):
            check(abs(Decimal(row[output]) - Decimal(row[numerator])/n) < Decimal('1e-11'),
                  f'Ratio mismatch: {output}, row {i}')

status = (ROOT/'PREPARATION_STATUS.md').read_text()
for feature in ('AI Enrichments', 'Workbook Assistant', 'Catalog Descriptions',
                'AI Assistant in Data Flows', 'Dataset Assistant',
                'Expression Assistant', 'Semantic Modeler Assistant', 'Language Narratives'):
    check(feature in status, f'Missing capability status: {feature}')
check('Industry Analytics' in status and 'zero errors and zero warnings' in status,
      'Verified instructor semantic demo status missing')
check('manual fallback validated' in status, 'Expression fallback disclosure missing')
semantic = json.loads((ROOT/'checkpoints/semantic-model-verification.json').read_text())
check(semantic['physical_tables'] == semantic['logical_tables'] == semantic['presentation_tables'] == 5,
      'Expected five tables in each semantic layer')
check(semantic['logical_fact_joins'] == 4 and len(semantic['reporting_measures']) == 8,
      'Semantic model join or reporting measure count mismatch')
check(semantic['credential_fields_found'] == 0 and semantic['deployed'] is False,
      'Private model credential/deployment assertion mismatch')
model_source = ROOT/'checkpoints/industry-semantic-model'
model_json = list(model_source.rglob('*.json'))
check(len(model_json) == 19, 'Exported model must contain 19 JSON files')
fact = json.loads((model_source/'logical/MPHA Claims/Claims Metrics.json').read_text())['logicalTable']
logical_columns = {c['name']: c for c in fact['logicalColumns']}
for name in semantic['additive_sum_measures']:
    check(logical_columns[name].get('aggregation', {}).get('rule') == 'SUM',
          f'Wrong semantic aggregation: {name}')
check(logical_columns['Claims Denial Ratio']['logicalColumnSource'] == semantic['ratio_definition'],
      'Derived denial ratio differs from inspected model')
reporting = json.loads((model_source/'presentation/MPHA Claims Workshop Demo/Claims Metrics.json').read_text())['presentationTable']
check([c['name'] for c in reporting['presentationColumns']] == semantic['reporting_measures'],
      'Presentation measure set differs from inspected export')
def scan_model_keys(value, location):
    if isinstance(value, dict):
        for key, child in value.items():
            check(not re.search(r'password|credential|token|wallet|secret|private.?key', key, re.I),
                  f'Unexpected sensitive key in model: {location}/{key}')
            scan_model_keys(child, location+'/'+key)
    elif isinstance(value, list):
        for i, child in enumerate(value):
            scan_model_keys(child, location+'/'+str(i))
for path in model_json:
    scan_model_keys(json.loads(path.read_text()), str(path.relative_to(model_source)))
check(not list(ROOT.rglob('*.zip')), 'Nested ZIP or wallet must not ship inside module')
check(not list(ROOT.rglob('*.pem')), 'Credential PEM must not ship inside module')
check(not list(ROOT.rglob('*.sso')), 'Wallet must not ship inside module')

# Added MCP artifacts: check data and saved native structure independently.
mcp=ROOT/'mcp'
snapshot=json.loads((mcp/'claims-mcp-snapshot.json').read_text())
check(len(snapshot['rows'])==30, 'MCP snapshot must have 30 rows')
check(len({(r[0],r[1]) for r in snapshot['rows']})==30, 'MCP snapshot grains must be unique')
csv_by_grain={(r['Service Month'][:7],r['District Name']):r for r in rows}
for r in snapshot['rows']:
    source=csv_by_grain.get((r[0],r[1]))
    check(source is not None, f'MCP snapshot grain absent from OAC checkpoint: {r[:2]}')
    if source:
        for pos,col in enumerate(('Claims Submitted Sum','Approved Claims Sum','Denied Claims Sum','Pending Claims Sum','Total Paid Amount Sum','Processing Days Total Approx Sum'),2):
            check(abs(Decimal(str(r[pos]))-Decimal(source[col]))<Decimal('1e-8'),f'MCP snapshot value mismatch: {r[:2]} {col}')
html_source=(mcp/'MPHA_Executive_Overview.html').read_text()
html_check=HTML();html_check.feed(html_source)
check(not html_check.remote_assets, 'Executive HTML has external runtime assets')
html_book=json.loads((mcp/'MPHA_MCP_Executive_HTML.workbook.json').read_text())
native_book=json.loads((mcp/'MPHA_MCP_Executive_Native.workbook.json').read_text())
frame=next(v for v in html_book['views']['children'] if v.get('pluginType')=='oracle.bi.tech.iframe')
frame_settings=frame['viewConfig']['settings']['oracle.bi.tech.iframe']['settings']
check(frame_settings['sourceType']=='SRCDOC' and frame_settings['frameSrc']==html_source,'Iframe source differs from reviewed HTML')
for book in (html_book,native_book):
    check(book['projectVersion']==1168,'MCP workbook projectVersion changed unexpectedly')
    check('@sharedcalc' not in json.dumps(book),'MCP workbook has unresolved shared calculation')
    view_names={v['viewName'] for v in book['views']['children']}
    for layout in book['layouts']['children']:
        for box in layout['children']:
            check(box['content']['viewName'] in view_names,'MCP layout references a missing visual')
plugins=[v.get('pluginType') for v in native_book['views']['children']]
check(plugins.count('oracle.bi.tech.ngperformancetile')==4,'Native must have four performance tiles')
for plugin in ('oracle.bi.tech.table','oracle.bi.tech.chart.line','oracle.bi.tech.chart.horizontalbar'):
    check(plugins.count(plugin)==1,'Native visual missing: '+plugin)
native_columns={c['columnID']:c for c in native_book['criteria']['columns']['children']}
for ident in ('DistrictApprovalRatio','DistrictDenialRatio','DistrictWeightedDays'):
    expression=native_columns[ident]['columnFormula']['expr']['expression']
    check(expression.count(' BY ')==3 and 'District Name' in expression,'Explicit district-grain guard missing: '+ident)
    check('THEN NULL' in expression,'Zero-denominator guard missing: '+ident)
for ident in ('ApprovalRatio','DenialRatio'):
    check(' BY ' not in native_columns[ident]['columnFormula']['expr']['expression'],'Overall KPI accidentally fixed to district grain')
table_view=next(v for v in native_book['views']['children'] if v.get('pluginType')=='oracle.bi.tech.table')
for ident in ('DistrictApprovalRatio','DistrictDenialRatio'):
    fmt=table_view['viewConfig']['settings']['viz:chart']['bidvtchart_number_format_'+ident]
    check(fmt['style']=='percent','Native table rate is not formatted as percent')
evidence=json.loads((mcp/'verification.json').read_text())
check({x['name'] for x in evidence['workbooks']}=={'MPHA_MCP_Executive_HTML','MPHA_MCP_Executive_Native'},'Expected approved MCP workbook names')
check(all(x['create_status']=='ok 200' for x in evidence['workbooks']),'Missing successful MCP create evidence')
policy=json.loads((mcp/'compat-config.example.json').read_text())['savePolicy']
check(len(policy['createNames'])==2 and not policy['replaceIds'],'Portable write policy must be create-only with exactly two names')
for path in ROOT.rglob('*'):
    if path.is_file():
        check('private-state' not in str(path.relative_to(ROOT)) and path.name not in ('token.json','claude_desktop_config.json','origami-bridge.json'),'Private runtime/config must not be packaged: '+path.name)

manifest_path = ROOT/'package-manifest.json'
if manifest_path.exists():
    file_manifest = json.loads(manifest_path.read_text())
    actual_paths = {str(p.relative_to(ROOT)) for p in ROOT.rglob('*')
                    if p.is_file() and p.name != 'package-manifest.json'}
    check({x['file'] for x in file_manifest} == actual_paths, 'Package file manifest mismatch')
    for item in file_manifest:
        path = ROOT/item['file']
        check(path.exists() and hashlib.sha256(path.read_bytes()).hexdigest() == item['sha256'],
              f"Package hash mismatch: {item['file']}")

if errors:
    print('\n'.join('FAIL: '+x for x in errors))
    raise SystemExit(1)
print(json.dumps({'result': 'passed', 'minutes': 180, 'agenda_blocks': len(agenda),
                  'screenshots': len(screenshots), 'screenshots_1920x1080': sum(x['width']==1920 for x in screenshots), 'native_claude_2400x1600': sum(x['width']==2400 for x in screenshots), 'local_links_checked': len(refs),
                  'csv_rows': len(rows), 'csv_columns': len(columns),
                  'limits': 'Offline checks only; see PREPARATION_STATUS.md for OAC release gates'},
                 indent=2))
