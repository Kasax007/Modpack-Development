"""qrun_plan.py [OUT.json] : the quest book as a run plan for the in-game quest check (dctest -Pscene=qrun).

Every quest of tools/dc_quests.py with its tasks and rewards, in an order where each quest comes after all of its
dependencies (chapter order otherwise). The harness (QuestRun.java) works through the list: it fulfils every task the
way a player would (items in the inventory, mobs killed by the player, the real structure / biome / dimension
visited, the creature looked at, the checkbox ticked), waits for Quest Icons to complete the quest and claims the
rewards.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import dc_quests as D

SP = '/tmp/claude-0/-home-user/4ca9508b-4f8c-5a8e-91dc-6059d6cc887c/scratchpad'
out = sys.argv[1] if len(sys.argv) > 1 else f'{SP}/v13/qrun_plan.json'

quests = []
for c in D.B.chapters:
    for q in c.quests:
        quests.append({
            'id': q['id'], 'key': f"{c.key}:{q['_key']}", 'title': q['title'], 'optional': bool(q.get('optional')),
            'deps': list(q.get('dependencies', [])), 'any': q.get('dependency_requirement') == 'one_completed',
            'tasks': q['tasks'], 'rewards': q.get('rewards', []),
        })
by_id = {q['id']: q for q in quests}
done, order = set(), []


def visit(q, stack=()):
    if q['id'] in done: return
    if q['id'] in stack: raise SystemExit(f"dependency cycle at {q['key']}")
    for d in q['deps']:
        if d in by_id: visit(by_id[d], stack + (q['id'],))
    done.add(q['id'])
    order.append(q)


for q in quests: visit(q)
json.dump({'quests': order}, open(out, 'w'), indent=1)
print(len(order), 'quests ->', out)
