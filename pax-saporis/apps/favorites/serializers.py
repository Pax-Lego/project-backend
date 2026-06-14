from rest_framework import serializers
from apps.favorites.models import FavoriteIngredient, FavoriteRecipe, FavoritePlan
from apps.ingredients.serializers import IngredientSerializer
from apps.recipes.serializers import RecipeSerializer
from apps.plans.serializers import DailyPlanSerializer


class FavoriteIngredientSerializer(serializers.ModelSerializer):
    ingredient_data = IngredientSerializer(source='ingredient', read_only=True)

    class Meta:
        model = FavoriteIngredient
        fields = ['id', 'ingredient', 'ingredient_data', 'created_at']
        read_only_fields = ['id', 'created_at']


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    recipe_data = RecipeSerializer(source='recipe', read_only=True)

    class Meta:
        model = FavoriteRecipe
        fields = ['id', 'recipe', 'recipe_data', 'created_at']
        read_only_fields = ['id', 'created_at']


class FavoritePlanSerializer(serializers.ModelSerializer):
    plan_data = DailyPlanSerializer(source='plan', read_only=True)

    class Meta:
        model = FavoritePlan
        fields = ['id', 'plan', 'plan_data', 'created_at']
        read_only_fields = ['id', 'created_at']