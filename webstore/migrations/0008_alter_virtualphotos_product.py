# Generated by Django 5.1.1 on 2024-10-06 21:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webstore', '0007_alter_userphotos_product_alter_userphotos_user_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='virtualphotos',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='virtual_photos', to='webstore.productitem'),
        ),
    ]