from django.shortcuts import render
from .serializers import RegisterSerializer, ChangePasswordSerializer, UpdateUserSerializer, UserInfoSerializer, \
    UserAdminSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated, BasePermission
from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from auth.permissions import IsSuperuser


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


class ChangePasswordView(generics.UpdateAPIView):
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangePasswordSerializer


class UpdateProfileView(generics.UpdateAPIView):
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = UpdateUserSerializer


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class UserInfoView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = UserInfoSerializer(request.user)
        return Response(user.data)


class AdminView(generics.ListAPIView, generics.UpdateAPIView):
    permission_classes = (IsSuperuser,)
    serializer_class = UserAdminSerializer
    queryset = User.objects.all()


class ChangeStaffStatusView(generics.UpdateAPIView):
    permission_classes = (IsSuperuser,)
    serializer_class = UserAdminSerializer
    queryset = User.objects.all()

    def patch(self, request, *args, **kwargs):
        user = self.get_object()
        user.is_staff = not user.is_staff
        user.save()
        return Response(UserAdminSerializer(user).data)
