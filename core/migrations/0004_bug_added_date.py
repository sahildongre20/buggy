# Generated by Django 4.0.4 on 2022-05-02 15:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_bug'),
    ]

    operations = [
        migrations.AddField(
            model_name='bug',
            name='added_date',
            field=models.DateField(auto_now=True),
        ),
    ]