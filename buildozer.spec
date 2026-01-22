[app]

# Номи барнома
title = Magoza POS

# Номи пакет
package.name = magozapos

# Домен
package.domain = org.mafoza

# Папкаи код
source.dir = .

# Файлҳое, ки ба APK дохил мешаванд
source.include_exts = py,png,jpg,kv,atlas,db,txt

# Версия
version = 1.0

# КИТОБХОНАҲО (Requirements) - ИН ҶОРО ДИҚҚАТ КУНЕД:
# Мо ҳамаи вобастагиҳои Flask-ро илова кардам
requirements = python3, flask, sqlite3, jinja2, werkzeug, itsdangerous, click, markupsafe, hostlist

# Ориентация
orientation = portrait

# Иҷозатномаҳои Android
android.permissions = INTERNET, CAMERA, NFC, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE

# Танзимоти API
android.api = 31
android.minapi = 21
android.sdk = 31

# Илова кардани хизматрасонии Flask
services = 

# Навъи экран
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1
