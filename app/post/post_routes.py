from flask import g, request
from app import app
from app.core.app_response import app_response
from app.core.user_auth import user_auth
from app.core.basic_handlers import insert, update, delete, select, select_all
from app.post.post import Post
from app.vol.vol import Vol
from app.comment.comment import Comment


@app.route('/post/', methods=['POST'], endpoint='post_insert')
@app_response
@user_auth
def post_insert():
    """ Post insert """
    if not g.user.can_edit:
        return {}, {'user_token': ['user_token have not permissions for vol edit'], }, 406

    vol_id = request.args.get('vol_id')
    vol = select(Vol, id=vol_id, deleted=0)
    if not vol:
        return {}, {'vol_id': ['vol not found or deleted'], }, 404

    post_status = request.args.get('post_status')
    post_title = request.args.get('post_title')

    post_meta = {
        'key_1': 'value 1',
        'key_2': 'value 1',
        'key_3': 'value 1',
    }

    post_tags = ['tag1', 'tag2', 'tag3']

    post = insert(Post, user_id=g.user.id, vol_id=vol.id, post_status=post_status, post_title=post_title, meta=post_meta, tags=post_tags)
    return {
        'post': str(post)
    }, {}, 201


@app.route('/post/<int:post_id>', methods=['PUT'], endpoint='post_update')
@app_response
@user_auth
def post_update(post_id):
    """ Post update """
    if not g.user.can_edit:
        return {}, {'user_token': ['user_token must have edit permissions'], }, 406

    post = select(Post, id=post_id, deleted=0)
    if not post:
        return {}, {'post_id': ['post not found or deleted']}, 404

    post_data = {}

    post_status = request.args.get('post_status')
    if post_status:
        post_data['post_status'] = post_status

    post_title = request.args.get('post_title')
    if post_title:
        post_data['post_title'] = post_title

    post_data['meta'] = {
        'key_1': 'value2',
        'key_2': 'value2',
        'key_3': None,
    }

    post_data['tags'] = ['tag4', 'tag5', 'tag6']

    post = update(post, **post_data)
    return {}, {}, 200


@app.route('/post/<int:post_id>', methods=['DELETE'], endpoint='post_delete')
@app_response
@user_auth
def post_delete(post_id):
    """ Post delete """
    if not g.user.can_edit:
        return {}, {'user_token': ['user_token must have edit permissions'], }, 406

    post = select(Post, id=post_id, deleted=0)
    if not post:
        return {}, {'comment_id': ['comment not found or deleted']}, 404

    #delete(post)

    comments = select_all(Comment, post_id=post.id, deleted=0)

    return {}, {}, 200
