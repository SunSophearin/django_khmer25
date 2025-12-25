from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.authentication import JWTAuthentication  # ✅ ADD

from .models import Profile
from .serializers import ProfileSerializer


class MyProfileView(APIView):
    authentication_classes = [JWTAuthentication]   # ✅ ADD
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        serializer = ProfileSerializer(profile, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class UploadProfileImage(APIView):
    authentication_classes = [JWTAuthentication]   # ✅ ADD
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def patch(self, request):
        profile, _ = Profile.objects.get_or_create(user=request.user)

        serializer = ProfileSerializer(
            profile,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class MyUserMeView(APIView):
    authentication_classes = [JWTAuthentication]   # ✅ ADD
    permission_classes = [IsAuthenticated]

    def get(self, request):
        u = request.user
        return Response(
            {"id": u.id, "email": u.email, "username": u.username},
            status=status.HTTP_200_OK
        )

    def patch(self, request):
        u = request.user

        username = request.data.get("username")
        if not username:
            return Response(
                {"username": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST
            )

        username = str(username).strip()
        if len(username) < 3:
            return Response(
                {"username": ["Username must be at least 3 characters."]},
                status=status.HTTP_400_BAD_REQUEST
            )

        u.username = username
        u.save(update_fields=["username"])

        return Response(
            {"id": u.id, "email": u.email, "username": u.username},
            status=status.HTTP_200_OK
        )
