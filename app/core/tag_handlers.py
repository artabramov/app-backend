from app import db, cache


def reset_tag(obj, **kwargs):
    cls = obj.__class__
    Tag = cls.tags.property.mapper.class_

    for tag_value in kwargs['tags']:
        tag_value = tag_value.strip().lower()
        tag = Tag.query.filter_by(**{Tag.parent: obj.id, 'tag_value': tag_value}).first()
        if tag and tag_value:
            tag.tag_value = tag_value
            db.session.add(tag)

        elif tag and not tag_value:
            db.session.delete(tag)

        elif not tag and tag_value:
            tag = Tag(obj.id, tag_value)
            db.session.add(tag)

    db.session.flush()
    cache.set('%s.%s' % (cls.__tablename__, obj.id), obj)
