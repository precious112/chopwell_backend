from django.test import TestCase
from users.models import Profile
from django.contrib.auth.models import User

class TestAppModels(TestCase):
    def setUp(self):
        self.testuser = User.objects.create_user(
            username='testuser', password='12345')
    def test_model_str(self):
        
        testprofile=Profile.objects.create(user=self.testuser)
        self.assertEqual(str(testprofile), "testuser Profile")