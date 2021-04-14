import datetime
import macos
import json
import subprocess

n_tabs = macos.n_tabs()

with open('n_tabs.csv') as fd:
    for line in fd:
        pass
    n_tabs_old = int(line.split(',')[1])

if n_tabs != n_tabs_old:
    now = datetime.datetime.now()

    with open('n_tabs.csv', 'a') as fd:
        print(f"{now.strftime('%Y-%m-%d %H:%M:%S')}", n_tabs, sep=',', file=fd)

    with open('/Users/tandav/Downloads/n_tabs_json/n_tabs.json', 'w') as fd:
        json.dump({'n_tabs' : n_tabs, 'updated_at': int(now.timestamp() * 1000)}, fd)
        
    subprocess.run(('sh', 'update.sh'), cwd='/Users/tandav/Downloads/n_tabs_json')
    # macos.notification(text=f'{n_tabs}', title='n_tabs')
