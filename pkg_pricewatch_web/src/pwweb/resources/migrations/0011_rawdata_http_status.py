# Generated by Django 3.0.5 on 2020-05-08 03:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0010_rawdata'),
    ]

    operations = [
        migrations.AddField(
            model_name='rawdata',
            name='http_status',
            field=models.SmallIntegerField(blank=True, null=True),
        ),
    ]
