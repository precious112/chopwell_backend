# Generated by Django 3.2 on 2022-06-24 18:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('foods', '0004_auto_20220624_1107'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='food',
            name='orders',
        ),
        migrations.CreateModel(
            name='Orders',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('food', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ordered_food', to='foods.food')),
                ('orderer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='food_orderer', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
