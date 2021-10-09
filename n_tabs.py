import datetime
import psutil
import macos # https://github.com/tandav/dotfiles/blob/master/bin/macos.py
import json
import sqlite3
import subprocess
import collections
import requests
from urllib.parse import urlparse
from pathlib import Path

DATABASE_FILE = 'n_tabs.db'

def sqlite_connect():
    conn = sqlite3.connect(DATABASE_FILE, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    return conn

def create_if_not_exists():
    if not Path(DATABASE_FILE).exists():
        conn = sqlite_connect()
        c = conn.cursor()
        c.execute('''
        CREATE TABLE tabs (timestamp timestamp primary key, n_tabs integer)
        ''')
        conn.commit()
        conn.close()
        print('initialized database file', DATABASE_FILE)


def insert(timestamp: datetime.datetime, n_tabs: int) -> None:
    conn = sqlite_connect()
    c = conn.cursor()
    c.execute("insert into tabs values (?, ?)", (timestamp, n_tabs))
    conn.commit()
    conn.close()
    print(f'inserted row, {n_tabs=}')


def get_n_tabs_history():
    conn = sqlite_connect()
    c = conn.cursor()
    c.execute("select n_tabs from tabs")
    return [n for n, in c.fetchall()]


def tabs_status(now):
    n_tabs = 0
    n_windows = 0
    hosts = collections.Counter()
    whitelist = set(open('whitelist.txt').read().split())
    tabs = macos.tabs(browser='Brave Browser')

    for window in tabs:
        n_windows += 1
        for title, url in window:
            n_tabs += 1
            host = urlparse(url).hostname
            if host not in whitelist:
                host = 'etc'
            hosts[host] += 1

    n_tabs_history = get_n_tabs_history()
    n_tabs_old = n_tabs_history[-1]

    if n_tabs != n_tabs_old:
        n_tabs_history.append(n_tabs)
        insert(now, n_tabs)

    with sqlite3.connect(
        DATABASE_FILE,
        detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
    ) as con:
        con.enable_load_extension(True)
        con.load_extension('./stats.dylib')  # https://github.com/nalgeon/sqlean/blob/main/docs/stats.md
        max_, min_, mean, std, median, n = con.cursor().execute('''
        select max(n_tabs)
             , min(n_tabs)
             , cast(avg(n_tabs) as int)
             , cast(stddev(n_tabs) as int)
             , median(n_tabs)
             , count(1)
          from tabs
        ''').fetchone()

    return {
        'n_tabs': n_tabs,
        'n_windows': n_windows,
        'max': max_,
        'min': min_,
        'mean': mean,
        'std': std,
        'median': median,
        'n': n,
        'hosts': hosts,
    }

def battery_status():
    _ = (
        subprocess
        .check_output(('ioreg', '-rn', 'AppleSmartBattery'), text=True)
        .splitlines()
    )
    for line in _:
        if '"MaxCapacity" = ' in line:
            MaxCapacity = int(line.split('=')[1])
        if '"CycleCount" = ' in line:
            CycleCount = int(line.split('=')[1])

    a, b = subprocess.check_output(('pmset', '-g', 'batt'), text=True).splitlines()
    b = b.split('\t')[1]
    return {
        'current_charge': f"{a} {b}",
        'max_capacity': MaxCapacity,
        'cycle_count': CycleCount,
    }


def memory_used_gb():
    """https://github.com/orefalo/free/blob/master/functions/free.fish"""
    mem = {}
    page_size = 4096  # bytes

    for line in subprocess.check_output(('vm_stat',), text=True).splitlines()[1:]:
        k, v = line.rsplit(maxsplit=1)
        v = int(v.strip('.'))
        mem[k] = v
    # Activity Monitor values for "Memory Used"
    return (
        mem['Anonymous pages:'] +  # App Memory
        mem['Pages wired down:'] +  # Wired Memory
        mem['Pages occupied by compressor:']  # Compressed
     ) * page_size / 2 ** 30

def uptime_status():
    x = subprocess.check_output(('uptime',), text=True).strip().split()
    return {
        'uptime': ' '.join(x[2:4]).strip(','),
        'load': [round(float(i) / psutil.cpu_count() * 100, 2) for i in x[-3:]],
        'memory_used': f'{round(memory_used_gb(), 2)} GB',
        'swap_used': f'{round(psutil.swap_memory().used / 2 ** 30, 2)} GB',
    }

def network_status():
    return {
        'lan_ip': json.loads(subprocess.check_output(('system_profiler', '-json', 'SPNetworkDataType')))['SPNetworkDataType'][0]['ip_address'][0],
    }

def os_status():
    return json.loads(subprocess.check_output(('system_profiler', '-json', 'SPSoftwareDataType')))['SPSoftwareDataType'][0]['os_version']

def backup_status():
    with sqlite3.connect(
        'file:/Users/tandav/Library/Application Support/Vorta/settings.db?mode=ro',
        uri=True,
        detect_types=sqlite3.PARSE_COLNAMES,
    ) as con:
        timestamp, duration, size = con.cursor().execute('''
        select time as "latest_backup [timestamp]"
             , cast(round(duration) as int)
             , round(size / 1e6, 1)
        from archivemodel
        order by time desc
        ''').fetchone()
        timestamp = int(timestamp.timestamp())
        return {'timestamp': timestamp, 'duration': duration, 'size': size}

def main() -> int:
    now = datetime.datetime.now()
    data = {
        'updated': int(now.timestamp()),
        'tabs': tabs_status(now),
        'battery': battery_status(),
        'uptime': uptime_status(),
        'network': network_status(),
        'os_version': os_status(),
        'latest_backup': backup_status(),
    }
    requests.post('https://tandav.me:5002', json=data)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
