from flask import g, request
from app import app, err
from app.core.app_response import app_response
from app.core.basic_handlers import insert, update, delete, select, select_all, select_count
from app.models.category import Category
from app.core.user_auth import user_auth


@app.route('/category/', methods=['POST'], endpoint='category_insert')
@app_response
@user_auth
def category_insert():
    if not g.user.can_admin:
        return {}, {'user_token': [err.NOT_ALLOWED], }, 400

    category_title = request.args.get('category_title')

    category = insert(Category, user_id=g.user.id, category_title=category_title)
    return {'category_id': category.id}, {}, 201


@app.route('/category/<int:category_id>', methods=['PUT'], endpoint='category_update')
@app_response
@user_auth
def category_update(category_id):
    if not g.user.can_admin:
        return {}, {'user_token': [err.NOT_ALLOWED], }, 400

    category_title = request.args.get('category_title', '')

    category = select(Category, id=category_id)
    if not category:
        return {}, {'category_id': [err.NOT_FOUND]}, 404

    category_data = {}
    if category_title:
        category_data['category_title'] = category_title

    category = update(category, **category_data)
    return {}, {}, 200


@app.route('/category/<int:category_id>', methods=['DELETE'], endpoint='category_delete')
@app_response
@user_auth
def category_delete(category_id):
    if not g.user.can_admin:
        return {}, {'user_token': [err.NOT_ALLOWED], }, 400

    category = select(Category, id=category_id)
    if not category:
        return {}, {'category_id': [err.NOT_FOUND]}, 404

    delete(category)
    return {}, {}, 200


@app.route('/categories/', methods=['GET'], endpoint='categories_list')
@app_response
@user_auth
def categories_list():
    if not g.user.can_read:
        return {}, {'user_token': [err.NOT_ALLOWED], }, 400

    categories = select_all(Category)

    return {
        'categories': [category.to_dict() for category in categories],
    }, {}, 200
