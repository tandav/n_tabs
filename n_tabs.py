import datetime
import macos

n_tabs = macos.n_tabs()

with open('n_tabs.csv') as fd:
    for line in fd:
        pass
    n_tabs_old = int(line.split(',')[1])

if n_tabs != n_tabs_old:
    with open('n_tabs.csv', 'a') as fd:
        print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", n_tabs, sep=',', file=fd)
    # macos.notification(text=f'{n_tabs}', title='n_tabs')
