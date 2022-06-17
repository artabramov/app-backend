from app import app
import os, qrcode

QRCODES_REF = app.config['QRCODES_REF']
QRCODES_PATH = app.config['QRCODES_PATH']


def qrcode_make(totp_key, user_login):
    qr = qrcode.make(QRCODES_REF % (totp_key, user_login))
    qr.save(QRCODES_PATH + totp_key + '.png')


def qrcode_remove(totp_key):
    if os.path.isfile(QRCODES_PATH + totp_key + '.png'):
        os.remove(QRCODES_PATH + totp_key + '.png')
