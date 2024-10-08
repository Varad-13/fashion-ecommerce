# Generated by Django 5.1.1 on 2024-10-06 19:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webstore', '0005_category_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productitem',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='webstore.category'),
        ),
    ]
