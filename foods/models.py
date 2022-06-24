from django.db import models
from PIL import Image
from users.models import Profile
from django.contrib.auth.models import User
from django.utils import timezone
from cloudinary.models import CloudinaryField

# Create your models here.
#NB:count field in food model is to show how many quantity of a certain food is available for sale
class Food(models.Model):
    profile=models.ForeignKey(Profile, on_delete=models.CASCADE,blank=True,null=True)
    name=models.CharField(max_length=110)
    image=models.ImageField(null=True,blank=True)
    count=models.IntegerField(default=0)
    price=models.DecimalField(max_digits=10, decimal_places=2,default=0.00)
    available=models.BooleanField(default=True)
    date=models.DateTimeField(default=timezone.now)
    
    def __str__(self): 
        return f'{self.name}'
    
class Transaction(models.Model):
    transaction_id=models.CharField(max_length=17,unique=True)
    reference=models.CharField(max_length=100,default='')
    reference_two=models.CharField(max_length=100,default='')
    transfer_code=models.CharField(max_length=100,blank="")
    sender=models.ForeignKey(User, on_delete=models.CASCADE,related_name='sender')
    receiver=models.ForeignKey(User, on_delete=models.CASCADE,related_name='receiver')
    date=models.DateTimeField(default=timezone.now)
    amount=models.DecimalField(max_digits=10, decimal_places=2,default=0.00)
    num_of_orders=models.IntegerField(default=0,null=True,blank=True)
    food=models.ForeignKey(Food,null=True,on_delete=models.CASCADE)
    refund=models.BooleanField(default=False)
    status=models.CharField(max_length=20,default="pending")
    failed=models.BooleanField(default=False)
    confirm=models.BooleanField(default=False)
    
    def __str__(self): 
        return f'{self.transaction_id}'
    
    
class Orders(models.Model):
    food=models.ForeignKey(Food, on_delete=models.CASCADE,related_name='ordered_food')
    orderer=models.ForeignKey(User,on_delete=models.CASCADE,related_name='food_orderer')
    
    def __str__(self): 
        return f'{self.food.name} order'