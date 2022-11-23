from django.contrib.gis.db import models as g_models
from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from django.core.validators import FileExtensionValidator
from django.utils import timezone
from django.conf import settings
from cloudinary.models import CloudinaryField

DAILY="daily"
MONTHLY="monthly"
YEARLY="yearly"
PREMIUM_PLANS= [
    (DAILY,750.00),
    (MONTHLY,15000.00),
    (YEARLY,70000.00)
    ]

# Create your models here.
class Profile(models.Model):
    user= models.OneToOneField(User,on_delete=models.CASCADE)
    image=models.ImageField(null=True,blank=True)
    is_vendor=models.BooleanField(default=False)
    debit=models.DecimalField(max_digits=10, decimal_places=2,default=0.00)
    balance=models.DecimalField(max_digits=10, decimal_places=2,default=0.00)
    account_number=models.CharField(max_length=12,blank=True)
    recipient_code=models.CharField(max_length=50,blank=True)
    longitude=models.CharField(max_length=100,blank=True)
    latitude=models.CharField(max_length=100,blank=True)
    country=models.CharField(max_length=50,default="nigeria")
    state=models.CharField(max_length=50,blank=True)
    city=models.CharField(max_length=50,blank=True)
    address=models.CharField(max_length=50,blank=True)
    premium=models.BooleanField(default=False)
    rating=models.ManyToManyField(User,related_name='ratings',blank=True,null=True)
    negative_rating=models.ManyToManyField(User,related_name='negativeratings',blank=True,null=True)
    contact=models.CharField(max_length=15,blank=True)
    
    def __str__(self): 
        return f'{self.user.username} Profile'
    
class OTP(models.Model):
    code=models.CharField(max_length=7)
    user=models.OneToOneField(User,  on_delete=models.CASCADE)
    
    
class Premium(models.Model):
    profile=models.OneToOneField(Profile,on_delete=models.CASCADE,related_name='premium_user')
    plan=models.CharField(max_length=30,choices=PREMIUM_PLANS,default=DAILY)
    start_date=models.DateTimeField()
    end_date=models.DateTimeField()
    active=models.BooleanField()
    
    
    
    
#IMP:add address field and contact
