import datetime
import macos # https://github.com/tandav/dotfiles/blob/master/bin/macos.py
import json
import subprocess
import statistics

n_tabs, n_windows = macos.n_tabs(n_windows=True)

with open('n_tabs.csv') as fd:
    tabs = [int(line.split(',')[1]) for line in fd]
n_tabs_old = tabs[-1]

if n_tabs != n_tabs_old:
    tabs.append(n_tabs)
    now = datetime.datetime.now()

    with open('n_tabs.csv', 'a') as fd:
        print(f"{now.strftime('%Y-%m-%d %H:%M:%S')}", n_tabs, sep=',', file=fd)

    with open('/Users/tandav/Downloads/n_tabs_json/n_tabs.json', 'w') as fd:
        json.dump({
            'n_tabs' : n_tabs,
            'n_windows': n_windows,
            'updated_at': int(now.timestamp() * 1000),
            'max': max(tabs),
            'min': min(tabs),
            'mean': int(statistics.mean(tabs)),
            'std': int(statistics.stdev(tabs)),
            'median': int(statistics.median(tabs)),
        }, fd)
        
    subprocess.run(('sh', 'update.sh'), cwd='/Users/tandav/Downloads/n_tabs_json')
    # macos.notification(text=f'{n_tabs}', title='n_tabs')
