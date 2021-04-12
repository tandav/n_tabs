import subprocess
import datetime
import macos

js_code = '''\
let browser = Application('Google Chrome')
let n_tabs = 0
for (let i = 0; i < browser.windows.length; i++) {
    n_tabs += browser.windows[i].tabs.length
}
'''

cmd = 'osascript', '-l', 'JavaScript', '-e', js_code
n_tabs = int(subprocess.check_output(cmd, text=True).strip())


with open('n_tabs.csv') as fd:
    for line in fd:
        pass
    n_tabs_old = int(line.split(',')[1])

if n_tabs != n_tabs_old:
    with open('n_tabs.csv', 'a') as fd:
        print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", n_tabs, sep=',', file=fd)
    # macos.notification(text=f'{n_tabs}', title='n_tabs')
