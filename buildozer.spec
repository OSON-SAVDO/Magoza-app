[app]

# Номи барнома, ки муштарӣ дар телефони худ мебинад
title = Magoza POS

# Номи пакет (бе фосила ва ҳарфҳои калон)
package.name = magozapos

# Домен
package.domain = org.mafoza

# Суроғаи код
source.dir = .

# Намуди файлҳо барои дохил кардан
source.include_exts = py,png,jpg,kv,atlas,db,txt

# Версияи барнома
version = 1.0

# КИТОБХОНАҲО (Муҳимтарин қисм барои пешгирии хатогии сурх)
requirements = python3, flask, sqlite3, jinja2, werkzeug, itsdangerous, click, markupsafe

# Иконаи барнома (агар файл бо номи icon.png дошта бошед)
icon.filename = %(source.dir)s/icon.png

# Ориентацияи экран
orientation = portrait

# Иҷозатҳои Android барои камера ва интернет
android.permissions = INTERNET, CAMERA, NFC, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE

# Танзимоти API
android.api = 31
android.minapi = 21
android.sdk = 31

# Навъи экран
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1
