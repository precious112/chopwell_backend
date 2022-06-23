from rest_framework.test import APITestCase,APIClient
from users.models import Profile,OTP
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status

''' to run tests you have to add the verification code to register
 and forget password APIView response. And also disable API key
 header permissions to run tests successfully. '''

class TestUserModel(APITestCase):
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
        
        
    def test_forget_password(self):
        self.authenticate()
        response=self.client.post(
            reverse("forget-password",kwargs={"email":"precious@gmail.com"})
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_create_password(self):
        self.authenticate()
        response=self.client.post(
            reverse("forget-password",kwargs={"email":"precious@gmail.com"})
            )
        response1=self.client.post(
            reverse("verify"),{"otp":response.data['code'],"username":self.username},format='json'
            )
        response2=self.client.post(
            reverse("create-password"),{"username":self.username,"password":"password"},format='json'
            )
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        
    def test_fail_forget_password(self):
        self.authenticate()
        response=self.client.post(
            reverse("forget-password",kwargs={"email":"precious4@gmail.com"})
            )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_fail_create_password(self):
        self.authenticate()
        response=self.client.post(
            reverse("forget-password",kwargs={"email":"precious@gmail.com"})
            )
        response1=self.client.post(
            reverse("verify"),{"otp":response.data['code'],"username":self.username},format='json'
            )
        response2=self.client.post(
            reverse("create-password"),{"username":"hakeem","password":"password"},format='json'
            )
        self.assertEqual(response2.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_create_profile(self):
        self.authenticate()
        response=self.client.post(
            reverse("create-profile",kwargs={"username":self.username}),format='json'
            )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
    def test_profile_create_profile(self):
        self.authenticate()
        response=self.client.post(
            reverse("create-profile",kwargs={"username":"oluwapelumi"}),format='json'
            )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_fail_create_profile(self):
        self.authenticate()
        response=self.client.post(
            reverse("create-profile",kwargs={"username":self.username}),format='json'
            )
        response1=self.client.post(
            reverse("create-profile",kwargs={"username":self.username}),format='json'
            )
        self.assertEqual(response1.status_code, status.HTTP_204_NO_CONTENT)
        
    def test_get_profile(self):
        self.authenticate()
        self.client.post(
            reverse("create-profile",kwargs={"username":self.username}),format='json'
            )
        response=self.client.get(
            reverse("get-profile",kwargs={"username":self.username}),format='json'
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_get_near_vendors(self):
        self.authenticate()
        response=self.client.post(
            reverse("create-profile",kwargs={"username":self.username}),format='json'
            )
        location={
    "location":{"type": "Point",
    "coordinates":[7.251070,5.203540]
    }
}
        self.client.patch(
            reverse("update-profile",kwargs={"pk":response.data['data']['id']}),location,format='json'
            )
        response1=self.client.get(
            reverse("get-near-vendors",kwargs={"username":self.username}),format='json'
            )
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        
        
    def test_get_rated_vendors(self):
        self.authenticate()
        self.client.post(
            reverse("create-profile",kwargs={"username":self.username}),format='json'
            )
        response=self.client.get(
            reverse("get-rated-vendors",kwargs={"id":self.id}),format='json'
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_rate_vendor(self):
        self.authenticate()
        user=User.objects.create(username="bola",email="prepre@gmail.com")
        profile=Profile.objects.create(user=user,is_vendor=True)
        response=self.client.post(
            reverse("rate-vendor",kwargs={"vendor":"bola","rate":1}),format='json'
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_fail_rate_vendor(self):
        self.authenticate()
        
        response=self.client.post(
            reverse("rate-vendor",kwargs={"vendor":"bola","rate":1}),format='json'
            )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_fail_profile_rate_vendor(self):
        self.authenticate()
        user=User.objects.create(username="bola",email="prepre@gmail.com")
        #profile=Profile.objects.create(user=user,is_vendor=True)
        response=self.client.post(
            reverse("rate-vendor",kwargs={"vendor":"bola","rate":1}),format='json'
            )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_logout(self):
        self.authenticate()
        response=self.client.post(
            reverse("logout",kwargs={"username":self.username}),format='json'
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        
        
        
                   
        
        
    