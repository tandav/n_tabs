import datetime
import macos # https://github.com/tandav/dotfiles/blob/master/bin/macos.py
import json
import subprocess
import statistics
import collections
from urllib.parse import urlparse

whitelist = set(open('whitelist.txt').read().split())

tabs = macos.tabs()

n_tabs = 0
n_windows = 0
hosts = collections.Counter()

for window in tabs:
    n_windows += 1
    for title, url in window:
        n_tabs += 1
        host = urlparse(url).hostname
        if host not in whitelist:
            host = 'etc'
        hosts[host] += 1


with open('n_tabs.csv') as fd:
    n_tabs_history = [int(line.split(',')[1]) for line in fd]
n_tabs_old = n_tabs_history[-1]

if n_tabs != n_tabs_old:
    n_tabs_history.append(n_tabs)
    now = datetime.datetime.now()

    with open('n_tabs.csv', 'a') as fd:
        print(f"{now.strftime('%Y-%m-%d %H:%M:%S')}", n_tabs, sep=',', file=fd)

    with open('/Users/tandav/Downloads/n_tabs_json/n_tabs.json', 'w') as fd:
        json.dump({
            'n_tabs': n_tabs,
            'n_windows': n_windows,
            'updated_at': int(now.timestamp() * 1000),
            'max': max(n_tabs_history),
            'min': min(n_tabs_history),
            'mean': int(statistics.mean(n_tabs_history)),
            'std': int(statistics.stdev(n_tabs_history)),
            'median': int(statistics.median(n_tabs_history)),
            'hosts': hosts,
        }, fd)

    subprocess.run(('sh', 'update.sh'), cwd='/Users/tandav/Downloads/n_tabs_json')
