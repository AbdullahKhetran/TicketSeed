import truststore; truststore.inject_into_ssl()
import httpx

resp = httpx.post(
    "http://localhost:8000/api/plan/sprints",
    json={"prd_markdown": "## Test App\nUsers can sign up and log in."},
    timeout=120,
)
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json()
    print(f"Validation ok: {data['validation']['ok']}")
    print(f"Issues: {data['validation']['issues']}")
    print(f"Sprints: {[s['id'] for s in data['plan']['sprints']]}")
    print(f"Requirements: {[r['id'] for r in data['plan']['requirements']]}")
else:
    print(resp.text)
