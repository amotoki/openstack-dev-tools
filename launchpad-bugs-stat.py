import argparse
import collections
from datetime import datetime
from datetime import timezone
import json
import sys

from launchpadlib.launchpad import Launchpad
from prettytable import PrettyTable


KNOWN_STATUSES = ['New', 'Confirmed', 'Triaged', 'In Progress']
KNOWN_PRIORITIES = ['Critical', 'High', 'Medium', 'Low', 'Wishlist', 'Undecided']

parser = argparse.ArgumentParser('')
parser.add_argument('project')
parser.add_argument('--quiet', action='store_true')
parser.add_argument('--stat-file')
args = parser.parse_args()


if args.stat_file:
    try:
        with open(args.stat_file) as f:
            saved_data = json.loads(f.read())
    except FileNotFoundError:
        saved_data = {}


lp = Launchpad.login_anonymously('just testing', 'production')
proj = lp.projects[args.project]

bugtasks = proj.searchTasks()

stat = {}

for bugtask in bugtasks:
    status = bugtask.status
    priority = bugtask.importance
    if status not in stat:
        stat[status] = collections.defaultdict(int)
    stat[status][priority] += 1


if args.stat_file:
    timestamp = datetime.now(timezone.utc).astimezone().isoformat()
    saved_data[timestamp] = stat
    with open(args.stat_file, 'w') as f:
        f.write(json.dumps(saved_data, indent=4, sort_keys=True))


unknown_statuses = set(stat.keys()) - set(KNOWN_STATUSES)

x = PrettyTable()

x.field_names = ['Status'] + KNOWN_PRIORITIES + ['Total']
for status in KNOWN_STATUSES + list(unknown_statuses):
    count = stat[status]
    d = [status]
    for p in KNOWN_PRIORITIES:
        d.append(count.get(p, 0))
    total = sum(d[1:])
    d.append(total)
    x.add_row(d)

print(x)
