"""Download pinned Flink connectors; refuse bytes differing from Maven SHA-512."""
import hashlib, json, pathlib, urllib.request
root = pathlib.Path(__file__).resolve().parents[1]
folder = root / 'infra/flink/lib'
folder.mkdir(exist_ok=True)
for item in json.loads((root / 'infra/flink/artifacts.json').read_text()):
    expected = urllib.request.urlopen(item['url'] + '.sha512', timeout=30).read().decode().split()[0]
    data = urllib.request.urlopen(item['url'], timeout=60).read()
    if hashlib.sha512(data).hexdigest() != expected:
        raise SystemExit('Artifact checksum mismatch: ' + item['name'])
    (folder / item['name']).write_bytes(data)
    print(item['name'], hashlib.sha256(data).hexdigest())
