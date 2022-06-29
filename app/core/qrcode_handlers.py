from app import app
import os, qrcode

QRCODES_REF = app.config['QRCODES_REF']
QRCODES_PATH = app.config['QRCODES_PATH']
QRCODES_SIZE = app.config['QRCODES_SIZE']
QRCODES_BORDER = app.config['QRCODES_BORDER']
QRCODES_COLOR = app.config['QRCODES_COLOR']
QRCODES_BACKGROUND = app.config['QRCODES_BACKGROUND']


def qrcode_make(totp_key, user_login):
    #qr = qrcode.make(QRCODES_REF % (totp_key, user_login))
    #qr.save(QRCODES_PATH + totp_key + '.png')

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=QRCODES_SIZE,
        border=QRCODES_BORDER,
    )
    qr.add_data(QRCODES_REF % (totp_key, user_login))
    qr.make(fit=True)
    
    img = qr.make_image(fill_color=QRCODES_COLOR, back_color=QRCODES_BACKGROUND)
    img.save(QRCODES_PATH + totp_key + '.png')


def qrcode_remove(totp_key):
    if os.path.isfile(QRCODES_PATH + totp_key + '.png'):
        os.remove(QRCODES_PATH + totp_key + '.png')
