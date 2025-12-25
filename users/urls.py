from django.urls import path
from .views import UploadProfileImage, MyProfileView, MyUserMeView

urlpatterns = [
    path("me/", MyUserMeView.as_view(), name="my-user-me"),
    path("profile/", MyProfileView.as_view(), name="my-profile"),          # ✅ ADD
    path("profile/image/", UploadProfileImage.as_view(), name="profile-image"),
]
