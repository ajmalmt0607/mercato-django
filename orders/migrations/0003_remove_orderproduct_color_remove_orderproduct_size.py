# Generated by Django 4.2.7 on 2024-09-19 05:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_order_address_line_2_order_city_order_state_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderproduct',
            name='color',
        ),
        migrations.RemoveField(
            model_name='orderproduct',
            name='size',
        ),
    ]
