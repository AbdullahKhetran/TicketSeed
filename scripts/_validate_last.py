import json, sys, pathlib, textwrap
sys.path.insert(0, '.')
from backend.app.models import SprintPlan

raw = pathlib.Path('scripts/last_response.json').read_text(encoding='utf-8').strip()
if raw.startswith('```'):
    raw = raw[raw.index('\n')+1:]
if raw.endswith('```'):
    raw = raw[:raw.rfind('```')]
raw = raw.strip()

data = json.loads(raw)
plan = SprintPlan.model_validate(data)
print('[OK] Pydantic validation passed')
print(f'  Project      : {plan.project.name}')
print(f'  Requirements : {len(plan.requirements)}')
print(f'  Sprints      : {len(plan.sprints)}')
print(f'  Questions    : {len(plan.client_questions)}')
for s in plan.sprints:
    print(f'  {s.id} ({s.name}): {len(s.requirement_ids)} reqs, depends_on={s.depends_on}')
print()
print('Client questions:')
for q in plan.client_questions:
    print(f'  {q.id}: {q.question[:80]}...')
