# Generated by Django 5.1.1 on 2024-10-06 17:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webstore', '0002_flashsale_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='flashsale',
            name='product',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='sale', to='webstore.productitem'),
        ),
    ]
