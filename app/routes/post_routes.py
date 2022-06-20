from flask import g, request
from app import app, err
from app.core.app_response import app_response
from app.core.user_auth import user_auth
from app.core.basic_handlers import insert, update, delete, select, select_all, select_count
from app.models.post import Post, PostStatus
from app.models.post_tag import PostTag
from app.models.volume import Volume
from marshmallow import ValidationError

POST_SELECT_LIMIT = app.config['POST_SELECT_LIMIT']


@app.route('/post/', methods=['POST'], endpoint='post_insert')
@app_response
@user_auth
def post_insert():
    if not g.user.can_edit:
        return {}, {'user_token': [err.NOT_ALLOWED], }, 400

    volume_id = request.args.get('volume_id')
    post_status = request.args.get('post_status')
    post_title = request.args.get('post_title')
    post_tags = PostTag.crop(request.args.get('post_tags'))

    volume = select(Volume, id=volume_id)
    if not volume:
        return {}, {'volume_id': [err.NOT_FOUND], }, 400

    post = insert(Post, user_id=g.user.id, volume_id=volume.id, post_status=post_status, post_title=post_title, tags=post_tags)
    return {'post_id': post.id}, {}, 201


@app.route('/post/<int:post_id>', methods=['PUT'], endpoint='post_update')
@app_response
@user_auth
def post_update(post_id):
    if not g.user.can_edit:
        return {}, {'user_token': [err.NOT_ALLOWED], }, 400

    post = select(Post, id=post_id)
    if not post:
        return {}, {'post_id': [err.NOT_FOUND]}, 404

    post_status = request.args.get('post_status')
    post_title = request.args.get('post_title')
    post_tags = PostTag.crop(request.args.get('post_tags'))

    post_data = {}
    if post_status:
        post_data['post_status'] = post_status
    
    if post_title:
        post_data['post_title'] = post_title

    if post_tags:
        post_data['tags'] = post_tags

    post = update(post, **post_data)
    return {}, {}, 200


@app.route('/post/<int:post_id>', methods=['GET'], endpoint='post_select')
@app_response
@user_auth
def post_select(post_id):
    if not g.user.can_read:
        return {}, {'user_token': [err.NOT_ALLOWED], }, 400

    post = select(Post, id=post_id)
    if post:
        return {'post': post.to_dict()}, {}, 200

    else:
        return {}, {'post_id': [err.NOT_FOUND]}, 404


@app.route('/post/<int:post_id>', methods=['DELETE'], endpoint='post_delete')
@app_response
@user_auth
def post_delete(post_id):
    """ Post delete """
    if not g.user.can_admin:
        return {}, {'user_token': [err.NOT_ALLOWED], }, 406

    post = select(Post, id=post_id)
    if not post:
        return {}, {'comment_id': [err.NOT_FOUND]}, 404

    delete(post)
    return {}, {}, 200


@app.route('/posts/<int:offset>', methods=['GET'], endpoint='posts_list')
@app_response
@user_auth
def posts_list(offset):
    if not g.user.can_read:
        return {}, {'user_token': [err.NOT_ALLOWED], }, 400

    post_status = request.args.get('post_status')
    if post_status not in PostStatus.__members__:
        raise ValidationError({'volume_status': [err.IS_INCORRECT]})

    posts = select_all(Post, post_status=post_status, offset=offset, limit=POST_SELECT_LIMIT)
    posts_count = select_count(Post, post_status=post_status)

    return {
        'posts': [post.to_dict() for post in posts],
        'posts_count': posts_count,
    }, {}, 200

