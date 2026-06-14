from rest_framework import serializers
from apps.plans.models import DailyPlan, PlanMeal
from apps.recipes.serializers import RecipeDetailSerializer


class PlanMealSerializer(serializers.ModelSerializer):
    recipe_data = RecipeDetailSerializer(source='recipe', read_only=True)
    calories = serializers.FloatField(read_only=True)
    protein = serializers.FloatField(read_only=True)
    carbs = serializers.FloatField(read_only=True)
    fat = serializers.FloatField(read_only=True)

    class Meta:
        model = PlanMeal
        fields = [
            'id', 'meal_type', 'name', 'recipe', 'recipe_data',
            'calories', 'protein', 'carbs', 'fat', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'calories', 'protein', 'carbs', 'fat']

    def validate(self, data):
        meal_type = data.get('meal_type')
        name = data.get('name')
        if meal_type in ['snack', 'supplement'] and not name:
            raise serializers.ValidationError(
                {'name': 'El campo name es requerido para snack y supplement'}
            )
        return data


class DailyPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyPlan
        fields = ['id', 'name', 'date', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class DailyPlanDetailSerializer(serializers.ModelSerializer):
    plan_meals = PlanMealSerializer(many=True, read_only=True)
    total_calories = serializers.FloatField(read_only=True)
    total_protein = serializers.FloatField(read_only=True)
    total_carbs = serializers.FloatField(read_only=True)
    total_fat = serializers.FloatField(read_only=True)

    class Meta:
        model = DailyPlan
        fields = [
            'id', 'name', 'date', 'description', 'plan_meals',
            'total_calories', 'total_protein', 'total_carbs', 'total_fat',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at',
            'total_calories', 'total_protein', 'total_carbs', 'total_fat'
        ]