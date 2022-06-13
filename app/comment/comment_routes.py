from flask import g, request
from app import app
from app.core.app_response import app_response
from app.core.user_auth import user_auth
from app.core.basic_handlers import insert, update, delete, select, select_sum, select_all
from app.post.post import Post
from app.comment.comment import Comment
from app.core.app_decimal import app_decimal


@app.route('/comment/', methods=['POST'], endpoint='comment_insert')
@app_response
@user_auth
def comment_insert():
    """
    Comment insert
    headers: user_token
    params: post_id, comment_content, comment_sum
    """
    if not g.user.can_edit:
        return {}, {'user_token': ['user have not permissions for edit'], }, 406

    post_id = request.args.get('post_id')
    post = select(Post, id=post_id, deleted=0)
    if not post:
        return {}, {'post_id': ['post not found or deleted'], }, 404

    comment_content = request.args.get('comment_content')
    comment_sum = request.args.get('comment_sum')

    comment = insert(Comment, user_id=g.user.id, post_id=post.id, comment_content=comment_content, comment_sum=comment_sum)
    
    if comment_sum:
        post_sum = app_decimal(select_sum(Comment, 'comment_sum', post_id=comment.post_id, deleted=0))
        update(comment.post, post_sum=post_sum)

        vol_sum = app_decimal(select_sum(Post, 'post_sum', vol_id=comment.post.vol_id, deleted=0))
        update(comment.post.vol, vol_sum=vol_sum)

    return {
        'comment': str(comment)
    }, {}, 201


@app.route('/comment/<int:comment_id>', methods=['PUT'], endpoint='comment_update')
@app_response
@user_auth
def comment_update(comment_id):
    """ Comment update """
    if not g.user.can_edit:
        return {}, {'user_token': ['user_token must have edit permissions'], }, 406

    comment = select(Comment, id=comment_id, deleted=0)
    if not comment:
        return {}, {'comment_id': ['comment not found or deleted']}, 404

    comment_content = request.args.get('comment_content')
    comment_sum = request.args.get('comment_sum')

    comment_data = {}
    if comment_content:
        comment_data['comment_content'] = comment_content

    if comment_sum:
        comment_data['comment_sum'] = comment_sum

    comment = update(comment, **comment_data)

    if comment_sum:
        post_sum = app_decimal(select_sum(Comment, 'comment_sum', post_id=comment.post_id, deleted=0))
        update(comment.post, post_sum=post_sum)

        vol_sum = app_decimal(select_sum(Post, 'post_sum', vol_id=comment.post.vol_id, deleted=0))
        update(comment.post.vol, vol_sum=vol_sum)

    return {}, {}, 200


@app.route('/comment/<int:comment_id>', methods=['DELETE'], endpoint='comment_delete')
@app_response
@user_auth
def comment_delete(comment_id):
    """ Comment delete """
    if not g.user.can_edit:
        return {}, {'user_token': ['user_token must have edit permissions'], }, 406

    comment = select(Comment, id=comment_id, deleted=0)
    if not comment:
        return {}, {'comment_id': ['comment not found or deleted']}, 404

    delete(comment)

    for upload in comment.uploads:
        delete(upload)

    if comment.comment_sum:
        post_sum = app_decimal(select_sum(Comment, 'comment_sum', post_id=comment.post_id, deleted=0))
        update(comment.post, post_sum=post_sum)

        vol_sum = app_decimal(select_sum(Post, 'post_sum', vol_id=comment.post.vol_id, deleted=0))
        update(comment.post.vol, vol_sum=vol_sum)

    return {}, {}, 200


@app.route('/comments/<int:post_id>', methods=['GET'], endpoint='comments_list')
@app_response
@user_auth
def comments_list(post_id):
    """ Comments list """
    if not g.user.can_read:
        return {}, {'user_token': ['user_token must have read permissions'], }, 406

    offset = int(request.args.get('offset', 0))
    limit = 10
    comments = select_all(Comment, post_id=post_id, deleted=0, offset=offset, limit=limit)

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
                'upload_file': upload.upload_file,
                'upload_mime': upload.upload_mime,
                'upload_size': upload.upload_size,
                'user': {
                    'id': upload.user_id,
                    'user_name': upload.user.user_name,
                },
            } for upload in comment.uploads],
        } for comment in comments]
    }, {}, 200
