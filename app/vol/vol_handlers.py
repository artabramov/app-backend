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


def vol_update(vol, **kwargs):
    for key in [x for x in kwargs if x != 'vol_meta']:
        value = kwargs[key]
        setattr(vol, key, value)
    db.session.add(vol)
    db.session.flush()

    if 'vol_meta' in kwargs:
        for meta_key in kwargs['vol_meta']:
            meta_value = kwargs['vol_meta'][meta_key]

            vol_meta = VolMeta.query.filter_by(vol_id=vol.id, meta_key=meta_key).first()
            if vol_meta and meta_value:
                vol_meta.meta_value = meta_value
                vol_meta.deleted = 0
                db.session.add(vol_meta)

            elif vol_meta and not meta_value:
                db.session.delete(vol_meta)

            else:
                vol_meta = VolMeta(vol.id, meta_key, meta_value)
                db.session.add(vol_meta)

        db.session.flush()

    cache.set('vol.%s' % (vol.id), vol)
    return vol


def vol_select(**kwargs):
    vol = None

    if 'id' in kwargs and len(kwargs) == 1:
        vol = cache.get('vol.%s' % (kwargs['id']))

    if not vol:
        vol = Vol.query.filter_by(**kwargs).first()

    if vol:
        cache.set('vol.%s' % (vol.id), vol)

    return vol
