from app import app
import os, qrcode

QRCODES_REF = app.config['QRCODES_REF']
QRCODES_BASE_DIR = app.config['APP_BASE_DIR'] + app.config['QRCODES_DIR']


def qrcode_make(totp_key, user_login):
    qr = qrcode.make(QRCODES_REF % (totp_key, user_login))
    qr.save(QRCODES_BASE_DIR + totp_key + '.png')


def qrcode_remove(totp_key):
    if os.path.isfile(QRCODES_BASE_DIR % totp_key):
        os.remove(QRCODES_BASE_DIR + totp_key + '.png')
