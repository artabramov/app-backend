from app import app
import os, qrcode

QRCODE_REF = app.config['QRCODE_REF']
QRCODE_PATH = app.config['QRCODE_PATH']


def qrcode_make(totp_key, user_login):
    qr = qrcode.make(QRCODE_REF % (totp_key, user_login))
    qr.save(QRCODE_PATH % totp_key)


def qrcode_remove(totp_key):
    if os.path.isfile(QRCODE_PATH % totp_key):
        os.remove(QRCODE_PATH % totp_key)
