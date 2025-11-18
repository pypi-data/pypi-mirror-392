import unittest

# import getSecrets as gs
from src import getSecrets as gs


class TestGetSecrets(unittest.TestCase):

    def test_listsecret(self):
        secrets = gs.list_secret()
        self.assertTrue('test' in secrets)

    def test_getsecrets(self):
        secret = gs.get_secret('test2')
        self.assertTrue('test2' in secret)
        if isinstance(secret, dict):
            self.assertEqual(secret['test'], 'test')
        else:
            self.assertEqual(secret, 'test2')

    def test_getUpdateSecrets(self):
        secret = gs.get_secret('test')
        secret = 'test1'
        gs.upd_secret('test', secret)
        secret = gs.get_secret('test')
        self.assertTrue('test' in secret)
        if isinstance(secret, dict):
            self.assertEqual(secret['test'], 'test1')
        else:
            self.assertEqual(secret, 'test1')

    def test_usr_pwd(self):
        usr, pwd = gs.get_user_pwd('test')
        self.assertEqual(usr, 'user')
        self.assertEqual(pwd, 'pwd')


if __name__ == '__main__':
    unittest.main()
