# Generated by Django 4.0.4 on 2023-04-29 11:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_auto_20230429_1025'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='isVerified',
            field=models.BooleanField(default=False),
        ),
    ]