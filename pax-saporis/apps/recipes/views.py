from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.ingredients.models import Ingredient
from apps.recipes.models import Recipe, RecipeIngredient
from apps.recipes.serializers import (
    RecipeDetailSerializer,
    RecipeIngredientSerializer,
    RecipeSerializer,
)


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Recipe.objects.filter(Q(user=self.request.user) | Q(is_default=True))

    def get_serializer_class(self):
        if self.action == "retrieve":
            return RecipeDetailSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, is_default=False)

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        instance.delete()

    @action(detail=False, methods=["get"])
    def defaults(self, request):
        recipes = Recipe.objects.filter(is_default=True)
        serializer = self.get_serializer(recipes, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def mine(self, request):
        recipes = Recipe.objects.filter(user=request.user)
        serializer = self.get_serializer(recipes, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def add_ingredient(self, request, pk=None):
        recipe = self.get_object()
        ingredient_id = request.data.get("ingredient_id")
        quantity = request.data.get("quantity")

        if not ingredient_id or not quantity:
            return Response(
                {"error": "ingredient_id y quantity son requeridos"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ingredient = Ingredient.objects.filter(id=ingredient_id).first()

        if ingredient is None:
            return Response(
                {"error": "Ingrediente no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )

        recipe_ingredient, created = RecipeIngredient.objects.get_or_create(
            recipe=recipe,
            ingredient=ingredient,
            defaults={"quantity": quantity},
        )

        if not created:
            recipe_ingredient.quantity = quantity
            recipe_ingredient.save()

        return Response(RecipeIngredientSerializer(recipe_ingredient).data)

    @action(detail=True, methods=["delete"], permission_classes=[IsAuthenticated])
    def remove_ingredient(self, request, pk=None):
        recipe = self.get_object()
        recipe_ingredient_id = request.data.get("recipe_ingredient_id")

        recipe_ingredient = RecipeIngredient.objects.filter(
            id=recipe_ingredient_id,
            recipe=recipe,
        ).first()

        if recipe_ingredient is None:
            return Response(
                {"error": "Ingrediente en receta no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )

        recipe_ingredient.delete()

        return Response(
            {"message": "Ingrediente removido"},
            status=status.HTTP_204_NO_CONTENT,
        )
