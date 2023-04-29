# Generated by Django 4.0.4 on 2023-04-29 10:25

from django.db import transaction
from django.db import migrations
from django.db import migrations
from faker import Faker
from core.models import User, Project

fake = Faker()


@transaction.atomic
def add_initial_data(apps, schema_editor):
    # add users
    try:
        project = Project.objects.create(
            name='Bug Severity Prediction Project',
            description='This project is for predicting bug severity'
        )

        # Create 10 dummy users and assign them to the project
        for _ in range(10):
            first_name = fake.first_name()
            last_name = fake.last_name()
            user = User.objects.create(
                first_name=first_name,
                last_name=last_name,
                full_name=f'{first_name} {last_name}',
                email=fake.unique.email(),
                assigned_to=project,
                password='dummy_password',
                username=fake.unique.first_name(),
                role='TM'
            )

            # execute queries here
    except Exception as e:
        # handle the exception here
        raise e


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_alter_bug_severity'),
    ]

    operations = [
        migrations.RunPython(add_initial_data),
    ]