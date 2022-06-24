from django.contrib import admin
from .models import Food,Transaction,Orders

# Register your models here.
admin.site.register(Food)
admin.site.register(Transaction)
admin.site.register(Orders)