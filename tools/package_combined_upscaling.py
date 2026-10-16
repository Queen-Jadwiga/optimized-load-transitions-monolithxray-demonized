"""Package the combined candidate; never install into a game directory."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import xml.etree.ElementTree as ET
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
RUNTIME_SHA256 = '3975567b8943c53acce397f2b72380092f84f162d00b0d2c7d08a1025c563983'
UPSCALING_SOURCE = '854dd2795203f8bd8992cb5a0c9646b57804652e'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def archive(stage, target):
    with ZipFile(target, 'w', compression=ZIP_DEFLATED, compresslevel=9) as out:
        for path in sorted(stage.rglob('*')):
            if path.is_file():
                info = ZipInfo(path.relative_to(stage).as_posix(), (2026, 10, 16, 0, 0, 0))
                info.compress_type = ZIP_DEFLATED
                info.external_attr = 0o644 << 16
                out.writestr(info, path.read_bytes(), compresslevel=9)

def copy(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)

def build(output, configuration, runtime):
    output.mkdir(parents=True, exist_ok=False)
    spec = importlib.util.spec_from_file_location('compatibility', ROOT / 'tools/dlss/package_compatibility.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.build(output / 'upstream-compatibility')
    stage = output / 'upstream-compatibility/package'
    instructions = (ROOT / 'docs/load-transitions/COMBINED_TEST.md').read_text()
    (stage / 'COMBINED_TEST.md').write_text(instructions, encoding='utf-8')
    (stage / 'README.txt').write_text(instructions, encoding='utf-8')
    for name, tag in [('info.xml', 'Name'), ('ModuleConfig.xml', 'moduleName')]:
        path = stage / 'fomod' / name
        tree = ET.parse(path)
        tree.getroot().find(tag).text = 'Optimized Load & Transitions + DLSS/FSR - Combined Test 1'
        if name == 'info.xml':
            tree.getroot().find('Version').text = '0.1.0'
            tree.getroot().find('Description').text = 'Requires the matching Combined Test 1 engine and SSS 23.5; uses brodrigz/bepis 0.5 compatibility shaders.'
        tree.write(path, encoding='utf-8', xml_declaration=True)
    for element in ET.parse(stage / 'fomod/ModuleConfig.xml').iter():
        if element.tag in ('file', 'folder'):
            source = stage / element.attrib['source'].replace('\\', '/')
            if not source.exists():
                raise RuntimeError(f'Missing FOMOD source: {source.relative_to(stage)}')
    patch = output / 'combined-upscaling-compatibility-test1.zip'
    archive(stage, patch)
    products = [patch]
    if runtime is not None:
        if digest(runtime) != RUNTIME_SHA256:
            raise RuntimeError('NVIDIA runtime SHA256 mismatch')
        binary_stage = output / 'binary-package'
        target = 'AnomalyDX11AVX' if configuration == 'DX11-AVX' else 'AnomalyDX11'
        for suffix in ('.exe', '.pdb'):
            copy(ROOT / '_build/_game/bin_dbg' / (target + suffix), binary_stage / 'bin' / (target + suffix))
        copy(runtime, binary_stage / 'bin/nvngx_dlss.dll')
        copy(ROOT / 'License.txt', binary_stage / 'License.txt')
        for src, dst in [('sdk/DLSS/LICENSE.txt', 'NVIDIA-DLSS.txt'),
                         ('sdk/FSR3/LICENSE.txt', 'AMD-FSR.txt'),
                         ('sdk/FSR3/Third_party_notices.txt', 'FSR-third-party-notices.txt')]:
            copy(ROOT / src, binary_stage / 'licenses' / dst)
        copy(ROOT / 'tools/dlss/release/CREDITS.txt', binary_stage / 'UPSCALING-CREDITS.txt')
        copy(ROOT / 'docs/load-transitions/COMBINED_TEST.md', binary_stage / 'INSTALL.md')
        provenance = {
            'status': 'experimental; game runtime, image quality and speedup unverified',
            'commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            'configuration': configuration,
            'upscaling_source': UPSCALING_SOURCE,
            'files': {p.relative_to(binary_stage).as_posix(): digest(p)
                      for p in sorted(binary_stage.rglob('*')) if p.is_file()},
        }
        (binary_stage / 'PROVENANCE.json').write_text(json.dumps(provenance, indent=2) + '\n', encoding='utf-8')
        binary = output / f'combined-load-upscaling-test1-{configuration}.zip'
        archive(binary_stage, binary)
        products.append(binary)
    (output / 'SHA256SUMS.txt').write_text(''.join(f'{digest(p)}  {p.name}\n' for p in products), encoding='utf-8')
    for path in products:
        print(f'Packaged {path.name}: {path.stat().st_size} bytes; SHA256 {digest(path)}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--configuration', choices=['DX11', 'DX11-AVX'], default='DX11-AVX')
    parser.add_argument('--runtime', type=Path)
    args = parser.parse_args()
    build(args.output.resolve(), args.configuration, args.runtime)
