from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post
from .const import (
    AUTHOR_USERNAME,
    GROUP_SLUG,
    URL_INDEX,
    URL_GROUP,
    URL_AUTHOR_PROFILE,
    URL_CREATE_POST,
)

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author_user = User.objects.create_user(username=AUTHOR_USERNAME)
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug=GROUP_SLUG,
            description="Тестовое описание группы",
        )
        cls.post = Post.objects.create(
            text="Тестовый текст поста",
            author=cls.author_user,
            group=cls.group,
        )
        cls.POST_URL = reverse("posts:post_detail", args=[cls.post.id])
        cls.POST_EDIT_URL = reverse("posts:post_edit", args=[cls.post.id])

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(PostPagesTests.author_user)

    def check_post_info(self, post):
        self.assertEqual(post.text, PostPagesTests.post.text)
        self.assertEqual(post.author, PostPagesTests.post.author)
        self.assertEqual(post.group, PostPagesTests.post.group)
        self.assertEqual(post.pk, PostPagesTests.post.pk)

    def test_create_edit_pages_show_correct_context(self):
        """Проверка коректности формы."""
        adresses = (URL_CREATE_POST, PostPagesTests.POST_EDIT_URL)
        for adress in adresses:
            with self.subTest(adress=adress):
                response = self.author_client.get(adress)
                self.assertIsInstance(
                    response.context["form"].fields["text"],
                    forms.fields.CharField,
                )
                self.assertIsInstance(
                    response.context["form"].fields["group"],
                    forms.fields.ChoiceField,
                )

    def test_post_pages_show_correct_context(self):
        """
        Страницы создаются с  верным контекст
        """
        addresses = [
            URL_INDEX,  # страница с пагинацией. В контексте 'page_obj'
            URL_GROUP,  # страница с пагинацией. В контексте 'page_obj'
            URL_AUTHOR_PROFILE,  # с пагинацией. В контексте 'page_obj'
            PostPagesTests.POST_URL,  # без пагинации. В контексте 'post'
        ]
        for adress in addresses:
            response = self.author_client.get(adress)
            if (
                "page_obj" in response.context
            ):  # мы используем "in", чтобы в правильно сформировать post.
                # Так как на странице детального поста, нет 'page obj'.
                post = response.context.get("page_obj")[
                    0
                ]  # если использовать assertIn, то тест для страницы
            else:  # детального поста всегда будет "падать"
                post = response.context.get("post")
            self.check_post_info(post)

    def test_group_page_show_correct_context(self):
        group = self.author_client.get(URL_GROUP).context.get("group")
        self.assertEqual(group.title, PostPagesTests.group.title)
        self.assertEqual(group.slug, PostPagesTests.group.slug),
        self.assertEqual(group.pk, PostPagesTests.group.pk),
        self.assertEqual(group.description, PostPagesTests.group.description)

    def test_profile_page_show_correct_context(self):
        author = self.author_client.get(URL_AUTHOR_PROFILE).context.get(
            "author"
        )
        self.assertEqual(author.username, PostPagesTests.author_user.username)
        self.assertEqual(author.pk, PostPagesTests.author_user.pk)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username=AUTHOR_USERNAME)
        cls.group = Group.objects.create(
            title="Тестовое название группы",
            slug=GROUP_SLUG,
            description="Тестовое описание группы",
        )
        cls.PAGES_WITH_PAGINATOR = [URL_INDEX, URL_GROUP, URL_AUTHOR_PROFILE]
        objs = [
            Post(text=f"Пост #{i}", author=cls.user, group=cls.group)
            for i in range(13)
        ]
        Post.objects.bulk_create(objs)

    def setUp(self):
        self.unauthorized_client = Client()

    def test_paginator_on_pages(self):
        """Проверка пагинации на страницах."""
        posts_on_first_page = 10
        posts_on_second_page = 3
        for reverse_address in PaginatorViewsTest.PAGES_WITH_PAGINATOR:
            with self.subTest(reverse_address=reverse_address):
                self.assertEqual(
                    len(
                        self.unauthorized_client.get(
                            reverse_address
                        ).context.get("page_obj")
                    ),
                    posts_on_first_page,
                )
                self.assertEqual(
                    len(
                        self.unauthorized_client.get(
                            reverse_address + "?page=2"
                        ).context.get("page_obj")
                    ),
                    posts_on_second_page,
                )
