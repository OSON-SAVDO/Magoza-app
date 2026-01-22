import os
import sqlite3
import datetime
import hashlib
import platform
from flask import Flask, render_template_string, request, redirect, session

# ==========================================
# ТАНЗИМОТИ ОСОН (ИНҶОРО ИВАЗ КУНЕД)
NOM_I_DUKON = "МАҒОЗАИ ХУШҚАДАМ"  # <--- Номи мағозаро инҷо иваз кунед
AUTHORIZED_ID = "322C3062"       # ID-и телефони муштарӣ
EXPIRY_DATE = "2050-01-22"       # Мӯҳлати иҷозатнома
# ==========================================

base_dir = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(base_dir, 'dukon_v7.db')
CHEK_FOLDER = os.path.join(base_dir, 'cheks')

app = Flask(__name__)
app.secret_key = 'mafoza_ultimate_secure_2026'

if not os.path.exists(CHEK_FOLDER):
    os.makedirs(CHEK_FOLDER)

def get_device_id():
    device_info = platform.node() + platform.machine() + "MAFOZA_SECURE_v7"
    return hashlib.sha256(device_info.encode()).hexdigest()[:8].upper()

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

with get_db() as conn:
    conn.execute('CREATE TABLE IF NOT EXISTS ambor (barcode TEXT PRIMARY KEY, nom TEXT, narh REAL, miqdor INTEGER)')
    conn.execute('CREATE TABLE IF NOT EXISTS furushot (id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT, narh REAL, sana TEXT)')

HTML_BASE = '''
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <script src="https://unpkg.com/html5-qrcode"></script>
    <style>
        body { font-family: sans-serif; background: #f4f7f6; padding: 10px; text-align: center; }
        .card { background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .btn { display: block; width: 100%; padding: 15px; margin: 10px 0; border: none; border-radius: 10px; color: white; font-weight: bold; text-decoration: none; font-size: 18px; cursor: pointer; }
        .b-g { background: #2ecc71; } .b-b { background: #3498db; } .b-r { background: #e74c3c; } .b-o { background: #f39c12; }
        input { width: 100%; padding: 15px; margin: 10px 0; border: 1px solid #ddd; border-radius: 8px; }
        table { width: 100%; border-collapse: collapse; }
        td { padding: 10px; border-bottom: 1px solid #eee; text-align: left; }
    </style>
</head>
<body>{{ content | safe }}</body>
</html>
'''

@app.before_request
def security_check():
    if request.endpoint == 'blocked': return
    if get_device_id() != AUTHORIZED_ID or datetime.date.today().isoformat() > EXPIRY_DATE:
        return redirect('/blocked')

@app.route('/blocked')
def blocked():
    return f"<h1>Дастрасӣ маҳдуд аст</h1><p>ID: {get_device_id()}</p>"

@app.route('/')
def home():
    session['cart'] = []
    c = f'''<h2>🏪 {NOM_I_DUKON}</h2>
    <div class="card">
        <a href="/k" class="btn b-g">💳 КАССА</a>
        <a href="/scan_qabul" class="btn b-o">📷 ҚАБУЛ</a>
        <a href="/s" class="btn b-b">📦 СКЛАД</a>
        <a href="/h" class="btn b-r">📊 ҲИСОБОТ</a>
    </div>'''
    return render_template_string(HTML_BASE, content=c)

@app.route('/k', methods=['GET', 'POST'])
def kassa():
    if 'cart' not in session: session['cart'] = []
    if request.method == 'POST':
        barcode = request.form.get('b')
        conn = get_db()
        t = conn.execute('SELECT * FROM ambor WHERE barcode=?', (barcode,)).fetchone()
        if t:
            cart = session['cart']
            cart.append({'nom': t['nom'], 'narh': t['narh'], 'barcode': barcode})
            session['cart'] = cart
        conn.close()
    
    total = sum(i['narh'] for i in session['cart'])
    c = f'''<div class="card"><h3>Касса</h3><div id="reader"></div>
    <form id="f" method="post"><input type="hidden" id="i" name="b"></form>
    <table>{''.join([f"<tr><td>{i['nom']}</td><td>{i['narh']} c.</td></tr>" for i in session['cart']])}</table>
    <h4>Ҷамъ: {total} c.</h4>
    <a href="/checkout" class="btn b-g">ХАТМ</a>
    <a href="/" class="btn b-r">БОЗГАШТ</a>
    </div><script>
        function onScanSuccess(t){{ document.getElementById("i").value=t; document.getElementById("f").submit(); }}
        let s=new Html5QrcodeScanner("reader",{{fps:10,qrbox:250}}); s.render(onScanSuccess);
    </script>'''
    return render_template_string(HTML_BASE, content=c)

@app.route('/checkout')
def checkout():
    conn = get_db()
    for i in session['cart']:
        conn.execute('INSERT INTO furushot (nom, narh, sana) VALUES (?,?,?)', (i['nom'], i['narh'], datetime.date.today().isoformat()))
        conn.execute('UPDATE ambor SET miqdor = miqdor - 1 WHERE barcode = ?', (i['barcode'],))
    conn.commit(); conn.close(); session['cart'] = []
    return redirect('/')

@app.route('/scan_qabul')
def scan_qabul():
    c = '''<div class="card"><div id="reader"></div><script>
    function onScanSuccess(t){ window.location.href="/q?b="+t; }
    let s=new Html5QrcodeScanner("reader",{fps:10,qrbox:250}); s.render(onScanSuccess);
    </script></div>'''
    return render_template_string(HTML_BASE, content=c)

@app.route('/q', methods=['GET', 'POST'])
def qabul():
    b = request.args.get('b') or request.form.get('b')
    if request.method == 'POST':
        conn = get_db()
        conn.execute('INSERT OR REPLACE INTO ambor VALUES (?,?,?,?)', (b, request.form['n'], request.form['p'], request.form['q']))
        conn.commit(); conn.close()
        return redirect('/')
    return render_template_string(HTML_BASE, content=f'''<form method="post" class="card">
    <input name="b" value="{b}" readonly>
    <input name="n" placeholder="Номи мол">
    <input name="p" placeholder="Нарх">
    <input name="q" placeholder="Миқдор">
    <button type="submit" class="btn b-g">ЗАХИРА</button></form>''')

@app.route('/s')
def sklad():
    conn = get_db(); r = conn.execute('SELECT * FROM ambor').fetchall(); conn.close()
    rows = "".join([f"<tr><td>{i['nom']}</td><td>{i['miqdor']}</td></tr>" for i in r])
    return render_template_string(HTML_BASE, content=f"<h3>Склад</h3><table>{rows}</table><a href='/' class='btn b-b'>БОЗГАШТ</a>")

@app.route('/h')
def hisobot():
    conn = get_db()
    summa = conn.execute('SELECT SUM(narh) FROM furushot WHERE sana=?', (datetime.date.today().isoformat(),)).fetchone()[0]
    return render_template_string(HTML_BASE, content=f"<h2>Имрӯз: {summa or 0} c.</h2><a href='/' class='btn b-b'>БОЗГАШТ</a>")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
