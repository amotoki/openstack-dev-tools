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


# Calculate total per status
total = collections.defaultdict(int)
for status in stat:
    count = stat[status]
    status_total = sum(count.values())
    stat[status]['Total'] = status_total
    for p in KNOWN_PRIORITIES:
        total[p] += count[p]
    total['Total'] += status_total
stat['Summary'] = total


if args.stat_file:
    timestamp = datetime.now(timezone.utc).astimezone().isoformat()
    saved_data[timestamp] = stat
    with open(args.stat_file, 'w') as f:
        f.write(json.dumps(saved_data, indent=4, sort_keys=True))


unknown_statuses = set(stat.keys()) - set(KNOWN_STATUSES)

x = PrettyTable()

x.field_names = ['Status'] + KNOWN_PRIORITIES + ['Total']

x.align['Status'] = "c"
for p in KNOWN_PRIORITIES:
    x.align[p] = "r"
x.align['Total'] = "r"

for status in KNOWN_STATUSES + list(unknown_statuses):
    if status == 'Summary':
        continue
    count = stat[status]
    d = [status]
    for p in KNOWN_PRIORITIES:
        d.append(count.get(p, 0))
    d.append(count['Total'])
    x.add_row(d)

# Summary line
d = []
d.append('Summary')
d += [stat['Summary'][p] for p in KNOWN_PRIORITIES]
d.append(stat['Summary']['Total'])
x.add_row(d)

print(x)
