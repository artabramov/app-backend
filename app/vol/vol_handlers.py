from app.vol.vol import Vol
from app.vol.vol_meta import VolMeta
from app import db, cache


def vol_insert(user_id, vol_title, vol_meta=None):
    vol = Vol(user_id, vol_title)
    db.session.add(vol)
    db.session.flush()

    if vol_meta:
        for meta_key in vol_meta:
            meta_value = vol_meta[meta_key]
            meta = VolMeta(vol.id, meta_key, meta_value)
            db.session.add(meta)
        db.session.flush()

    cache.set('vol.%s' % (vol.id), vol)
    return vol
