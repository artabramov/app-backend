import imp
from app.core.app_decimal import app_decimal
from app.core.basic_handlers import insert, update, delete, select, select_all, select_count, select_sum
from app.models.upload import Upload
from app.models.comment import Comment
from app.models.post import Post
from app.models.post_meta import PostMeta
from app.models.volume import Volume
from app.models.user import User
from app import db
from sqlalchemy.sql import func


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

    if cls in [Upload, Comment, Post]:
        # post
        post_id = comment.post_id if cls in [Upload, Comment] else obj_id
        post = Post.query.filter(Post.id==post_id).first()
        # post uploads
        post_uploads_count = db.session.query(func.count(getattr(Upload, 'id'))).filter(Upload.comment_id.in_(comments_ids)).one()[0]
        post_uploads_size = db.session.query(func.sum(getattr(Upload, 'upload_size'))).filter(Upload.comment_id.in_(comments_ids)).one()[0]
        # update post
        update(post, meta={
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

    pass
