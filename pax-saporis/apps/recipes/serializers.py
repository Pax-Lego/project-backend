from rest_framework import serializers

from apps.recipes.models import Recipe, RecipeIngredient


class RecipeIngredientSerializer(serializers.ModelSerializer):
    ingredient_name = serializers.CharField(source="ingredient.name", read_only=True)
    ingredient_id = serializers.IntegerField(source="ingredient.id", read_only=True)
    calories = serializers.FloatField(read_only=True)
    protein = serializers.FloatField(read_only=True)
    carbs = serializers.FloatField(read_only=True)
    fat = serializers.FloatField(read_only=True)

    class Meta:
        model = RecipeIngredient
        fields = [
            "id",
            "ingredient_id",
            "ingredient_name",
            "quantity_g",
            "calories",
            "protein",
            "carbs",
            "fat",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "calories", "protein", "carbs", "fat"]


class RecipeSerializer(serializers.ModelSerializer):
    ingredients_rel = RecipeIngredientSerializer(many=True, read_only=True)
    total_calories = serializers.FloatField(read_only=True)
    total_protein = serializers.FloatField(read_only=True)
    total_carbs = serializers.FloatField(read_only=True)
    total_fat = serializers.FloatField(read_only=True)

    class Meta:
        model = Recipe
        fields = [
            "id",
            "name",
            "description",
            "is_default",
            "ingredients_rel",
            "total_calories",
            "total_protein",
            "total_carbs",
            "total_fat",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "is_default",
            "total_calories",
            "total_protein",
            "total_carbs",
            "total_fat",
        ]


class RecipeDetailSerializer(serializers.ModelSerializer):
    ingredients_rel = RecipeIngredientSerializer(many=True, read_only=True)
    total_calories = serializers.FloatField(read_only=True)
    total_protein = serializers.FloatField(read_only=True)
    total_carbs = serializers.FloatField(read_only=True)
    total_fat = serializers.FloatField(read_only=True)

    class Meta:
        model = Recipe
        fields = [
            "id",
            "name",
            "description",
            "is_default",
            "ingredients_rel",
            "total_calories",
            "total_protein",
            "total_carbs",
            "total_fat",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "is_default",
            "total_calories",
            "total_protein",
            "total_carbs",
            "total_fat",
        ]
