from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Article


class HomePageTests(TestCase):
    def test_url_exists_at_correct_location_homepageview(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_homepage_view(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home.html")
        self.assertContains(response, "Home")
        self.assertContains(response, "bootstrap.min.css")


class NewspaperTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.author = user_model.objects.create_user(
            username="reporter",
            password="secure-test-password",
        )
        self.reader = user_model.objects.create_user(
            username="reader",
            password="secure-test-password",
        )
        self.article = self._create_article()

    def _create_article(self, **overrides):
        values = {
            "title": "Community garden opens",
            "body": "Neighbors opened a new garden this morning.",
            "author": self.author,
        }
        values.update(overrides)
        return Article.objects.create(**values)

    def test_homepage_lists_articles_and_public_detail_is_readable(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, self.article.title)

        detail = self.client.get(
            reverse("article_detail", kwargs={"pk": self.article.pk})
        )
        self.assertEqual(detail.status_code, 200)
        self.assertContains(detail, self.article.body)

    def test_regular_user_can_publish_and_comment(self):
        self.client.login(username="reader", password="secure-test-password")
        create_response = self.client.post(
            reverse("article_new"),
            {"title": "Local team wins", "body": "A great match."},
        )
        self.assertEqual(create_response.status_code, 302)
        new_article = Article.objects.get(title="Local team wins")
        self.assertEqual(new_article.author, self.reader)

        comment_response = self.client.post(
            reverse("comment_new", kwargs={"article_pk": self.article.pk}),
            {"body": "Thanks for the report!"},
        )
        self.assertRedirects(
            comment_response,
            reverse("article_detail", kwargs={"pk": self.article.pk}),
        )
        comment = self.article.comments.get()
        self.assertEqual(comment.author, self.reader)
        self.assertEqual(comment.body, "Thanks for the report!")

    def test_article_management_requires_login_and_author_ownership(self):
        edit_url = reverse("article_edit", kwargs={"pk": self.article.pk})
        response = self.client.get(edit_url)
        self.assertRedirects(response, f"{reverse('login')}?next={edit_url}")

        self.client.login(username="reader", password="secure-test-password")
        forbidden = self.client.get(edit_url)
        self.assertEqual(forbidden.status_code, 403)

        self.client.login(username="reporter", password="secure-test-password")
        allowed = self.client.get(edit_url)
        self.assertEqual(allowed.status_code, 200)

    def test_anonymous_users_cannot_post_comments(self):
        response = self.client.post(
            reverse("comment_new", kwargs={"article_pk": self.article.pk}),
            {"body": "Anonymous comment"},
        )
        self.assertRedirects(
            response,
            f"{reverse('login')}?next="
            f"{reverse('comment_new', kwargs={'article_pk': self.article.pk})}",
        )
        self.assertEqual(self.article.comments.count(), 0)

    def test_empty_comment_shows_validation_error(self):
        self.client.login(username="reader", password="secure-test-password")
        response = self.client.post(
            reverse("comment_new", kwargs={"article_pk": self.article.pk}),
            {"body": ""},
        )
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, "This field is required.", status_code=400)
        self.assertEqual(self.article.comments.count(), 0)
