# Generated by Django 3.2 on 2022-08-04 15:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('foods', '0005_auto_20220624_1158'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orders',
            name='food',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='amount',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='food',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='num_of_orders',
        ),
        migrations.AddField(
            model_name='orders',
            name='paid',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='orders',
            name='total_amount',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AddField(
            model_name='orders',
            name='total_orders',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='orders',
            name='vendor',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='order_vendor', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='transaction',
            name='order',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='transaction_order', to='foods.orders'),
        ),
        migrations.CreateModel(
            name='FoodDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('num_of_orders', models.IntegerField(blank=True, default=0, null=True)),
                ('amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('food', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ordered_food', to='foods.food')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order', to='foods.orders')),
            ],
        ),
    ]
