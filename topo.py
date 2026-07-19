import os
os.environ["DJANGO_SETTINGS_MODULE"] = "project.settings"
import django
django.setup()
from django.db.migrations.loader import MigrationLoader
from collections import defaultdict, deque

loader = MigrationLoader(None, ignore_no_migrations=True)
graph = loader.graph

children_of = defaultdict(set)
for node in graph.nodes:
    for child in graph.node_map[node].children:
        children_of[child].add(node)

in_degree = defaultdict(int)
for node in graph.nodes:
    in_degree[node] = len(children_of.get(node, set()))

queue = deque([n for n in graph.nodes if in_degree[n] == 0])
topo = []

while queue:
    node = queue.popleft()
    topo.append(node)
    for child in graph.node_map[node].children:
        in_degree[child] -= 1
        if in_degree[child] == 0:
            queue.append(child)

for app, name in topo:
    if app in ("condominium", "parameters"):
        print(f"{app:20s} {name}")
