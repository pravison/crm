# Generated by Django 5.1.4 on 2024-12-28 15:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ai', '0001_initial'),
        ('customers', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taskpipeline',
            name='customer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='customers.customer'),
        ),
    ]
