
from django.urls import path
from .views import SignUpView

from accounts import views

urlpatterns = [
    path('accounts/', SignUpView.as_view(), name = 'signup'),
    path('update/', views.profile_update, name='update')
    
]

