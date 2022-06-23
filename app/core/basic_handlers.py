from app import db, cache
from sqlalchemy import asc, desc, inspect
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

    #recount(cls, obj.id)
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


def update(obj, **kwargs):
    cls = obj.__class__

    for key in [x for x in kwargs if x not in ['meta', 'tags']]:
        value = kwargs[key]
        setattr(obj, key, value)

    db.session.merge(obj)
    db.session.flush()

    if 'meta' in kwargs:
        update_meta(obj, kwargs['meta'])

    if 'tags' in kwargs:
        update_tags(obj, kwargs['tags'])

    cache.delete('%s.%s' % (cls.__tablename__, obj.id))
    return obj


def delete(obj):
    db.session.delete(obj)
    db.session.flush()
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


def recount(cls, obj_id):
    if cls == Upload:
        # upload
        upload_id = obj_id
        upload = Upload.query.filter(Upload.id==upload_id).first()
        # other uploads
        uploads_ids = db.session.query(Upload.id).filter(Upload.comment_id==upload.comment_id).subquery()
        uploads = Upload.query.filter(Upload.id.in_(uploads_ids)).all()

    if cls in [Upload, Comment]:
        # comment
        comment_id = upload.comment_id if cls == Upload else obj_id
        comment = Comment.query.filter(Comment.id==comment_id).first()
        # comment uploads
        comment_uploads_count = db.session.query(func.count(getattr(Upload, 'id'))).filter(Upload.comment_id==comment_id).one()[0]
        comment_uploads_size = db.session.query(func.sum(getattr(Upload, 'upload_size'))).filter(Upload.comment_id==comment_id).one()[0]        
        # other comments
        comments_ids = db.session.query(Comment.id).filter(Comment.post_id==comment.post_id).subquery()
        comments = Comment.query.filter(Comment.id.in_(comments_ids)).all()
        # comments data (post_meta)
        post_comments_count = db.session.query(func.count(getattr(Comment, 'id'))).filter(Comment.id.in_(comments_ids)).one()[0]
        post_comments_sum = db.session.query(func.sum(getattr(Comment, 'comment_sum'))).filter(Comment.id.in_(comments_ids)).one()[0]

    if cls in [Upload, Comment, Post]:
        # post
        post_id = comment.post_id if cls in [Upload, Comment] else obj_id
        post = Post.query.filter(Post.id==post_id).first()
        # post uploads
        post_uploads_count = db.session.query(func.count(getattr(Upload, 'id'))).filter(Upload.comment_id.in_(comments_ids)).one()[0]
        post_uploads_size = db.session.query(func.sum(getattr(Upload, 'upload_size'))).filter(Upload.comment_id.in_(comments_ids)).one()[0]
        # update post
        update(post, post_sum=post_comments_sum, meta={
            'comments_count': str(post_comments_count),
            'uploads_count': str(post_uploads_count),
            'uploads_size': str(post_uploads_size),
        })
        # other posts
        posts_ids = db.session.query(Post.id).filter(Post.volume_id==post.volume_id).subquery()
        posts = Post.query.filter(Post.id.in_(posts_ids)).all()
        # posts data (volume_meta)
        volume_posts_count = db.session.query(func.count(getattr(Post, 'id'))).filter(Post.id.in_(posts_ids)).one()[0]
        volume_posts_sum = db.session.query(func.sum(getattr(Post, 'post_sum'))).filter(Post.id.in_(posts_ids)).one()[0]


    if cls in [Upload, Comment, Post, Volume]:
        # volume
        volume_id = post.volume_id if cls in [Upload, Comment, Post] else obj_id
        volume = Volume.query.filter(Volume.id==volume_id).first()
        # volume data (volume_meta)
        volume_comments_ids = db.session.query(Comment.id).filter(Comment.post_id.in_(posts_ids)).subquery()
        volume_comments = Comment.query.filter(Comment.id.in_(volume_comments_ids)).all()
        volume_uploads_count = db.session.query(func.count(getattr(Upload, 'id'))).filter(Upload.comment_id.in_(volume_comments_ids)).one()[0]
        volume_uploads_size = db.session.query(func.sum(getattr(Upload, 'upload_size'))).filter(Upload.comment_id.in_(volume_comments_ids)).one()[0]

    if cls in [Upload, Comment, Post, Volume, User]:
        # user
        if cls == User:
            user_id = obj_id
            user = User.query.filter(User.id==user_id).first()
        else:
            obj = cls.query.filter(cls.id==obj_id).first()
            user = User.query.filter(User.id==obj.user_id).first()
        # user data (user_meta)
        user_uploads_size = db.session.query(func.sum(getattr(Upload, 'upload_size'))).filter(Upload.user_id==user.id).one()[0]
        user_uploads_count = db.session.query(func.count(getattr(Upload, 'id'))).filter(Upload.user_id==user.id).one()[0]
        # posts and comments data (user_meta)
        user_comments_count = db.session.query(func.count(getattr(Comment, 'id'))).filter(Comment.user_id==user.id).one()[0]
        user_posts_count = db.session.query(func.count(getattr(Post, 'id'))).filter(Post.user_id==user.id).one()[0]

