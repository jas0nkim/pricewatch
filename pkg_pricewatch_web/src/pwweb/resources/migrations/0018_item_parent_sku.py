# Generated by Django 3.0.7 on 2020-06-05 21:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0017_auto_20200605_1651'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='parent_sku',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
    ]
