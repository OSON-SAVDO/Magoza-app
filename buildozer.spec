[app]

# Номи барнома, ки дар телефон пайдо мешавад
title = Magoza POS

# Номи пакет (бояд бе ҳарфҳои калон ва бе фосила бошад)
package.name = magozapos

# Домени барнома
package.domain = org.mafoza

# Папкае, ки код дар онҷост
source.dir = .

# Намуди файлҳое, ки бояд ба APK дохил шаванд
source.include_exts = py,png,jpg,kv,atlas,db,txt

# Версияи барнома
version = 1.0

# Китобхонаҳои лозимӣ ( Flask ва дигар модулҳо)
requirements = python3,flask,sqlite3,hashlib,werkzeug,jinja2,itsdangerous,click

# Нишони барнома (агар дошта бошед, номашро инҷо нависед, вагарна холи монед)
# icon.filename = %(source.dir)s/icon.png

# Ориентацияи экран (танҳо амудӣ)
orientation = portrait

# Иҷозатҳои Android (Permission)
android.permissions = INTERNET, CAMERA, NFC, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE

# (Option) Агар барномаи шумо WebView-ро талаб кунад
android.api = 31
android.minapi = 21
android.sdk = 31

# Навъи сохтмон
fullscreen = 0

[buildozer]
# Дараҷаи гузоришдиҳӣ (2 барои дидани хатогиҳо)
log_level = 2
warn_on_root = 1
