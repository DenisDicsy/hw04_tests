from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from http import HTTPStatus
from posts.models import Post, Group

User = get_user_model()

URL_INDEX = reverse("posts:index")
AUTHOR_USERNAME = "test_user"
GROUP_SLUG = "test_slug"
URL_GROUP = reverse("posts:group_list", args=[GROUP_SLUG])
URL_AUTHOR_PROFILE = reverse("posts:profile", args=[AUTHOR_USERNAME])
URL_CREATE_POST = reverse("posts:post_create")


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author_user = User.objects.create(
            username=AUTHOR_USERNAME,
        )
        cls.group = Group.objects.create(
            title="группа",
            slug=GROUP_SLUG,
            description="проверка описания",
        )
        cls.post = Post.objects.create(
            text="Тестовый текст",
            author=cls.author_user,
            group=cls.group,
        )
        cls.POST_URL = reverse("posts:post_detail", args=[cls.post.id])
        cls.POST_EDIT_URL = reverse("posts:post_edit", args=[cls.post.id])

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем авторизованый клиент
        self.user = User.objects.create_user(username="some_user")
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(PostURLTests.author_user)

    def test_urls_status(self):
        address_status_client = [
            [URL_INDEX, HTTPStatus.OK, self.guest_client],
            [URL_GROUP, HTTPStatus.OK, self.guest_client],
            [URL_AUTHOR_PROFILE, HTTPStatus.OK, self.guest_client],
            [URL_CREATE_POST, HTTPStatus.OK, self.authorized_client],
            [URL_CREATE_POST, HTTPStatus.FOUND, self.guest_client],
            [PostURLTests.POST_URL, HTTPStatus.OK, self.guest_client],
            [PostURLTests.POST_EDIT_URL, HTTPStatus.FOUND, self.guest_client],
            [
                PostURLTests.POST_EDIT_URL,
                HTTPStatus.FOUND,
                self.authorized_client,
            ],
            [PostURLTests.POST_EDIT_URL, HTTPStatus.OK, self.author_client],
        ]
        for test in address_status_client:
            adress, status, client = test
            self.assertEqual(
                client.get(adress).status_code,
                status,
                f"{adress} вернул другой статус код. Нежели {status}",
            )

    # Проверяем статус 404 для авторизованного пользователя
    def test_task_list_url_redirect_anonymous(self):
        """Страница /unexisting_page/ не существует."""
        response = self.authorized_client.get("/unexisting_page/")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    # Проверка вызываемых шаблонов для каждого адреса
    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            URL_INDEX: "posts/index.html",
            URL_GROUP: "posts/group_list.html",
            URL_AUTHOR_PROFILE: "posts/profile.html",
            PostURLTests.POST_URL: "posts/post_detail.html",
            PostURLTests.POST_EDIT_URL: "posts/create_post.html",
            URL_CREATE_POST: "posts/create_post.html",
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertTemplateUsed(
                    response,
                    template,
                    f"неверный шаблон - {template} для адреса {url}",
                )
