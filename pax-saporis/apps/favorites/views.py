from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.favorites.models import FavoriteIngredient, FavoritePlan, FavoriteRecipe
from apps.favorites.serializers import (
    FavoriteIngredientSerializer,
    FavoritePlanSerializer,
    FavoriteRecipeSerializer,
)


class FavoriteIngredientViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteIngredientSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "delete"]

    def get_queryset(self):
        return FavoriteIngredient.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        if FavoriteIngredient.objects.filter(
            user=request.user, ingredient_id=request.data.get("ingredient")
        ).exists():
            return Response(
                {"error": "Este ingrediente ya está en favoritos"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().create(request, *args, **kwargs)


class FavoriteRecipeViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteRecipeSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "delete"]

    def get_queryset(self):
        return FavoriteRecipe.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        if FavoriteRecipe.objects.filter(
            user=request.user, recipe_id=request.data.get("recipe")
        ).exists():
            return Response(
                {"error": "Esta receta ya está en favoritos"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().create(request, *args, **kwargs)


class FavoritePlanViewSet(viewsets.ModelViewSet):
    serializer_class = FavoritePlanSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "delete"]

    def get_queryset(self):
        return FavoritePlan.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        if FavoritePlan.objects.filter(
            user=request.user, plan_id=request.data.get("plan")
        ).exists():
            return Response(
                {"error": "Este plan ya está en favoritos"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().create(request, *args, **kwargs)
