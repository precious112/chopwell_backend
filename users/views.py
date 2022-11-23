from django.shortcuts import render
from django.contrib.auth import authenticate
from rest_framework.response import Response
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer,VerifySerializer,UpdatePasswordSerializer,ProfileSerializer,UserProfileSerializer
from django.contrib.auth.models import User
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import AllowAny
from rest_framework import generics, permissions,status
from .models import OTP
import random
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.authtoken.models import Token
from .models import Profile,Premium
from django.contrib.gis.measure import D
from django.contrib.gis.geos import *
import json,requests
from rest_framework import filters
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework_api_key.permissions import HasAPIKey
from .calculate_distance import dis

# Create your views here.
class RegisterAPI(generics.GenericAPIView):
    permission_classes = [HasAPIKey]
    serializer_class = RegisterSerializer
    
    def post(self,request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user.is_active=False
        user.save()
        code_list=[]
        for i in range(7):
            n=random.randint(0, 9)
            code_list.append(n)
        code=''.join(str(item) for item in code_list)
        print("code",code)
        try:
            old_otp=OTP.objects.get(user=user)
            old_otp.delete()
            new_otp=OTP.objects.create(user=user, code=code)
            
        except OTP.DoesNotExist:
            new_otp=OTP.objects.create(user=user, code=code)
        message='your chopwell verification code is ' +code
        print(user.email)
        send_mail('Verify your account', 
                  message, settings.EMAIL_HOST_USER,
                  [user.email])
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "message":"you have successfully registered!",
            "code":code
            },status=status.HTTP_201_CREATED)
@swagger_auto_schema(
    method='post',
    request_body=VerifySerializer,
     tags=['Users']
    )    
@api_view(['POST'])
@permission_classes([HasAPIKey])
def Verify(request):
    serializer=VerifySerializer(data=request.data) 
    serializer.is_valid(raise_exception=True)
    if OTP.objects.filter(code=serializer.data['otp']).exists():
        try:
            user=User.objects.get(username=serializer.data['username']) 
            user.is_active=True 
            user.save()
            token=None
            if Token.objects.filter(user=user).exists():
                token=Token.objects.filter(user=user).first()
            else:
                token=Token.objects.create(user=user) 
            return Response({"message":"verification successfull",
                         "token":token.key
                         }
                        ,status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response("user does not exist",status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({"message":"verification code incorrect,try again"}
                        ,status=status.HTTP_400_BAD_REQUEST)
    
class LoginAPI(generics.GenericAPIView):
    permission_classes = [HasAPIKey]
    serializer_class =LoginSerializer
    
    def post(self,request):
        serializer=self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user=None
        token=None
        user = serializer.validated_data
        try:
           token=Token.objects.get(user=user) 
        except Token.DoesNotExist:
            token=Token.objects.create(user=user)
        return Response({"message":"you've successfully logged in",
                         "token":token.key
                         },
                        status=status.HTTP_200_OK)
    
@api_view(['POST'])
@permission_classes([HasAPIKey])
def ForgetPassword(request,email):
    user=User.objects.filter(email=email).first()
    code_list=[] 
    for i in range(7): 
        n=random.randint(0, 9) 
        code_list.append(n)
    code=''.join(str(item) for item in code_list)
    print("code",code)
    if user==None:
        return Response({"message":"user with email doesn't exist"},status=status.HTTP_404_NOT_FOUND)
    try: 
        old_otp=OTP.objects.get(user=user) 
        old_otp.delete() 
        new_otp=OTP.objects.create(user=user, code=code)
            
    except OTP.DoesNotExist: 
        new_otp=OTP.objects.create(user=user, code=code)
    message='your chopwell verification code is ' +code
    send_mail('Verify your account', 
                  message, settings.EMAIL_HOST_USER,
                  [user.email])
    return Response({
            "user": UserSerializer(user).data,
            "message":"verification code sent!",
            "code":code
            },status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username','password'],
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING),
                'password':openapi.Schema(type=openapi.TYPE_STRING)
            },
        ),
    responses={200:UserSerializer},
        security=[],
        tags=['Users'],
    )
@api_view(['POST'])
@permission_classes([HasAPIKey])
def createPassword(request):
    serializer=UpdatePasswordSerializer(data=request.data)
    serializer.is_valid()
    try:
        user=User.objects.get(username=serializer.data['username'])
        user.set_password(serializer.data['password'])
        user.save()
        return Response({"message":"pin successfully saved",
                         "user":UserSerializer(user).data
                         
                         },status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({"message":"user you're setting the pin for is inexistent"},
                        status=status.HTTP_404_NOT_FOUND)
    
    

@api_view(['GET'])
def get_profile(request,username):
    try:
       user=User.objects.get(username=username)
       try:
          profile=Profile.objects.get(user=user)
          serializer=ProfileSerializer(profile) 
          return Response(serializer.data,status=status.HTTP_200_OK)
       except Profile.DoesNotExist:
           return Response({"not found":"profile doesn't exist"},status=status.HTTP_404_NOT_FOUND)
       
    except User.DoesNotExist:
        return Response({"message":"user doesn't exist"},status=status.HTTP_404_NOT_FOUND)
    

@api_view(['POST'])
def create_profile(request,username):
    user=User.objects.filter(username=username).first()
    if user==None:
        return Response({"message":"user doesn't exist"},status=status.HTTP_404_NOT_FOUND)
    if Profile.objects.filter(user=user).exists():
        return Response({"message":"profile exists already"},status=status.HTTP_204_NO_CONTENT)
    else:
        profile=Profile.objects.create(user=user)
        profile.save()
        serializer=ProfileSerializer(profile) 
        return Response({"message":"profile created successfully","data":serializer.data},status=status.HTTP_201_CREATED)
    
    
class UpdateProfile(generics.UpdateAPIView):
    queryset=Profile.objects.all()
    serializer_class=ProfileSerializer
     
    
        
@api_view(['GET'])
def GetNearVendors(request,username):
    try:
        user=User.objects.get(username=username)
        try: 
            profile=Profile.objects.get(user=user) 
            user_location=(profile.latitude,profile.longitude)
            vendors=Profile.objects.all().exclude(is_vendor=False).exclude(latitude=None,longitude=None)
            near_vendors=vendors
            for vendor in vendors.iterator():
                vendor_location=(vendor.latitude,vendor.longitude)
                distance=dis(user_location,vendor_location)
                if distance>5:
                    near_vendors.exclude(user=vendor.user)
            serializer=ProfileSerializer(near_vendors,many=True) 
            return Response(serializer.data,status=status.HTTP_200_OK)
        except Profile.DoesNotExist:
           return Response({"message":"profile doesn't exist"},status=status.HTTP_404_NOT_FOUND)
    
    except User.DoesNotExist:
        return Response({"message":"user doesn't exist"},status=status.HTTP_404_NOT_FOUND)
    
@api_view(['GET'])
def GetPremiumVendors(request,username):
    try:
        user=User.objects.get(username=username)
        try: 
            profile=Profile.objects.get(user=user)
            user_location=(profile.latitude,profile.longitude)
            profiles=Profile.objects.filter(is_vendor=True,premium=True)
            profiles.exclude(location=None).exclude(latitude=None,longitude=None)
            premium_profiles=profiles
            for profile in profiles.iterator():
                vendor_location=(profile.latitude,profile.longitude)
                distance=dis(user_location,vendor_location)
                if distance>15:
                    premium_profiles.exclude(user=profile.user)
            serializer=ProfileSerializer(premium_profiles,many=True) 
            return Response(serializer.data,status=status.HTTP_200_OK)
        except Profile.DoesNotExist:
           return Response({"message":"profile doesn't exist"},status=status.HTTP_404_NOT_FOUND)
    
    except User.DoesNotExist:
        return Response({"message":"user doesn't exist"},status=status.HTTP_404_NOT_FOUND)
    
    
@api_view(['GET'])
def GetRatedVendors(request,id): 
    try:
        user=User.objects.get(id=id)
        profiles=Profile.objects.filter(rating__in=[user])
        serializer=ProfileSerializer(profiles,many=True) 
        return Response(serializer.data,status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({"message":"user doesn't exist"},status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def SetUpUserPayStackTransferPayment(request,username):
    try:
        user=User.objects.get(username=username)
        try:
            profile=Profile.objects.get(user=user)
            url='https://api.paystack.co/transferrecipient' 
            headers = {
            'Authorization': 'Bearer '+settings.PAYSTACK_SECRET_KEY, 
            'Content-Type' : 'application/json', 
            'Accept': 'application/json',
            
            }
            data={
                "type": "nuban",
                "name": f'{user.first_name} {user.last_name}',
                "account_number": f'{profile.account_name}',
                "bank_code": "011",
                "currency": "NGN"
                
                }
            resp=requests.post(url,headers=headers,data=json.dumps(data))
            response=resp.json()
            if resp.json()['message'] == 'Transfer recipient created successfully':
                profile.recipient_code=response['data']['recipient_code']
                profile.save()
                serializer=ProfileSerializer()
                return Response({"paystack":response,
                                 "data":serializer.data
                                 },status=status.HTTP_201_CREATED)
            return Response(response,status=status.HTTP_400_BAD_REQUEST)
        except Profile.DoesNotExist:
            return Response({"message":"profile doesn't exist"},status=status.HTTP_404_NOT_FOUND)
    except User.DoesNotExist:
        return Response({"message":"user doesn't exist"},status=status.HTTP_404_NOT_FOUND)
    
@api_view(['POST'])
def RateVendors(request,vendor,rate):
    try:
        vendor=User.objects.get(username=vendor)
        try:
            vendor_profile=Profile.objects.get(user=vendor)
            if request.user in vendor_profile.rating.all() or vendor_profile.negative_rating.all():
                pass
            else:
                if rate==1:
                    vendor_profile.rating.add(request.user)
                    vendor_profile.save()
                if rate==0:
                    vendor_profile.negative_rating.add(request.user)
                    vendor_profile.save()
                serializer=ProfileSerializer(vendor_profile)
                return Response(serializer.data,status=status.HTTP_200_OK)
        except Profile.DoesNotExist:
            return Response({"message":"profile doesn't exist"},status=status.HTTP_404_NOT_FOUND)
    except User.DoesNotExist:
        return Response({"message":"user doesn't exist"},status=status.HTTP_404_NOT_FOUND)
    
    
class SearchVendor(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class=UserProfileSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['username']
    
    
@api_view(['POST'])
def Logout(request,username):
    try:
        user=User.objects.get(username=username)
        if request.user==user:
            try:
                token=Token.objects.get(user=user)
                token.delete()
                return Response("user logged out successfully",status=status.HTTP_200_OK)
            except Token.DoesNotExist:
                return Response("invalid request!",status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("can't carry out this request,wrong user",status=status.HTTP_401_UNAUTHORIZED)
    except User.DoesNotExist:
        return Response({"message":"user doesn't exist"},status=status.HTTP_404_NOT_FOUND)
            

