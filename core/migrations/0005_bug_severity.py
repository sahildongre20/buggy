# Generated by Django 4.0.4 on 2023-02-17 18:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_bug_added_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='bug',
            name='severity',
            field=models.CharField(default='Not Set', max_length=20),
            preserve_default=False,
        ),
    ]