from django.urls import path, include
from rest_framework.routers import SimpleRouter
from apps.profiles import views

router = SimpleRouter()
router.register(r'weight', views.WeightEntryViewSet, basename='weight')
router.register(r'', views.ProfileView, basename='profile')

urlpatterns = [
    path('', include(router.urls)),
]