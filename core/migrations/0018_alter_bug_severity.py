# Generated by Django 4.0.4 on 2023-05-05 17:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_comments'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bug',
            name='severity',
            field=models.CharField(choices=[('minor', 'MINOR'), ('normal', 'NORMAL'), ('major', 'MAJOR'), ('critical', 'CRITICAL'), ('blocker', 'BLOCKER')], max_length=20, null=True),
        ),
    ]