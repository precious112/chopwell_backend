from rest_framework.test import APITestCase,APIClient
from foods.models import Food,Transaction
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from users.models import Profile
from unittest.mock import patch
import json,requests
import random

class MockInitialResponse:
 
    def __init__(self):
        self.status_code = 200
        
    def json(self):
        return {
            "status": True,
  "message": "Authorization URL created",
  "data": {
    "authorization_url": "https://checkout.paystack.com/0peioxfhpn",
    "access_code": "0peioxfhpn",
    "reference": "7PVGX8MEk85tgeEpVDtD"
  }
            }
    
    
class MockVerifyResponse:
 
    def __init__(self):
        self.status_code = 200
        
    def json(self):
        return {
  "status": True,
  "message": "Verification successful",
  "data": {
    "amount": 27000,
    "currency": "NGN",
    "transaction_date": "2016-10-01T11:03:09.000Z",
    "status": "success",
    "reference": "DG4uishudoq90LD",
    "domain": "test",
    "metadata": 0,
    "gateway_response": "Successful",
    "message": None,
    "channel": "card",
    "ip_address": "41.1.25.1",
    "log": {
      "time_spent": 9,
      "attempts": 1,
      "authentication": None,
      "errors": 0,
      "success": True,
      "mobile": False,
      "input": [],
      "channel": None,
      "history": [{
        "type": "input",
        "message": "Filled these fields: card number, card expiry, card cvv",
        "time": 7
        },
        {
          "type": "action",
          "message": "Attempted to pay",
          "time": 7
        },
        {
          "type": "success",
          "message": "Successfully paid",
          "time": 8
        },
        {
          "type": "close",
          "message": "Page closed",
          "time": 9
        }
      ]
    },
    "fees": None,
    "authorization": {
      "authorization_code": "AUTH_8dfhjjdt",
      "card_type": "visa",
      "last4": "1381",
      "exp_month": "08",
      "exp_year": "2018",
      "bin": "412345",
      "bank": "TEST BANK",
      "channel": "card",
      "signature": "SIG_idyuhgd87dUYSHO92D",
      "reusable": True,
      "country_code": "NG",
      "account_name": "BoJack Horseman"
    },
    "customer": {
      "id": 84312,
      "customer_code": "CUS_hdhye17yj8qd2tx",
      "first_name": "BoJack",
      "last_name": "Horseman",
      "email": "bojack@horseman.com"
    },
    "plan": "PLN_0as2m9n02cl0kp6",
    "requested_amount": 1500000
  }
}



class TestFoodApp(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.register_form={"username":"balogun","email":"precious@gmail.com","password":"password"}
        
    def authenticate(self):
        
        response=self.client.post(
            reverse("register"),self.register_form,format='json'
            )
        
        
        self.id=response.data['user']['id']
        self.username=response.data['user']['username']
        self.otp=response.data['code']
        self.client.post(
            reverse("verify"),{"otp":self.otp,"username":self.username},format='json'
            )
        response1=self.client.post(
            reverse("login"),{"username":"balogun","password":"password"},format='json'
            )
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + response1.data['token'])
        
    def test_List_Vendor_Foods(self):
        self.authenticate()
        user=User.objects.filter(username=self.username).first()
        profile=Profile.objects.create(user=user,is_vendor=True)
        other_user=User.objects.create(username="oluwapelumi",email="babe@gmail.com")
        profile=Profile.objects.create(user=other_user,is_vendor=True)
        response=self.client.get(
            reverse("list-vendor-foods",kwargs={"username":"oluwapelumi"}),format='json'
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_Fail_Profile_List_Vendor_Foods(self):
        self.authenticate()
        other_user=User.objects.create(username="oluwapelumi",email="babe@gmail.com")
        #profile=Profile.objects.create(user=other_user,is_vendor=True)
        response=self.client.get(
            reverse("list-vendor-foods",kwargs={"username":"oluwapelumi"}),format='json'
            )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_Fail_User_List_Vendor_Foods(self):
        self.authenticate()
        response=self.client.get(
            reverse("list-vendor-foods",kwargs={"username":"oluwapelumi"}),format='json'
            )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    @patch("requests.post", return_value=MockInitialResponse())
    def test_pay_vendor(self,mocked):
        self.authenticate()
        user=User.objects.filter(username=self.username).first()
        profile=Profile.objects.create(user=user)
        other_user=User.objects.create(username="oluwapelumi",email="babe@gmail.com")
        other_profile=Profile.objects.create(user=other_user,is_vendor=True)
        food=Food.objects.create(profile=other_profile)
        response=self.client.post(
            reverse("pay-vendor",kwargs={"username1":self.username,"username2":"oluwapelumi","id":food.id}),format='json'
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        
    @patch("requests.get", return_value=MockVerifyResponse())
    def test_verify_payment(self,mocked):
        self.authenticate()
        user=User.objects.filter(username=self.username).first()
        profile=Profile.objects.create(user=user)
        other_user=User.objects.create(username="oluwapelumi",email="babe@gmail.com")
        other_profile=Profile.objects.create(user=other_user,is_vendor=True)
        food=Food.objects.create(profile=other_profile)
        t_id=random.randint(1000, 9999)
        transaction=Transaction.objects.create(
            transaction_id=f'TransactionID{t_id}',
            sender=user,
            receiver=other_user,
            food=food
            )
        response=self.client.post(
            reverse("verify-payment",kwargs={"reference":"yCmB555R3","transaction_id":transaction.transaction_id,"username1":self.username,"username2":"oluwapelumi","id":food.id}),format='json'
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)