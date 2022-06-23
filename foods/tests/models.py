from django.test import TestCase
from foods.models import Food,Transaction
from users.models import Profile
from django.contrib.auth.models import User
import random

class TestAppModels(TestCase):
    def setUp(self):
        self.testuser = User.objects.create_user(
            username='testuser', password='12345')
        self.testprofile=Profile.objects.create(user=self.testuser,is_vendor=True)
        
    def test_food_model_str(self):
        testFood=Food.objects.create(profile=self.testprofile,name="rice")
        self.assertEqual(str(testFood), "rice")
        
    def test_transaction_model_str(self):
        other_user=User.objects.create(username="bola",email="bola@gmail.com")
        t_id=random.randint(1000, 9999)
        transaction=Transaction.objects.create(
            transaction_id=f'TransactionID{t_id}',
            sender=self.testuser,
            receiver=other_user
            )
        self.assertEqual(str(transaction),f'TransactionID{t_id}')