from django.urls import path
from auth.views import RegisterView, ChangePasswordView, UpdateProfileView, LogoutView, UserInfoView, AdminView, \
    ChangeStaffStatusView
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('change_password/<int:pk>/', ChangePasswordView.as_view(), name='auth_change_password'),
    path('update_profile/<int:pk>/', UpdateProfileView.as_view(), name='auth_update_profile'),
    path('logout/', LogoutView.as_view(), name='auth_logout'),
    path('current_user/', UserInfoView.as_view(), name='user_info'),
    path('users/', AdminView.as_view(), name="users"),
    path('users/<int:pk>/staff-status/', ChangeStaffStatusView.as_view(), name="change-staff-status")
]
