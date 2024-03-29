# Generated by Django 4.0.4 on 2023-05-05 17:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_alter_bug_severity'),
    ]

    operations = [
        migrations.AddField(
            model_name='bug',
            name='is_predicted',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='bug',
            name='severity',
            field=models.CharField(choices=[('MINOR', 'MINOR'), ('NORMAL', 'NORMAL'), ('MAJOR', 'MAJOR'), ('CRITICAL', 'CRITICAL'), ('BLOCKER', 'BLOCKER')], max_length=20, null=True),
        ),
    ]
