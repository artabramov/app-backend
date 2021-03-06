from flask import g, request
from app import app, err
from app.core.app_response import app_response
from app.core.basic_handlers import insert, update, delete, select, select_all, select_count
from app.models.category import Category
from app.models.user import User
from app.core.user_auth import user_auth


def to_dict(category):
    user = select(User, id=category.user_id)
    return {
        'id': category.id,
        'created': category.created,
        'user_id': category.user_id,
        'user': {'user_login': user.user_login},
        'category_title': category.category_title,
        'category_summary': category.category_summary,
    }


@app.route('/category/', methods=['POST'], endpoint='category_insert')
@app_response
@user_auth
def category_insert():
    if not g.user.can_admin:
        return {}, {'user_token': [err.PERMISSION_DENIED], }, 200

    category_title = request.args.get('category_title')
    category_summary = request.args.get('category_summary', '')

    category = insert(Category, user_id=g.user.id, category_title=category_title, category_summary=category_summary)
    return {'category_id': category.id}, {}, 201


@app.route('/category/<int:category_id>/', methods=['GET'], endpoint='category_select')
@app_response
@user_auth
def category_select(category_id):
    if not g.user.can_read:
        return {}, {'user_token': [err.PERMISSION_DENIED], }, 200

    category = select(Category, id=category_id)
    if category:
        return {'category': to_dict(category)}, {}, 200

    else:
        return {}, {'category_id': [err.VALUE_NOT_FOUND]}, 200


@app.route('/category/<int:category_id>/', methods=['PUT'], endpoint='category_update')
@app_response
@user_auth
def category_update(category_id):
    if not g.user.can_admin:
        return {}, {'user_token': [err.PERMISSION_DENIED], }, 200

    category_title = request.args.get('category_title', '')
    category_summary = request.args.get('category_summary', '')

    category = select(Category, id=category_id)
    if not category:
        return {}, {'category_id': [err.VALUE_NOT_FOUND]}, 200

    category_data = {}
    if category_title:
        category_data['category_title'] = category_title

    if category_summary:
        category_data['category_summary'] = category_summary

    category = update(category, **category_data)
    return {}, {}, 200


@app.route('/category/<int:category_id>/', methods=['DELETE'], endpoint='category_delete')
@app_response
@user_auth
def category_delete(category_id):
    if not g.user.can_admin:
        return {}, {'user_token': [err.PERMISSION_DENIED], }, 200

    category = select(Category, id=category_id)
    if not category:
        return {}, {'category_id': [err.VALUE_NOT_FOUND]}, 200

    delete(category)
    return {}, {}, 200


@app.route('/categories/', methods=['GET'], endpoint='categories_list')
@app_response
@user_auth
def categories_list():
    if not g.user.can_read:
        return {}, {'user_token': [err.PERMISSION_DENIED], }, 200

    categories = select_all(Category)
    return {
        'categories': [to_dict(category) for category in categories],
    }, {}, 200
