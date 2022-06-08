from app import db, cache


def reset_meta(obj, **kwargs):
    cls = obj.__class__
    Meta = cls.meta.property.mapper.class_

    for meta_key in kwargs['meta']:
        meta_value = kwargs['meta'][meta_key]
        meta = Meta.query.filter_by(**{Meta.parent: obj.id, 'meta_key': meta_key}).first()
        if meta and meta_value:
            meta.meta_value = meta_value
            meta.deleted = 0
            db.session.add(meta)

        elif meta and not meta_value:
            db.session.delete(meta)

        elif not meta and meta_value:
            meta = Meta(obj.id, meta_key, meta_value)
            db.session.add(meta)

    db.session.flush()

    cache.set('%s.%s' % (cls.__tablename__, obj.id), obj)
