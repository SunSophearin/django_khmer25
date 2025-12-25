from rest_framework import serializers
from .models import Profile
from djoser.serializers import UserSerializer

class ProfileSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ["image", "image_url"]

    def get_image_url(self, obj):
        """
        Return FULL absolute image URL
        """
        request = self.context.get("request")

        if not obj.image:
            return None

        # If request exists → build absolute URL
        if request is not None:
            return request.build_absolute_uri(obj.image.url)

        # Fallback (should not usually happen)
        return obj.image.url


class CustomUserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ("username",)
        read_only_fields = ("id", "email")
