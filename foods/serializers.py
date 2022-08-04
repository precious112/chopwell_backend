from rest_framework import serializers
from .models import Food,Transaction,Orders,FoodDetail
from django.contrib.auth.models import User


class UserNameSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=('id','username')
        
class FoodDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model=FoodDetail
        fields='__all__'
        
class OrderSerializer(serializers.ModelSerializer):
    order=FoodDetailSerializer(many=True,read_only=True)
    class Meta:
        model=Orders
        fields=('orderer','total_orders','total_amount','paid','order')
    def to_representation(self,instance):
        rep = super().to_representation(instance)
        rep['orderer']=UserNameSerializer(instance.orderer).data
        return rep

class FoodSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=Food
        fields=('profile','name','image','count','price','available','date')
        
class TransactionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=Transaction
        fields=('transaction_id','sender','receiver','date','order','reference','refund','failed','confirm')
        
    def to_representation(self,instance):
        rep = super().to_representation(instance)
        rep['sender']=UserNameSerializer(instance.sender).data
        rep['receiver']=UserNameSerializer(instance.receiver).data
        rep['order']=OrderSerializer(instance.order).data
        return rep
    
class ConfirmSerializer(serializers.Serializer):
    value=serializers.CharField()
    
    

    
        
    