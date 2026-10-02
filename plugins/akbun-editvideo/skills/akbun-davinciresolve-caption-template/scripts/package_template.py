# /// script
# requires-python = ">=3.12"
# ///

import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[1]


def write_asset(path, data):
  if path.exists():
    if path.read_bytes() != data:
      raise ValueError(f'기존 파일 내용이 다릅니다: {path}')
    return
  with path.open('xb') as stream:
    stream.write(data)


def package(destination):
  sources = sorted((ROOT / 'assets').glob('*.setting'))
  if not sources:
    raise ValueError('패키징할 템플릿이 없습니다')
  members = {f'Edit/Titles/Akbun/{source.name}': source.read_bytes() for source in sources}
  guide = (ROOT / 'assets' / 'readme.md').read_bytes()
  digest = hashlib.sha256(b''.join(name.encode() + data for name, data in members.items()) + guide).hexdigest()
  output = destination / digest[:12]
  output.mkdir(parents=True, exist_ok=True)
  target = output / f'Akbun-Caption-{digest[:12]}.drfx'
  if target.exists():
    with ZipFile(target) as archive:
      if archive.namelist() != list(members) or any(archive.read(name) != data for name, data in members.items()):
        raise ValueError(f'기존 파일 내용이 다릅니다: {target}')
  else:
    with target.open('xb') as stream:
      with ZipFile(stream, 'w', ZIP_DEFLATED) as archive:
        for name, data in members.items():
          archive.writestr(name, data)
  with ZipFile(target) as archive:
    if archive.testzip() is not None or any(archive.read(name) != data for name, data in members.items()):
      raise ValueError('DRFX 검증 실패')
  for source in sources:
    write_asset(output / source.name, source.read_bytes())
  write_asset(output / 'readme.md', guide)
  return {
    'path': str(target), 'folder': str(output), 'bundle_sha256': digest,
    'readme': str(output / 'readme.md'), 'installed': False,
  }


def main():
  parser = argparse.ArgumentParser(description='자막 템플릿을 Downloads에 DRFX로 패키징; 설치하지 않음')
  parser.add_argument('--output', type=Path, default=Path.home() / 'Downloads' / 'Akbun-Caption')
  args = parser.parse_args()
  print(json.dumps(package(args.output.expanduser().resolve()), ensure_ascii=False, indent=2))


if __name__ == '__main__':
  main()
