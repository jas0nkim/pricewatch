# Generated by Django 3.0.7 on 2020-06-05 03:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0014_item_itemprice'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='upc',
            field=models.SmallIntegerField(blank=True, null=True),
        ),
    ]
