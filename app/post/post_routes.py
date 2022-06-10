from flask import g, request
from app import app
from app.core.app_response import app_response
from app.core.primary_handlers import insert, update, delete, select, search
from app.post.post import Post
from app.core.user_auth import user_auth


@app.route('/post/', methods=['POST'], endpoint='post_post')
@app_response
@user_auth
def post_post():
    """ Post insert """
    if not g.user.can_edit:
        return {}, {'user_token': ['user_token have not permissions for vol edit'], }, 406

    vol_id = request.args.get('vol_id')
    post_title = request.args.get('post_title')

    post_meta = {
        'key_1': 'value 1!!!',
        'key_2': 'value 2!!!',
        'key_3': 'value 3!!!',
    }

    post_tags = ['one', 'two', 'three']

    post = insert(Post, user_id=g.user.id, vol_id=vol_id, post_title=post_title, meta=post_meta, tags=post_tags)

    return {
        'vol': str(post)
    }, {}, 201

