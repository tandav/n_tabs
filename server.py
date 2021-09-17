from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import datetime
import json


def ago(e):
    # e: pass timedelta between timestamps in 1579812524 format
    e *= 1000 # convert to 1579812524000 format
    t = round(e / 1000)
    n = round(t /   60)
    r = round(n /   60)
    o = round(r /   24)
    i = round(o /   30)
    a = round(i /   12)
    if   e <  0: return              'just now'
    elif t < 10: return              'just now'
    elif t < 45: return str(t) + ' seconds ago'
    elif t < 90: return          'a minute ago'
    elif n < 45: return str(n) + ' minutes ago'
    elif n < 90: return           'an hour ago'
    elif r < 24: return str(r) +   ' hours ago'
    elif r < 36: return             'a day ago'
    elif o < 30: return str(o) +    ' days ago'
    elif o < 45: return           'a month ago'
    elif i < 12: return str(i) +  ' months ago'
    elif i < 18: return            'a year ago'
    else:        return str(a) +   ' years ago'

app = FastAPI()
tabs = {
    'n_tabs': None, 'n_windows': None, 'updated_at': int(datetime.datetime.now().timestamp() * 1000),
    'max': None, 'min': None, 'mean': None, 'std': None, 'median': None,
    'n': None, 'hosts': None,
}

@app.get('/', response_class=HTMLResponse)
def root():
    return f'''
    <h1>How many tabs are opened right now?</h1>
    <div class='big_number', id='n_tabs'>{tabs['n_tabs']}</div>
    <div id='stats'>min={tabs['min']} max={tabs['max']} mean={tabs['mean']} std={tabs['std']} median={tabs['median']} n={tabs['n']}</div>
    
    <h1>How many browser windows?</h1>
    <div class='big_number', id='n_windows'>{tabs['n_windows']}</div>
    
    <div id='updated'>updated: {ago(int(datetime.datetime.now().timestamp() * 1000) - tabs['updated_at'])}</div>
    <h3>Hosts stats:</h3>
    <pre id='hosts'>{json.dumps(tabs['hosts'])}</pre>
    <a href='https://github.com/tandav/n_tabs'>github</a>
    ''' + '''
    <style>
    .big_number {
        font-size: 36pt;
    }
    pre {
        background-color: rgba(0, 0, 0, 0.05);
    }
    </style>
    '''
