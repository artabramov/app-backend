import imp
from app.core.app_decimal import app_decimal
from app.core.basic_handlers import insert, update, delete, select, select_all, select_count, select_sum
from app.models.upload import Upload
from app.models.comment import Comment
from app.models.post import Post
from app.models.post_meta import PostMeta
from app.models.volume import Volume
from app import db
from sqlalchemy.sql import func


def recount_uploads2(obj):

    # delete the upload
    if isinstance(obj, Comment):

        # recount uploads size of the comment:
        uploads_ids = db.session.query(Upload.id).filter(Upload.comment_id==obj.id).subquery()
        uploads = Upload.query.filter(Upload.id.in_(uploads_ids)).all()
        
        # recount uploads size of the post:
        comments_ids = db.session.query(Comment.id).filter(Comment.post_id==obj.post_id).subquery()
        comments = Comment.query.filter(Comment.id.in_(comments_ids)).all()
        
        # recount posts size of the volume:
        posts_ids = db.session.query(Post.id).filter(Post.id==obj.post_id).subquery()
        posts = Post.query.filter(Post.id.in_(posts_ids)).all()

        # volume
        volume = select(Volume, id=posts[0].volume_id)

        pass


def recount_uploads(comment):
    post = select(Post, id=comment.post_id)
    comments_subquery = db.session.query(Comment.id).filter(Comment.post_id==post.id).subquery()
    uploads_count = db.session.query(func.count(getattr(Upload, 'id'))).filter(Upload.comment_id.in_(comments_subquery)).one()[0]
    uploads_size = db.session.query(func.sum(getattr(Upload, 'upload_size'))).filter(Upload.comment_id.in_(comments_subquery)).one()[0]
    post_meta = {
        'uploads_count': str(uploads_count),
        'uploads_size': str(uploads_size),
    }
    update(post, meta=post_meta)

    volume = select(Volume, id=post.volume_id)
    #posts_subquery = db.session.query(Post.id).filter(Post.volume_id==volume.id).subquery()
    #uploads_count = db.session.query(func.sum(getattr(PostMeta, 'meta_value'))).filter(Upload.comment_id.in_(comments_subquery)).one()[0]
    posts_subquery = db.session.query(Post.id).filter(Post.volume_id==volume.id).subquery()
    comments_subquery = db.session.query(Comment.id).filter(Comment.post_id.in_(posts_subquery)).subquery()
    uploads_count = db.session.query(func.count(getattr(Upload, 'id'))).filter(Upload.comment_id.in_(comments_subquery)).one()[0]
    uploads_size = db.session.query(func.sum(getattr(Upload, 'upload_size'))).filter(Upload.comment_id.in_(comments_subquery)).one()[0]
    volume_meta = {
        'uploads_count': str(uploads_count),
        'uploads_size': str(uploads_size),
    }
    update(volume, meta=volume_meta)


def recount_comments(comment):
    #uploads_count = select_count(Upload, comment_id=comment.id)
    #uploads_size = select_sum(Upload, 'upload_size', comment_id=comment.id)
    #comment_meta = {
    #    'uploads_count': str(uploads_count),
    #    'uploads_size': str(uploads_size),
    #}
    #update(comment, meta=comment_meta)
    pass


def recount_post(post):
    post_sum = app_decimal(select_sum(Comment, 'comment_sum', post_id=post.id))
    comments_count = select_count(Comment, post_id=post.id)
    post_meta = {
        'comments_count': str(comments_count),
    }
    update(post, post_sum=post_sum, meta=post_meta)
    recount_volume(post.volume)


def recount_volume(volume):
    volume_sum = app_decimal(select_sum(Post, 'post_sum', volume_id=volume.id, post_status='done'))
    update(volume, volume_sum=volume_sum)
