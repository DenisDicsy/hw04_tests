from django.urls import reverse


AUTHOR_USERNAME = "test_user"
GROUP_SLUG = "test_slug"
URL_INDEX = reverse("posts:index")
URL_GROUP = reverse("posts:group_list", args=[GROUP_SLUG])
URL_AUTHOR_PROFILE = reverse("posts:profile", args=[AUTHOR_USERNAME])
URL_CREATE_POST = reverse("posts:post_create")
