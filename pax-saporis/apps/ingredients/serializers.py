from rest_framework import serializers

from apps.ingredients.models import Ingredient


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = [
            "id",
            "name",
            "is_default",
            "calories_per_100g",
            "protein_g",
            "carbs_g",
            "fat_g",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "is_default"]
