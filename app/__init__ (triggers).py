from .config import Config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event, DDL
from app.core.app_logger import create_logger
from flask_caching import Cache


app = Flask(__name__)
app.config.from_object(Config)

log = create_logger(app)

db = SQLAlchemy(app)

cache = Cache(config=app.config)
cache.init_app(app)


@app.before_first_request
def before_first_request():
    from app.user import user, user_meta
    from app.vol import vol, vol_meta
    from app.post import post, post_meta, post_tag
    from app.comment import comment
    from app.upload import upload
    db.create_all()
    

    #from app.comment.comment import Comment
    #event.listen(
    #    Comment.__table__,
    #    'after_create',
    #    DDL("SELECT COUNT(id) FROM comments;")
    #)

    


    t_comment_insert = """
        DROP TRIGGER IF EXISTS comment_insert ON comments;
        DROP FUNCTION IF EXISTS comment_insert;

        CREATE FUNCTION comment_insert() RETURNS trigger AS $comment_insert$
            DECLARE
                _vol_id INTEGER;
            BEGIN
                IF NEW.comment_sum <> 0 THEN
                    SELECT posts.vol_id INTO _vol_id FROM posts WHERE posts.id=NEW.post_id LIMIT 1;
                    UPDATE posts SET post_sum=(SELECT SUM(comment_sum) FROM comments WHERE post_id=NEW.post_id) WHERE id=NEW.post_id;
                    UPDATE vols SET vol_sum=(SELECT SUM(post_sum) FROM posts WHERE posts.vol_id=_vol_id) WHERE id=_vol_id;
                END IF;
                RETURN NEW;
            END;
        $comment_insert$ LANGUAGE plpgsql;
        CREATE TRIGGER comment_insert AFTER INSERT ON comments FOR EACH ROW EXECUTE PROCEDURE comment_insert();
    """
    db.engine.execute(t_comment_insert)

    t_comment_update = """
        DROP TRIGGER IF EXISTS comment_update ON comments;
        DROP FUNCTION IF EXISTS comment_update;

        CREATE FUNCTION comment_update() RETURNS trigger AS $comment_update$
            DECLARE
                _vol_id INTEGER;
            BEGIN
                IF NEW.comment_sum <> OLD.comment_sum THEN
                    SELECT posts.vol_id INTO _vol_id FROM posts WHERE posts.id=NEW.post_id LIMIT 1;
                    UPDATE posts SET post_sum=(SELECT SUM(comment_sum) FROM comments WHERE post_id=NEW.post_id) WHERE id=NEW.post_id;
                    UPDATE vols SET vol_sum=(SELECT SUM(post_sum) FROM posts WHERE posts.vol_id=_vol_id) WHERE id=_vol_id;
                END IF;
                RETURN NEW;
            END;
        $comment_update$ LANGUAGE plpgsql;
        CREATE TRIGGER comment_update AFTER UPDATE ON comments FOR EACH ROW EXECUTE PROCEDURE comment_update();
    """
    db.engine.execute(t_comment_update)

    t_comment_delete = """
        DROP TRIGGER IF EXISTS comment_delete ON comments;
        DROP FUNCTION IF EXISTS comment_delete;

        CREATE FUNCTION comment_delete() RETURNS trigger AS $comment_delete$
            DECLARE
                _vol_id INTEGER;
            BEGIN
                IF OLD.comment_sum <> 0 THEN
                    SELECT posts.vol_id INTO _vol_id FROM posts WHERE posts.id=OLD.post_id LIMIT 1;
                    UPDATE posts SET post_sum=(SELECT SUM(comment_sum) FROM comments WHERE post_id=OLD.post_id) WHERE id=OLD.post_id;
                    UPDATE vols SET vol_sum=(SELECT SUM(post_sum) FROM posts WHERE posts.vol_id=_vol_id) WHERE id=_vol_id;
                END IF;
                RETURN NEW;
            END;
        $comment_delete$ LANGUAGE plpgsql;
        CREATE TRIGGER comment_delete AFTER DELETE ON comments FOR EACH ROW EXECUTE PROCEDURE comment_delete();
    """
    db.engine.execute(t_comment_update)


from app.hi import hi_routes
from app.user import user_routes
from app.vol import vol_routes
from app.post import post_routes
from app.comment import comment_routes
from app.upload import upload_routes
