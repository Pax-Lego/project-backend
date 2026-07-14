from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.ingredients.models import Ingredient
from apps.lists.models import IngredientList, RecipeList
from apps.lists.serializers import (
    IngredientListDetailSerializer,
    IngredientListSerializer,
    RecipeListDetailSerializer,
    RecipeListSerializer,
)
from apps.recipes.models import Recipe


class IngredientListViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return IngredientList.objects.filter(
            Q(user=self.request.user) | Q(is_builtin=True)
        )

    def get_serializer_class(self):
        if self.action == "retrieve":
            return IngredientListDetailSerializer
        return IngredientListSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, is_builtin=False)

    def perform_update(self, serializer):
        if self.get_object().is_builtin:
            raise PermissionDenied("No puedes editar la lista predeterminada")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.is_builtin:
            raise PermissionDenied("No puedes eliminar la lista predeterminada")
        instance.delete()

    @action(detail=True, methods=["post"])
    def add_ingredient(self, request, pk=None):
        list_obj = self.get_object()
        if list_obj.is_builtin:
            return Response(
                {"error": "La lista predeterminada se gestiona automáticamente"},
                status=status.HTTP_403_FORBIDDEN,
            )
        ingredient = Ingredient.objects.filter(
            Q(user=request.user) | Q(is_default=True),
            id=request.data.get("ingredient_id"),
        ).first()
        if ingredient is None:
            return Response(
                {"error": "Ingrediente no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )
        list_obj.ingredients.add(ingredient)
        return Response(IngredientListDetailSerializer(list_obj).data)

    @action(detail=True, methods=["delete"])
    def remove_ingredient(self, request, pk=None):
        list_obj = self.get_object()
        if list_obj.is_builtin:
            return Response(
                {"error": "La lista predeterminada se gestiona automáticamente"},
                status=status.HTTP_403_FORBIDDEN,
            )
        list_obj.ingredients.remove(request.data.get("ingredient_id"))
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeListViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return RecipeList.objects.filter(Q(user=self.request.user) | Q(is_builtin=True))

    def get_serializer_class(self):
        if self.action == "retrieve":
            return RecipeListDetailSerializer
        return RecipeListSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, is_builtin=False)

    def perform_update(self, serializer):
        if self.get_object().is_builtin:
            raise PermissionDenied("No puedes editar la lista predeterminada")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.is_builtin:
            raise PermissionDenied("No puedes eliminar la lista predeterminada")
        instance.delete()

    @action(detail=True, methods=["post"])
    def add_recipe(self, request, pk=None):
        list_obj = self.get_object()
        if list_obj.is_builtin:
            return Response(
                {"error": "La lista predeterminada se gestiona automáticamente"},
                status=status.HTTP_403_FORBIDDEN,
            )
        recipe = Recipe.objects.filter(
            Q(user=request.user) | Q(is_default=True),
            id=request.data.get("recipe_id"),
        ).first()
        if recipe is None:
            return Response(
                {"error": "Receta no encontrada"},
                status=status.HTTP_404_NOT_FOUND,
            )
        list_obj.recipes.add(recipe)
        return Response(RecipeListDetailSerializer(list_obj).data)

    @action(detail=True, methods=["delete"])
    def remove_recipe(self, request, pk=None):
        list_obj = self.get_object()
        if list_obj.is_builtin:
            return Response(
                {"error": "La lista predeterminada se gestiona automáticamente"},
                status=status.HTTP_403_FORBIDDEN,
            )
        list_obj.recipes.remove(request.data.get("recipe_id"))
        return Response(status=status.HTTP_204_NO_CONTENT)
