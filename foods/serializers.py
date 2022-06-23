from rest_framework import serializers
from .models import Food,Transaction
from django.contrib.auth.models import User


class UserNameSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=('id','username')

class FoodSerializer(serializers.ModelSerializer):
    class Meta:
        model=Food
        fields=  '__all__'
        
class TransactionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=Transaction
        fields=('transaction_id','sender','receiver','date','amount','food','reference','refund','failed','confirm')
        
    def to_representation(self,instance):
        rep = super().to_representation(instance)
        rep['sender']=UserNameSerializer(instance.sender).data
        rep['receiver']=UserNameSerializer(instance.receiver).data
        rep['food']=FoodSerializer(instance.food).data
        return rep
    
class ConfirmSerializer(serializers.Serializer):
    value=serializers.CharField()