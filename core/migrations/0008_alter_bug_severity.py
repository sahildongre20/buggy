# Generated by Django 4.0.4 on 2023-04-29 05:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_alter_user_managers_alter_bug_severity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bug',
            name='severity',
            field=models.CharField(max_length=20, null=True),
        ),
    ]
