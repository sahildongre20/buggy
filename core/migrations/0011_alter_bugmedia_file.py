# Generated by Django 4.0.4 on 2023-05-03 06:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_bugmedia'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bugmedia',
            name='file',
            field=models.FileField(upload_to='static'),
        ),
    ]
