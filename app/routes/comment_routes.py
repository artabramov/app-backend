from flask import g, request
from app import app, err
from app.core.app_response import app_response
from app.core.user_auth import user_auth
from app.core.basic_handlers import insert, update, delete, select, select_all, select_sum, select_count
from app.models.post import Post
from app.models.comment import Comment
from app.core.app_decimal import app_decimal

COMMENT_SELECT_LIMIT = app.config['COMMENT_SELECT_LIMIT']


@app.route('/comment/', methods=['POST'], endpoint='comment_insert')
@app_response
@user_auth
def comment_insert():
    if not g.user.can_edit:
        return {}, {'user_token': [err.NOT_ALLOWED], }, 400

    post_id = request.args.get('post_id')
    comment_content = request.args.get('comment_content')
    comment_sum = request.args.get('comment_sum')

    post = select(Post, id=post_id)
    if not post:
        return {}, {'post_id': [err.NOT_FOUND], }, 400

    comment = insert(Comment, user_id=g.user.id, post_id=post.id, comment_content=comment_content, comment_sum=comment_sum)
    
    #if comment_sum:
    #    post_sum = app_decimal(select_sum(Comment, 'comment_sum', post_id=comment.post_id, deleted=0))
    #    update(comment.post, post_sum=post_sum)
    #    volume_sum = app_decimal(select_sum(Post, 'post_sum', volume_id=comment.post.volume_id, deleted=0))
    #    update(comment.post.volume, volume_sum=volume_sum)

    return {'comment_id': comment.id}, {}, 201


@app.route('/comment/<int:comment_id>/', methods=['PUT'], endpoint='comment_update')
@app_response
@user_auth
def comment_update(comment_id):
    if not g.user.can_edit:
        return {}, {'user_token': [err.NOT_ALLOWED], }, 400

    comment_content = request.args.get('comment_content')
    comment_sum = request.args.get('comment_sum')

    comment = select(Comment, id=comment_id)
    if not comment:
        return {}, {'comment_id': [err.NOT_FOUND]}, 404

    comment_data = {}
    if comment_content:
        comment_data['comment_content'] = comment_content

    if comment_sum:
        comment_data['comment_sum'] = comment_sum

    comment = update(comment, **comment_data)


    #if comment_sum:
    #    post_sum = app_decimal(select_sum(Comment, 'comment_sum', post_id=comment.post_id, deleted=0))
    #    update(comment.post, post_sum=post_sum)
    #    volume_sum = app_decimal(select_sum(Post, 'post_sum', volume_id=comment.post.volume_id, deleted=0))
    #    update(comment.post.volume, volume_sum=volume_sum)

    return {}, {}, 200


@app.route('/comment/<int:comment_id>', methods=['DELETE'], endpoint='comment_delete')
@app_response
@user_auth
def comment_delete(comment_id):
    if not g.user.can_admin:
        return {}, {'user_token': [err.NOT_ALLOWED], }, 400

    comment = select(Comment, id=comment_id)
    if not comment:
        return {}, {'comment_id': [err.NOT_FOUND]}, 404

    delete(comment)

    #for upload in comment.uploads:
    #    delete(upload)

    #if comment.comment_sum:
    #    post_sum = app_decimal(select_sum(Comment, 'comment_sum', post_id=comment.post_id, deleted=0))
    #    update(comment.post, post_sum=post_sum)
    #    volume_sum = app_decimal(select_sum(Post, 'post_sum', volume_id=comment.post.volume_id, deleted=0))
    #    update(comment.post.volume, volume_sum=volume_sum)

    return {}, {}, 200


@app.route('/post/<int:post_id>/comments/<int:offset>/', methods=['GET'], endpoint='comments_list')
@app_response
@user_auth
def comments_list(post_id, offset):
    if not g.user.can_read:
        return {}, {'user_token': [err.NOT_ALLOWED], }, 400

    comments = select_all(Comment, post_id=post_id, offset=offset, limit=COMMENT_SELECT_LIMIT)
    comments_count = select_count(Comment, post_id=post_id)

    return {
        'comments': [comment.to_dict() for comment in comments],
        'comments_count': comments_count,
    }, {}, 200

    """
    return {'comments': 
        [{
            'id': comment.id, 
            'created': comment.created, 
            'comment_content': comment.comment_content,
            'comment_sum': comment.comment_sum,
            'user': {
                'id': comment.user_id,
                'user_name': comment.user.user_name,
            },
            'uploads': [{
                'id': upload.id,
                'created': upload.created,
                'upload_name': upload.upload_name,
                'upload_dir': upload.upload_dir,
                'upload_url': upload.upload_url,
                'upload_mime': upload.upload_mime,
                'upload_size': upload.upload_size,
                'user': {
                    'id': upload.user_id,
                    'user_name': upload.user.user_name,
                },
            } for upload in comment.uploads],
        } for comment in comments],
        'comments_count': comments_count,
    }, {}, 200
    """
