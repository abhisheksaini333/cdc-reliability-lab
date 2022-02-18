"""Download pinned Flink connectors; refuse bytes differing from the reviewed SHA-256 lock."""
import hashlib, json, pathlib, urllib.request
root = pathlib.Path(__file__).resolve().parents[1]
folder = root / 'infra/flink/lib'
folder.mkdir(exist_ok=True)
for item in json.loads((root / 'infra/flink/artifacts.json').read_text()):
    expected = item['sha256']
    data = urllib.request.urlopen(item['url'], timeout=60).read()
    if hashlib.sha256(data).hexdigest() != expected:
        raise SystemExit('Artifact checksum mismatch: ' + item['name'])
    (folder / item['name']).write_bytes(data)
    print(item['name'], hashlib.sha256(data).hexdigest())
