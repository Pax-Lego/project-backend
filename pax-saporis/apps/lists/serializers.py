from rest_framework import serializers

from apps.ingredients.serializers import IngredientSerializer
from apps.lists.models import IngredientList, RecipeList
from apps.recipes.serializers import RecipeSerializer


class IngredientListSerializer(serializers.ModelSerializer):
    ingredient_count = serializers.IntegerField(
        source="ingredients.count", read_only=True
    )
    ingredient_ids = serializers.PrimaryKeyRelatedField(
        source="ingredients", many=True, read_only=True
    )

    class Meta:
        model = IngredientList
        fields = [
            "id",
            "name",
            "is_builtin",
            "ingredient_count",
            "ingredient_ids",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "is_builtin",
            "ingredient_count",
            "ingredient_ids",
            "created_at",
            "updated_at",
        ]

    def validate_name(self, value):
        request = self.context.get("request")
        user = request.user if request else None
        qs = IngredientList.objects.filter(user=user, name=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Ya tienes una lista con este nombre.")
        return value


class IngredientListDetailSerializer(IngredientListSerializer):
    ingredients = IngredientSerializer(many=True, read_only=True)

    class Meta(IngredientListSerializer.Meta):
        fields = IngredientListSerializer.Meta.fields + ["ingredients"]


class RecipeListSerializer(serializers.ModelSerializer):
    recipe_count = serializers.IntegerField(source="recipes.count", read_only=True)
    recipe_ids = serializers.PrimaryKeyRelatedField(
        source="recipes", many=True, read_only=True
    )

    class Meta:
        model = RecipeList
        fields = [
            "id",
            "name",
            "is_builtin",
            "recipe_count",
            "recipe_ids",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "is_builtin",
            "recipe_count",
            "recipe_ids",
            "created_at",
            "updated_at",
        ]

    def validate_name(self, value):
        request = self.context.get("request")
        user = request.user if request else None
        qs = RecipeList.objects.filter(user=user, name=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Ya tienes una lista con este nombre.")
        return value


class RecipeListDetailSerializer(RecipeListSerializer):
    recipes = RecipeSerializer(many=True, read_only=True)

    class Meta(RecipeListSerializer.Meta):
        fields = RecipeListSerializer.Meta.fields + ["recipes"]
