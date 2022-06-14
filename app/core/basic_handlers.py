from app import db, cache
from sqlalchemy import asc, desc
from sqlalchemy.sql import func


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

    if 'tags' in kwargs:
        for tag_value in kwargs['tags']:
            tag = cls.tags.property.mapper.class_(obj.id, tag_value)
            db.session.add(tag)
        db.session.flush()

    if 'uploads' in kwargs:
        for upload_dict in kwargs['uploads']:
            upload = cls.uploads.property.mapper.class_(obj.id, **upload_dict)
            db.session.add(upload)
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
        update_meta(obj, **kwargs)

    if 'tags' in kwargs:
        update_tags(obj, kwargs['tags'])

    cache.set('%s.%s' % (cls.__tablename__, obj.id), obj)
    return obj


def delete(obj):
    cls = obj.__class__

    obj.delete()
    db.session.add(obj)
    db.session.flush()

    cache.delete('%s.%s' % (cls.__tablename__, obj.id))
    return True


def select_all(cls, **kwargs):
    query = cls.query.filter(*[
        getattr(cls, k).in_(v) if isinstance(v, list) else getattr(cls, k) == v
        for k, v in kwargs.items() if k not in ['order_by', 'order', 'limit', 'offset']
    ])

    if 'order_by' in kwargs and kwargs['order'] == 'asc':
        query = query.order_by(asc(kwargs['order_by']))

    elif 'order_by' in kwargs and kwargs['order'] == 'desc':
        query = query.order_by(desc(kwargs['order_by']))

    else:
        query = query.order_by(desc('id'))

    if 'limit' in kwargs:
        query = query.limit(kwargs['limit'])
    else:
        query = query.limit(None)

    if 'offset' in kwargs:
        query = query.offset(kwargs['offset'])
    else:
        query = query.offset(0)
    
    objs = query.all()
    for obj in objs:
        cache.set('%s.%s' % (cls.__tablename__, obj.id), obj)

    return objs


def select_sum(cls, field, **kwargs):
    query = db.session.query(func.sum(getattr(cls, field)))
    for key in kwargs:
        query = query.filter(getattr(cls, key) == kwargs[key])
    return query.one()[0]


def select_count(cls, **kwargs):
    query = db.session.query(func.count(getattr(cls, 'id')))
    for key in kwargs:
        query = query.filter(getattr(cls, key) == kwargs[key])
    return query.one()[0]


def update_meta(obj, **kwargs):
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


def update_tags(obj, tags_data):
    cls = obj.__class__
    Tag = cls.tags.property.mapper.class_

    for tag in obj.tags:
        db.session.delete(tag)

    for tag_value in tags_data:
        tag_value = tag_value.strip().lower()
        tag = Tag.query.filter_by(**{Tag.parent: obj.id, 'tag_value': tag_value}).first()
        if not tag and tag_value:
            tag = Tag(obj.id, tag_value)
            db.session.add(tag)

    db.session.flush()
    cache.set('%s.%s' % (cls.__tablename__, obj.id), obj)
