import os
import sqlite3
import datetime
import hashlib
import platform
from flask import Flask, render_template_string, request, redirect, session

# Танзимоти роҳ (Path) барои Android
# Ин қисм муҳим аст, то барнома базаи маълумотро дар дохили APK гум накунад
base_dir = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(base_dir, 'dukon_v7.db')
CHEK_FOLDER = os.path.join(base_dir, 'cheks')

app = Flask(__name__)
app.secret_key = 'mafoza_ultimate_secure_2026'

# Сохтани папкаи чекҳо агар набошад
if not os.path.exists(CHEK_FOLDER):
    os.makedirs(CHEK_FOLDER)

# --- БАХШИ МУҲОФИЗАТ (LICENSE SYSTEM) ---
def get_device_id():
    # ID-и ягона дар асоси телефон
    device_info = platform.node() + platform.machine() + "MAFOZA_SECURE_v7"
    return hashlib.sha256(device_info.encode()).hexdigest()[:8].upper()

# ТАНЗИМОТИ ЛИЦЕНЗИЯ
AUTHORIZED_ID = "322C3062"  # ID-и телефони муштарӣ
EXPIRY_DATE = "2027-01-22"  # То кадом вақт кор мекунад

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

# Эҷоди базаи маълумот
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
        body { font-family: sans-serif; background: #f0f2f5; padding: 10px; text-align: center; }
        .card { background: white; padding: 15px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 15px; }
        .btn { display: block; width: 100%; padding: 15px; margin: 8px 0; border: none; border-radius: 8px; color: white; font-weight: bold; text-decoration: none; cursor: pointer; font-size: 16px; }
        .b-g { background: #27ae60; } .b-b { background: #2980b9; } .b-r { background: #c0392b; } .b-o { background: #e67e22; } .b-nfc { background: #00d2d3; }
        input { width: 100%; padding: 12px; margin: 8px 0; border: 1px solid #ccc; border-radius: 6px; box-sizing: border-box; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { border-bottom: 1px dashed #ccc; padding: 10px; text-align: left; }
        .receipt { border: 2px solid #000; padding: 20px; background: #fff; max-width: 320px; margin: auto; text-align: left; font-family: monospace; }
    </style>
</head>
<body>
    {{ content | safe }}
</body>
</html>
'''

@app.before_request
def security_check():
    if request.endpoint in ['blocked', 'static']: return
    my_id = get_device_id()
    today = datetime.date.today().isoformat()
    if my_id != AUTHORIZED_ID or today > EXPIRY_DATE:
        return redirect('/blocked')

@app.route('/blocked')
def blocked():
    my_id = get_device_id()
    return f'''
    <div style="text-align:center; padding:50px; font-family:sans-serif;">
        <h1 style="color:red;">🚫 ДАСТРАСӢ МАҲДУД АСТ</h1>
        <p>ID-и ин телефон: <b>{my_id}</b></p>
        <p>Мӯҳлати иҷозатнома: {EXPIRY_DATE}</p>
    </div>'''

@app.route('/')
def home():
    session['cart'] = []
    c = f'''<h2>🏪 MAFOZA PREMIUM</h2>
    <div class="card">
        <a href="/k" class="btn b-g">💳 КАССА (ФУРӮШ)</a>
        <a href="/scan_qabul" class="btn b-o">📷 ҚАБУЛИ БОР</a>
        <a href="/s" class="btn b-b">📦 СКЛАД</a>
        <a href="/view_cheks" class="btn b-b" style="background:#7f8c8d">📂 АРХИВ</a>
        <a href="/h" class="btn b-r">📊 ҲИСОБОТ</a>
    </div>'''
    return render_template_string(HTML_BASE, content=c)

@app.route('/k', methods=['GET', 'POST'])
def kassa():
    if 'cart' not in session: session['cart'] = []
    msg = ""
    if request.method == 'POST':
        barcode = request.form.get('b')
        conn = get_db()
        t = conn.execute('SELECT * FROM ambor WHERE barcode=?', (barcode,)).fetchone()
        conn.close()
        if t:
            cart = session['cart']
            found = False
            for item in cart:
                if item['barcode'] == barcode:
                    item['qty'] += 1
                    found = True; break
            if not found: cart.append({'barcode': barcode, 'nom': t['nom'], 'narh': t['narh'], 'qty': 1})
            session['cart'] = cart
        else: msg = "❌ Мол нест!"

    total = sum(i['narh'] * i['qty'] for i in session['cart'])
    rows = "".join([f"<tr><td>{i['nom']}</td><td>{i['qty']} x {i['narh']}</td></tr>" for i in session['cart']])
    
    c = f'''<div class="card"><h3>💳 Касса</h3><div id="reader"></div>
    <form id="f" method="post"><input type="hidden" id="i" name="b"></form>
    <p style="color:red">{msg}</p>
    <table>{rows}</table>
    <h3 style="text-align:right">ҶАМЪ: {total} c.</h3>
    <button onclick="window.location.href='intent://pay#Intent;scheme=alifpay;package=tj.alif.mobi;end'" class="btn b-nfc">💳 ПАРДОХТИ NFC</button>
    <a href="/checkout" class="btn b-g">✅ ТАСДИҚ ВА ЧЕК</a>
    <a href="/" class="btn b-r">БЕКОР</a>
    </div><script>
        function onScanSuccess(t){{ document.getElementById("i").value=t; document.getElementById("f").submit(); }}
        let s=new Html5QrcodeScanner("reader",{{fps:10,qrbox:200}}); s.render(onScanSuccess);
    </script>'''
    return render_template_string(HTML_BASE, content=c)

@app.route('/checkout')
def checkout():
    if not session.get('cart'): return redirect('/')
    conn = get_db()
    now = datetime.datetime.now()
    file_name = now.strftime("%Y%m%d_%H%M%S") + ".txt"
    total = sum(i['narh'] * i['qty'] for i in session['cart'])
    receipt_text = f"--- ЧЕКИ МАҒОЗА ---\nСана: {now.strftime('%Y-%m-%d %H:%M')}\n------------------\n"
    for i in session['cart']:
        sub = i['narh'] * i['qty']
        receipt_text += f"{i['nom']}\n{i['qty']} x {i['narh']} = {sub}\n"
        for _ in range(i['qty']):
            conn.execute('INSERT INTO furushot (nom, narh, sana) VALUES (?,?,?)', (i['nom'], i['narh'], now.strftime('%Y-%m-%d')))
        conn.execute('UPDATE ambor SET miqdor = miqdor - ? WHERE barcode = ?', (i['qty'], i['barcode']))
    receipt_text += f"------------------\nҶАМЪ: {total} сомонӣ\n"
    with open(os.path.join(CHEK_FOLDER, file_name), "w", encoding="utf-8") as f:
        f.write(receipt_text)
    conn.commit(); conn.close(); session['cart'] = []
    return redirect(f'/read_chek/{file_name}')

@app.route('/read_chek/<filename>')
def read_chek(filename):
    path = os.path.join(CHEK_FOLDER, filename)
    with open(path, "r", encoding="utf-8") as f: content = f.read()
    qr = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=Check_{filename}"
    res = f'''<div class="receipt"><pre>{content}</pre><div style="text-align:center"><img src="{qr}" width="150"></div></div>
    <br><a href="/view_cheks" class="btn b-b">АРХИВ</a><button onclick="window.print()" class="btn b-g">ЧОП</button>'''
    return render_template_string(HTML_BASE, content=res)

@app.route('/view_cheks')
def view_cheks():
    files = sorted(os.listdir(CHEK_FOLDER), reverse=True)
    list_h = "<h3>📂 Архив</h3><div class='card'><ul>"
    for f in files:
        list_h += f"<li><a href='/read_chek/{f}' style='text-decoration:none; color:#2980b9;'>📄 {f}</a></li>"
    list_h += "</ul></div><a href='/' class='btn b-r'>БОЗГАШТ</a>"
    return render_template_string(HTML_BASE, content=list_h)

@app.route('/scan_qabul')
def scan_qabul():
    c = '''<div class="card"><h3>📷 Қабули Бор</h3><div id="reader"></div>
    <script>
        function onScanSuccess(t){ window.location.href = "/qabul_form?b=" + t; }
        let s = new Html5QrcodeScanner("reader", {fps:10, qrbox:250});
        s.render(onScanSuccess);
    </script><a href="/" class="btn b-r">БОЗГАШТ</a></div>'''
    return render_template_string(HTML_BASE, content=c)

@app.route('/qabul_form', methods=['GET', 'POST'])
def qabul_form():
    barcode = request.args.get('b') or request.form.get('b')
    conn = get_db()
    t = conn.execute('SELECT * FROM ambor WHERE barcode=?', (barcode,)).fetchone()
    if request.method == 'POST':
        conn.execute('INSERT OR REPLACE INTO ambor VALUES (?,?,?,?)', (barcode, request.form['n'], request.form['p'], (t['miqdor'] if t else 0) + int(request.form['q'])))
        conn.commit(); conn.close()
        return redirect('/s')
    conn.close()
    c = f'''<div class="card"><h3>Маълумот</h3><form method="post">
    <input name="b" value="{barcode}" readonly>
    <input name="n" value="{t['nom'] if t else ''}" placeholder="Ном" required>
    <input name="p" value="{t['narh'] if t else ''}" placeholder="Нарх" required>
    <input name="q" type="number" placeholder="Миқдор" required autofocus>
    <button type="submit" class="btn b-g">ЗАХИРА</button></form></div>'''
    return render_template_string(HTML_BASE, content=c)

@app.route('/s')
def sklad():
    conn = get_db(); rows = conn.execute('SELECT * FROM ambor').fetchall(); conn.close()
    t = "<table><tr><th>Ном</th><th>Адад</th></tr>" + "".join([f"<tr><td>{r['nom']}</td><td>{r['miqdor']}</td></tr>" for r in rows]) + "</table>"
    return render_template_string(HTML_BASE, content=f'<div class="card"><h3>📦 Склад</h3>{t}<br><a href="/" class="btn b-b">БОЗГАШТ</a></div>')

@app.route('/h')
def hisobot():
    conn = get_db()
    total = conn.execute('SELECT SUM(narh) FROM furushot WHERE sana=?', (datetime.date.today().isoformat(),)).fetchone()[0]
    conn.close()
    return render_template_string(HTML_BASE, content=f'<div class="card"><h3>📊 Фурӯши имрӯз</h3><h2 style="color:green">{total or 0} с.</h2><a href="/" class="btn b-b">БОЗГАШТ</a></div>')

if __name__ == '__main__':
    # Дар APK бояд порти 5000 ва хости 0.0.0.0 бошад
    app.run(host='0.0.0.0', port=5000, debug=False)
