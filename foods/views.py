from django.shortcuts import render
from rest_framework.response import Response
from .serializers import FoodSerializer,TransactionSerializer,ConfirmSerializer,OrderSerializer
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import AllowAny
from rest_framework import generics, permissions,status
from .models import Food,Transaction,Orders,FoodDetail
from users.models import Profile
from users.serializers import ProfileSerializer
from rest_framework import viewsets, filters
from django.contrib.auth.models import User
import json,requests
import random
from django.conf import settings
from django.db import transaction
from django.db.models import F,Q
from django.shortcuts import get_object_or_404

# Create your views here.
class CreateFood(generics.CreateAPIView):
    queryset=Food.objects.all()
    serializer_class=FoodSerializer
    
    
class ListVendorFoods(generics.GenericAPIView):
    serializer_class=FoodSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['date']
    def get_vendor(self,request,username):
        try:
            user=User.objects.get(username=username) 
            return user
        except User.DoesNotExist:
            user=None
            return user
    def get_vendor_profile(self,user):
        try:
            profile=Profile.objects.get(user=user)
            return profile
        except Profile.DoesNotExist:
            profile=None
            return profile
    def get(self,request,username):
        user = self.get_vendor(request,username)
        if user==None:
            return Response({"message":"vendor doesn't exist"},status=status.HTTP_404_NOT_FOUND)
        vendor=self.get_vendor_profile(user)
        if vendor==None:
            return Response({"message":"vendor profile doesn't exist"},status=status.HTTP_404_NOT_FOUND)
        if vendor.is_vendor==True:
            foods=self.filter_queryset(Food.objects.filter(profile=vendor,available=True))
            serializer=self.get_serializer(foods,many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response({"message":"user is not a vendor"},status=status.HTTP_400_BAD_REQUEST)
    
class DetailFood(generics.RetrieveAPIView):
    queryset=Food.objects.all()
    serializer_class=FoodSerializer
    
class UpdateFood(generics.UpdateAPIView):
    queryset=Food.objects.all()
    serializer_class=FoodSerializer
    
class DeleteFood(generics.DestroyAPIView):
    queryset=Food.objects.all()
    serializer_class=FoodSerializer
    
class OrderDetail(generics.RetrieveAPIView):
    queryset=Orders.objects.all()
    serializer_class=OrderSerializer

'''
normal convention: username1 is for the customer,username2 is for the vendor.

 '''

@api_view(['POST'])
@transaction.atomic
def add_to_orders(request,username1,username2,id,orders):
    food=Food.objects.filter(id=id).select_for_update()[0] 
    user1=User.objects.filter(username=username1).select_for_update()[0]
    user2=User.objects.filter(username=username2).select_for_update()[0]
    profile1=Profile.objects.filter(user=user1).select_for_update()[0]
    profile2=Profile.objects.filter(user=user2).select_for_update()[0]
    
    if Orders.objects.filter(orderer=user1,vendor=user2,paid=False).exists():
        pass
    else:
        Orders.objects.create(orderer=user1,vendor=user2)
        
    if food.available==True and food.count>=orders:
        order=Orders.objects.filter(orderer=user1,vendor=user2,paid=False).select_for_update()[0]
        ordered_food=FoodDetail.objects.create(
            food=food,
            num_of_orders=orders,
            amount=orders*food.price,
            order=order
            )
        
        food.count -= orders
        food.save()
        if food.count<=0:
            food.available=False
            food.save()
        order.total_orders+=orders
        order.total_amount+=orders*food.price
        order.save()
        return Response({"food_ordered":FoodSerializer(food).data,
                         "message":"food ordered successfully"
                         },status=status.HTTP_200_OK)
    
    else:
        return Response({"message":"sorry,out of order"},status=status.HTTP_400_BAD_REQUEST)
            
        
        
    
@api_view(['POST'])
@transaction.atomic
def pay_vendor(request,username1,username2,id,order_id):
    food=Food.objects.filter(id=id).select_for_update()[0]
    user1=User.objects.filter(username=username1).select_for_update()[0]
    user2=User.objects.filter(username=username2).select_for_update()[0]
    profile1=Profile.objects.filter(user=user1).select_for_update()[0]
    profile2=Profile.objects.filter(user=user2).select_for_update()[0]
    order=get_object_or_404(Orders,orderer=user1,vendor=user2,paid=False,id=order_id)
    
    url = 'https://api.paystack.co/transaction/initialize'
    headers = {
            'Authorization': 'Bearer '+settings.PAYSTACK_SECRET_KEY, 
            'Content-Type' : 'application/json', 
            'Accept': 'application/json',
            
            }
    amount=int(order.total_amount)
    email=str(user1.email)
    body={
                "email":email,
                "amount":amount
                }
    r=None
    r = requests.post(url, headers=headers, data=json.dumps(body))
    response = r.json()
    
    if response['message']=="Authorization URL created":
        t_id=random.randint(1000, 9999)
        while Transaction.objects.filter(transaction_id=f'TransactionID{t_id}').exists():
            t_id=random.randint(1000, 9999)
        transaction=Transaction.objects.create(
        transaction_id=f'TransactionID{t_id}',
        reference=response['data']['reference'],
        sender=user1,
        receiver=user2,
        order=order,
        status="pending"
                )
        serializer=TransactionSerializer(transaction)
        return Response({"response":response,
                                 "data":serializer.data
                                 },status=status.HTTP_200_OK)
    return Response(response,status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['POST'])
@transaction.atomic
def verify_payment(request,reference,transaction_id,username1,username2,order_id):

    order=Orders.objects.filter(id=order_id).select_for_update()[0]
    user1=User.objects.filter(username=username1).select_for_update()[0]
    user2=User.objects.filter(username=username2).select_for_update()[0]
    profile1=Profile.objects.filter(user=user1).select_for_update()[0]
    profile2=Profile.objects.filter(user=user2).select_for_update()[0]
    transaction=Transaction.objects.filter(transaction_id=transaction_id).select_for_update()[0]
    
    url = f'https://api.paystack.co/transaction/verify/{reference}'
    headers = {
    'Authorization': 'Bearer '+settings.PAYSTACK_SECRET_KEY,
    'Content-Type' : 'application/json',
    'Accept': 'application/json',
    }
    resp = requests.get(url,headers=headers)
    

    if resp.json()['data']['status'] == 'success':
        transaction.status='success'
        transaction.save()
        profile1.debit+=order.total_amount
        profile1.save()
        profile2.balance+=order.total_amount
        profile2.save()
        order.paid=True
        order.save()
        
        return Response({"message":"transaction verified successfully",
                         "response":resp.json(),
                         "transaction":TransactionSerializer(transaction).data
                         },status=status.HTTP_200_OK)
    else:
        transaction.status='failed'
        transaction.save()
        return Response(resp.json(),status=status.HTTP_400_BAD_REQUEST)
    
    
@api_view(['POST'])
@transaction.atomic
def confirm_delivery(request,transaction_id,username1,username2):
    user1=User.objects.filter(username=username1).select_for_update()[0]
    user2=User.objects.filter(username=username2).select_for_update()[0]
    profile1=Profile.objects.filter(user=user1).select_for_update()[0]
    profile2=Profile.objects.filter(user=user2).select_for_update()[0]
    transaction=Transaction.objects.filter(transaction_id=transaction_id).select_for_update()[0]
    confirm=ConfirmSerializer(data=request.data)
    confirm.is_valid()
    url='https://api.paystack.co/transfer'
    headers = {
    'Authorization': 'Bearer '+settings.PAYSTACK_SECRET,
    'Content-Type' : 'application/json',
    'Accept': 'application/json',
    }
    amount=int(transaction.amount)
    if confirm.validated_data['value']=="0":
        
        data={
            "source": "balance",
            "reason": "vendor payment",
            "amount":amount,
            "recipient":profile1.reference_code
            }
        resp = requests.post(url,headers=headers,data=json.dumps(data))
        response=resp.json()
        if response['data']['status']=='pending':
            transaction.transfer_code=response['data']['transfer_code']
            transaction.save()
        return Response({"response":response,
                         "data":profile1,
                         "message":"payment cancelation pending"
                         },status=status.HTTP_200_OK)
    
    if confirm.validated_data['value']=="1":
        data={
            "source": "balance",
            "reason": "vendor payment",
            "amount":amount,
            "recipient":profile2.reference_code
            }
        resp = requests.post(url,headers=headers,data=data)
        response=resp.json()
        if response['data']['status']=='pending':
            transaction.transfer_code=response['data']['transfer_code']
            transaction.save()
        return Response({"response":response,
                         "data":profile2,
                         "message":"payment confirmation pending"
                         },status=status.HTTP_200_OK)
    
    

        
            
@api_view(['POST'])
@transaction.atomic
def finalize_confirmation(request,transaction_id):
    transaction=Transaction.objects.filter(transaction_id=transaction_id).select_for_update()[0]
    url='https://api.paystack.co/transfer/finalize_transfer'
    headers = {
    'Authorization': 'Bearer '+settings.PAYSTACK_SECRET,
    'Content-Type' : 'application/json',
    'Accept': 'application/json',
    }
    data={
        "transfer_code":transaction.transfer_code
        }
    resp = requests.post(url,headers=headers,data=json.dumps(data))
    response=resp.json()
    if response['data']['status']=='success':
        transaction.reference_two=response['data']['reference']
        transaction.save()
    return Response(response,status=status.HTTP_200_OK)
    

@api_view(['POST'])
@transaction.atomic
def verify_confirmation(request,transaction_id,reference_two):
    profile=ProfileSerializer(data=request.data)
    profile.is_valid()
    transaction=Transaction.objects.filter(transaction_id=transaction_id).select_for_update()[0]
    url=f'https://api.paystack.co/transfer/verify/{reference_two}'
    headers = {
    'Authorization': 'Bearer '+settings.PAYSTACK_SECRET,
    'Content-Type' : 'application/json',
    'Accept': 'application/json',
    }
    resp = requests.get(url,headers=headers)
    response=resp.json()
    if response['data']['status']=='success':
        if transaction.sender==profile.user:
            profile.debit-=transaction.amount
            profile.save()
            transaction.failed=True
            transaction.save()
            return Response({"message":"payment cancellation successful",
                             "response":response},status=status.HTTP_200_OK)
        
        if transaction.receiver==profile.user:
            profile.balance+=transaction.amount
            profile.save()
            transaction.confirm=True
            transaction.save()
            return Response({"message":"payment confirmation successful",
                             "response":response},status=status.HTTP_200_OK)
        
    return Response(response,status=status.HTTP_400_BAD_REQUEST)


class UserTransactionsAPI(generics.GenericAPIView):
    serializer_class=TransactionSerializer
    ordering_fields = ['date']
    def get_transactions(self,username):
        try:
            user=User.objects.get(username=username)
            transactions=Transaction.objects.filter(Q(sender=user)|Q(receiver=user))
            return transactions
        except User.DoesNotExist:
            return Response({"message":"user doesn't exist"},status=status.HTTP_400_BAD_REQUEST)
    def get(self,request,username):
        transactions=self.filter_queryset(self.get_transactions(username))
        serializer=self.get_serializer(transactions,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
        
    
    