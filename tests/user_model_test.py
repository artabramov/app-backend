import unittest
from unittest.mock import MagicMock, patch
#import app
from app.models.user import User, UserStatus
from app.models.post_meta import PostMeta
from app.models.volume_meta import VolumeMeta
from app.models.user_meta import UserMeta
from marshmallow import ValidationError


class UserTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test___setattr__user_status_correct(self):
        user = User('dummy', 'dummy', 'dummy')
        User.__setattr__(user, 'user_status', 'editor')
        self.assertEqual(user.user_status, UserStatus.editor)


    def test___setattr__user_status_incorrect(self):
        user = User('dummy', 'dummy', 'dummy')
        self.assertRaises(ValidationError, User.__setattr__, user, 'user_status', 'dummy')


if __name__ == '__main__':
    unittest.main()