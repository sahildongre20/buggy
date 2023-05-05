from django.test import TestCase, Client
from django.urls import reverse
from core.models import (
    Project,
    User,
    Bug,
    BUG_STATUS_CHOICES,
    PRIORITY_CHOICES,
    SEVERITY_CHOICES,
)


class ProjectModelTestCase(TestCase):
    def setUp(self):
        self.project = Project.objects.create(
            name="Test Project", description="Test description"
        )

    def test_project_name(self):
        self.assertEqual(str(self.project), "Test Project")


class UserModelTestCase(TestCase):
    def setUp(self):
        self.project = Project.objects.create(name="Test Project")
        self.user = User.objects.create(
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            role="TM",
            assigned_to=self.project,
        )

    def test_user_full_name(self):
        self.assertEqual(str(self.user), "testuser")
        self.assertEqual(self.user.full_name, "Test User")
        self.assertEqual(self.user.role, "TM")


class BugModelTestCase(TestCase):
    def setUp(self):
        self.project = Project.objects.create(name="Test Project")
        self.user = User.objects.create(
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            role="TM",
            assigned_to=self.project,
        )
        self.bug = Bug.objects.create(
            title="Test Bug",
            description="Test description",
            status="NEW",
            assigned_to=self.user,
            submitted_by=self.user,
            project=self.project,
            priority="LOW",
        )

    def test_bug_title(self):
        self.assertEqual(str(self.bug), "Test Bug")
        self.assertEqual(self.bug.status, "NEW")
        self.assertEqual(self.bug.priority, "LOW")


from django.test import TestCase
from django.urls import reverse
from core.models import Bug, Project, User


class AuthorizationTestCase(TestCase):
    def setUp(self):
        # Create a project and some users
        self.project1 = Project.objects.create(name="Project 1")
        self.project2 = Project.objects.create(name="Project 2")
        self.user1 = User.objects.create_user(
            username="user1", password="password1", email="user1@mail.com"
        )
        self.user2 = User.objects.create_user(
            username="user2", password="password2", email="user2@mail.com"
        )
        self.user3 = User.objects.create_user(
            username="user3", password="password3", email="user3@mail.com"
        )
        self.user1.role = "O"  # Set user1 as project owner for project1
        self.user1.assigned_to = self.project1
        self.user1.save()
        self.user2.assigned_to = self.project1
        self.user2.save()
        self.user3.assigned_to = self.project2
        self.user3.save()

        # Create bugs assigned to different users and projects
        self.bug1 = Bug.objects.create(
            title="Bug 1", project=self.project1, submitted_by=self.user2
        )
        self.bug2 = Bug.objects.create(
            title="Bug 2", project=self.project2, submitted_by=self.user3
        )

    def test_user_can_only_see_bugs_for_their_projects(self):
        # Login as user1 (project owner for project1) and try to access bugs for project2
        self.client.login(username="user1", password="password1")
        response = self.client.get(reverse("bugs_list"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Bug 2")

        # Login as user2 (team member for project1) and try to access bugs for project2
        self.client.login(username="user2", password="password2")
        response = self.client.get(reverse("bugs_list"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Bug 2")

        # Login as user3 (team member for project2) and try to access bugs for project1
        self.client.login(username="user3", password="password3")
        response = self.client.get(reverse("bugs_list"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Bug 1")
