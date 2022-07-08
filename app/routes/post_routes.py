from flask import g, request
from app import app, err
from app.core.app_response import app_response
from app.core.user_auth import user_auth
from app.core.basic_handlers import insert, update, delete, select, select_all, select_count
from app.models.user import User
from app.models.post import Post, PostStatus
from app.models.post_tag import PostTag
from app.models.volume import Volume
from app.models.category import Category
from marshmallow import ValidationError

POST_SELECT_LIMIT = app.config['POST_SELECT_LIMIT']


@app.route('/post/', methods=['POST'], endpoint='post_insert')
@app_response
@user_auth
def post_insert():
    if not g.user.can_edit:
        return {}, {'user_token': [err.NOT_ALLOWED], }, 400

    # TODO: check all ..._id integer items accepted from request
    volume_id = request.args.get('volume_id')
    category_id = request.args.get('category_id')
    post_status = request.args.get('post_status')
    post_title = request.args.get('post_title')
    post_content = request.args.get('post_content')
    post_sum = request.args.get('post_sum')
    post_tags = PostTag.crop(request.args.get('post_tags'))

    volume = select(Volume, id=volume_id)
    if not volume:
        return {}, {'volume_id': [err.NOT_FOUND], }, 400

    category = select(Category, id=category_id)
    if not volume:
        return {}, {'category_id': [err.NOT_FOUND], }, 400

    post = insert(Post, user_id=g.user.id, volume_id=volume.id, category_id=category.id, post_status=post_status, post_title=post_title, post_content=post_content, post_sum=post_sum, tags=post_tags)
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
    post_content = request.args.get('post_content')
    post_sum = request.args.get('post_sum')
    post_tags = PostTag.crop(request.args.get('post_tags'))

    post_data = {}
    if post_status:
        post_data['post_status'] = post_status
    
    if post_title:
        post_data['post_title'] = post_title

    if post_content:
        post_data['post_content'] = post_content

    if post_sum:
        post_data['post_sum'] = post_sum

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
    if not g.user.can_admin:
        return {}, {'user_token': [err.NOT_ALLOWED], }, 406

    post = select(Post, id=post_id)
    if not post:
        return {}, {'comment_id': [err.NOT_FOUND]}, 404

    delete(post)
    return {}, {}, 200


@app.route('/posts/<int:offset>/', methods=['GET'], endpoint='posts_list')
@app_response
@user_auth
def posts_list(offset):
    if not g.user.can_read:
        return {}, {'user_token': [err.NOT_ALLOWED], }, 400

    volume_id = request.args.get('volume_id')
    post_status = request.args.get('post_status')
    post_title = request.args.get('post_title')
    post_tag = request.args.get('post_tag')

    posts, posts_count = [], 0
    if post_status and volume_id:
        if post_status not in PostStatus.__members__:
            raise ValidationError({'post_status': [err.IS_INCORRECT]})
            
        posts = select_all(Post, volume_id=volume_id, post_status=post_status, offset=offset, limit=POST_SELECT_LIMIT)
        posts_count = select_count(Post, volume_id=volume_id, post_status=post_status)

    elif post_title:
        posts = select_all(Post, post_title='%{}%'.format(post_title), offset=offset, limit=POST_SELECT_LIMIT)
        posts_count = select_count(Post, post_title='%{}%'.format(post_title))

    elif post_tag:
        posts = select_all(Post, tag_value=post_tag, offset=offset, limit=POST_SELECT_LIMIT)
        posts_count = select_count(Post, tag_value=post_tag)

    return {
        'posts': [post.to_dict() for post in posts],
        'posts_count': posts_count,
    }, {}, 200
