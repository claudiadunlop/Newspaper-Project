from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

class UsersManagersTests(TestCase):
    def test_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpass1234",
        )
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "testuser@example.com")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        
    def test_create_superuser(self):
        User = get_user_model()
        admin_user = User.objects.create_superuser(
            username="testsuperuser",
            email="testsuperuser@example.com",
            password="testpass1234",
        )
        self.assertEqual(admin_user.username, "testsuperuser")
        self.assertEqual(admin_user.email, "testsuperuser@example.com")
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)



class SignupPageTests(TestCase):
    def test_url_exists_at_correct_location_signupview(self):
        response = self.client.get("/accounts/signup/")
        self.assertEqual(response.status_code, 200)

    def test_signup_view_name(self):
        response = self.client.get(reverse("signup"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/signup.html")

    def test_signup_form(self):
        response = self.client.post(
        reverse("signup"),
        {
            "username": "testuser",
            "email": "testuser@email.com",
            "password1": "testpass123",
            "password2": "testpass123",
        },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(get_user_model().objects.all().count(), 1)
        self.assertEqual(get_user_model().objects.all()[0].username, "testuser")
        self.assertEqual(
            get_user_model().objects.all()[0].email, "testuser@email.com"
        )

    def test_signup_creates_a_regular_user(self):
        response = self.client.post(
            reverse("signup"),
            {
                "username": "newreader",
                "email": "reader@example.com",
                "password1": "reader-password-123",
                "password2": "reader-password-123",
            },
        )
        self.assertEqual(response.status_code, 302)
        user = get_user_model().objects.get(username="newreader")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_regular_user_can_log_in_and_log_out(self):
        user = get_user_model().objects.create_user(
            username="reader",
            password="reader-password-123",
        )

        login_response = self.client.post(
            reverse("login"),
            {"username": "reader", "password": "reader-password-123"},
        )
        self.assertRedirects(login_response, reverse("home"))
        self.assertTrue(self.client.session.get("_auth_user_id"))

        logout_response = self.client.post(reverse("logout"))
        self.assertRedirects(logout_response, reverse("home"))
        self.assertNotIn("_auth_user_id", self.client.session)
