#!/bin/bash -x

python launchpad-bugs-stat.py --stat-file data/neutron-bug-stats.json neutron
python launchpad-bugs-stat.py --stat-file data/horizon-bug-stats.json horizon

git add -u
git commit -m "Update bug stats of horizon and neutron"
