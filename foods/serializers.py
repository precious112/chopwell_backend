from rest_framework import serializers
from .models import Food,Transaction,Orders
from django.contrib.auth.models import User


class UserNameSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=('id','username')
        
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model=Orders
        fields=('food','orderer')
    def to_representation(self,instance):
        rep = super().to_representation(instance)
        rep['orderer']=UserNameSerializer(instance.orderer).data
        return rep

class FoodSerializer(serializers.ModelSerializer):
    ordered_food=OrderSerializer(many=True,read_only=True)
    class Meta:
        model=Food
        fields=('profile','name','image','count','price','available','date','ordered_food')
        
class TransactionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=Transaction
        fields=('transaction_id','sender','receiver','date','amount','num_of_orders','food','reference','refund','failed','confirm')
        
    def to_representation(self,instance):
        rep = super().to_representation(instance)
        rep['sender']=UserNameSerializer(instance.sender).data
        rep['receiver']=UserNameSerializer(instance.receiver).data
        rep['food']=FoodSerializer(instance.food).data
        return rep
    
class ConfirmSerializer(serializers.Serializer):
    value=serializers.CharField()
    
    

    
        
    