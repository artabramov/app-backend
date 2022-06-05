from app import db, cache
from sqlalchemy import asc, desc


def insert(cls, **kwargs):
    obj = cls(**{k: kwargs[k] for k in kwargs if k not in ['meta', 'tags']})
    db.session.add(obj)
    db.session.flush()

    if 'meta' in kwargs:
        for meta_key in kwargs['meta']:
            meta_value = kwargs['meta'][meta_key]
            meta = cls.meta.property.mapper.class_(obj.id, meta_key, meta_value)
            db.session.add(meta)
        db.session.flush()

    cache.set('%s.%s' % (cls.__tablename__, obj.id), obj)
    return obj


def select(cls, **kwargs):
    obj = None

    if 'id' in kwargs and len(kwargs) == 1:
        obj = cache.get('%s.%s' % (cls.__tablename__, kwargs['id']))

    if not obj:
        obj = cls.query.filter_by(**kwargs).first()

    if obj:
        cache.set('%s.%s' % (cls.__tablename__, obj.id), obj)

    return obj


def update(obj, **kwargs):
    cls = obj.__class__

    for key in [x for x in kwargs if x not in ['meta', 'tags']]:
        value = kwargs[key]
        setattr(obj, key, value)
    db.session.add(obj)
    db.session.flush()

    if 'meta' in kwargs:
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
    return obj


def delete(obj):
    cls = obj.__class__

    obj.delete()
    db.session.add(obj)
    db.session.flush()

    cache.delete('%s.%s' % (cls.__tablename__, obj.id))
    return True
