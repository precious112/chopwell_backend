# Generated by Django 4.0.5 on 2022-06-22 09:13

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('foods', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='food',
            name='orders',
            field=models.ManyToManyField(blank=True, related_name='user_orders', to=settings.AUTH_USER_MODEL),
        ),
    ]
