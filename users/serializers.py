from .models import Profile
from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_gis.serializers import GeoFeatureModelSerializer

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=('id','username','email','is_active','first_name','last_name')
        
'''class ProfileSerializer(GeoFeatureModelSerializer):
    class Meta:
        model=Profile
        geo_field = 'location'
        fields=('id','image','is_vendor','debit','balance','premium','rating','negative_rating') '''

class ProfileSerializer(GeoFeatureModelSerializer):
    class Meta:
        model=Profile
        fields=('id','image','is_vendor','debit','longitude','latitude','balance','premium','rating','negative_rating')
        
    def to_representation(self,instance):
        rep = super().to_representation(instance)
        rep['user']=UserSerializer(instance.user).data
        return rep
    
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model=User 
        fields=('id','username','email','password')
        extra_kwargs={'password':{'write_only':True}}
        
    def create(self,validated_data):
        user= User.objects.create_user(validated_data['username'],validated_data['email'],validated_data['password'])
        return user
    
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError('Incorrect Credentials Passed.')
        
class VerifySerializer(serializers.Serializer):
    otp=serializers.CharField()
    username=serializers.CharField()
    
class UpdatePasswordSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    

class UserProfileSerializer(serializers.Serializer):
    profile=ProfileSerializer()
    class Meta:
        model=User
        fields=('profile')
