from flask import g

from app import db, cache
from sqlalchemy import asc, desc, column
from sqlalchemy.sql import func

from app.models.upload import Upload
from app.models.comment import Comment
from app.models.post import Post
from app.models.volume import Volume
from app.models.user import User


def insert(cls, **kwargs):
    obj = cls(**{k: kwargs[k] for k in kwargs if k not in ['meta', 'tags']})
    db.session.add(obj)
    db.session.flush()

    if 'meta' in kwargs and kwargs['meta']:
        for meta_key in kwargs['meta']:
            meta_value = kwargs['meta'][meta_key]
            meta = cls.meta.property.mapper.class_(obj.id, meta_key, meta_value)
            db.session.add(meta)
        db.session.flush()

    if 'tags' in kwargs and kwargs['tags']:
        for tag_value in kwargs['tags']:
            tag = cls.tags.property.mapper.class_(obj.id, tag_value)
            db.session.add(tag)
        db.session.flush()

    recount(obj)
    return obj


def select(cls, **kwargs):
    obj = None

    if 'id' in kwargs and len(kwargs) == 1:
        obj = cache.get('%s.%s' % (cls.__tablename__, kwargs['id']))

    if not obj:
        #obj = cls.query.filter_by(**kwargs).first()
        obj = cls.query.filter(*[getattr(cls, k).in_(v) if isinstance(v, list) else getattr(cls, k) == v for k, v in kwargs.items()]).first()

    if obj:
        cache.set('%s.%s' % (cls.__tablename__, obj.id), obj)

    return obj


def update(obj, is_recounted=False, **kwargs):
    cls = obj.__class__

    for key in [x for x in kwargs if x not in ['meta', 'tags', 'is_recounted']]:
        value = kwargs[key]
        setattr(obj, key, value)

    db.session.merge(obj)
    db.session.flush()

    if 'meta' in kwargs:
        update_meta(obj, kwargs['meta'])

    if 'tags' in kwargs:
        update_tags(obj, kwargs['tags'])

    if not is_recounted:
        recount(obj)

    cache.delete('%s.%s' % (cls.__tablename__, obj.id))
    return obj


def delete(obj):
    db.session.delete(obj)
    db.session.flush()

    recount(obj)
    
    cache.clear()
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


def select_by_tag(cls, tag_value, **kwargs):
    Tag = cls.tags.property.mapper.class_
    parent = Tag._parent
    objs_ids = db.session.query(column(getattr(Tag, '_parent'))).filter(Tag.tag_value==tag_value).subquery()
    
    query = cls.query.filter(cls.id.in_(objs_ids))

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


def select_count_by_tag(cls, tag_value, **kwargs):
    Tag = cls.tags.property.mapper.class_
    parent = Tag._parent
    query = db.session.query(func.count(Tag.id)).filter(Tag.tag_value==tag_value)
    return query.one()[0]


def update_meta(obj, meta_data):
    cls = obj.__class__
    Meta = cls.meta.property.mapper.class_

    for meta_key in meta_data:
        meta_value = meta_data[meta_key]
        meta = Meta.query.filter_by(**{Meta._parent: obj.id, 'meta_key': meta_key}).first()
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
        tag = Tag.query.filter_by(**{Tag._parent: obj.id, 'tag_value': tag_value}).first()
        if tag_value:
            tag = Tag(obj.id, tag_value)
            db.session.add(tag)

    db.session.flush()


def _get_parent_data(obj):
    if obj.__class__ == Upload:
        return Comment, obj.comment_id

    elif obj.__class__ == Comment:
        return Post, obj.post_id

    elif obj.__class__ == Post:
        return Volume, obj.volume_id


def recount(obj):
    parent_cls, parent_id = _get_parent_data(obj)

    # comment
    if parent_cls == Comment:
        comment_id = parent_id
        comment = Comment.query.filter(Comment.id==comment_id).first()

    # post
    if parent_cls in [Comment, Post]:
        post_id = parent_id if parent_cls == Post else comment.post_id
        post = Post.query.filter(Post.id==post_id).first()

        if post:
            # ...
            post_comments_ids = db.session.query(Comment.id).filter(Comment.post_id==post.id).subquery()
            post_comments = Comment.query.filter(Comment.id.in_(post_comments_ids)).all()

            # ...
            post_comments_count = db.session.query(func.count(Comment.id)).filter(Comment.post_id==post.id).scalar()
            post_comments_sum = db.session.query(func.sum(Comment.comment_sum)).filter(Comment.post_id==post.id).scalar() or 0
            post_uploads_count = db.session.query(func.count(Upload.id)).filter(Upload.comment_id.in_(post_comments_ids)).scalar()
            post_uploads_size = db.session.query(func.sum(Upload.upload_size)).filter(Upload.comment_id.in_(post_comments_ids)).scalar() or 0

            # ...
            update(post, is_recounted=True, post_sum=post_comments_sum, meta={
                'comments_count': str(post_comments_count),
                'uploads_count': str(post_uploads_count),
                'uploads_size': str(post_uploads_size),
            })

    # volume
    if parent_cls in [Comment, Post, Volume]:
        volume_id = parent_id if parent_cls == Volume else post.volume_id
        volume = Volume.query.filter(Volume.id==volume_id).first()

        if volume:
            # ...
            volume_posts_ids = db.session.query(Post.id).filter(Post.volume_id==volume_id).subquery()
            volume_posts_comments_ids = db.session.query(Comment.id).filter(Comment.post_id.in_(volume_posts_ids)).subquery()

            # ...
            volume_posts_count = db.session.query(func.count(Post.id)).filter(Post.volume_id==volume.id).scalar()
            volume_posts_sum = db.session.query(func.sum(Post.post_sum)).filter(Post.volume_id==volume.id).filter(Post.post_status=='done').scalar() or 0
            volume_uploads_count = db.session.query(func.count(Upload.id)).filter(Upload.comment_id.in_(volume_posts_comments_ids)).scalar()
            volume_uploads_size = db.session.query(func.sum(Upload.upload_size)).filter(Upload.comment_id.in_(volume_posts_comments_ids)).scalar() or 0

            # ...
            update(volume, is_recounted=True, volume_sum=volume_posts_sum, meta={
                'posts_count': str(volume_posts_count),
                'uploads_count': str(volume_uploads_count),
                'uploads_size': str(volume_uploads_size),
            })
