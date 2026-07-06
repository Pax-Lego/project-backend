from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.plans.models import DailyPlan, PlanMeal
from apps.plans.serializers import (
    DailyPlanDetailSerializer,
    DailyPlanSerializer,
    PlanMealSerializer,
)
from apps.recipes.models import Recipe


class DailyPlanViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return DailyPlan.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return DailyPlanDetailSerializer
        return DailyPlanSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["get"])
    def nutritional_summary(self, request, pk=None):
        plan = self.get_object()
        return Response(
            {
                "total_calories": plan.total_calories,
                "total_protein": plan.total_protein,
                "total_carbs": plan.total_carbs,
                "total_fat": plan.total_fat,
            }
        )

    @action(detail=True, methods=["post"])
    def add_meal(self, request, pk=None):
        plan = self.get_object()
        meal_type = request.data.get("meal_type")
        name = request.data.get("name")
        recipe_id = request.data.get("recipe_id")

        valid_types = [choice[0] for choice in PlanMeal.MealType.choices]
        if not meal_type or meal_type not in valid_types:
            return Response(
                {"error": f"meal_type debe ser uno de: {', '.join(valid_types)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if meal_type in ["snack", "supplement"] and not name:
            return Response(
                {"error": "El campo name es requerido para snack y suplemento"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        recipe = None
        if recipe_id:
            recipe = Recipe.objects.filter(
                Q(user=request.user) | Q(is_default=True),
                id=recipe_id,
            ).first()

            if recipe is None:
                return Response(
                    {"error": "Receta no encontrada"},
                    status=status.HTTP_404_NOT_FOUND,
                )

        if meal_type in PlanMeal.UNIQUE_MEAL_TYPES:
            plan_meal, created = PlanMeal.objects.get_or_create(
                daily_plan=plan, meal_type=meal_type, defaults={"recipe": recipe}
            )
            if not created:
                plan_meal.recipe = recipe
                plan_meal.save()
        else:
            plan_meal, created = PlanMeal.objects.get_or_create(
                daily_plan=plan,
                meal_type=meal_type,
                name=name,
                defaults={"recipe": recipe},
            )
            if not created:
                plan_meal.recipe = recipe
                plan_meal.save()

        return Response(PlanMealSerializer(plan_meal).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["delete"])
    def remove_meal(self, request, pk=None):
        plan = self.get_object()
        meal_type = request.data.get("meal_type")
        name = request.data.get("name")

        if not meal_type:
            return Response(
                {"error": "meal_type es requerido"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if meal_type in PlanMeal.UNIQUE_MEAL_TYPES:
            plan_meal = PlanMeal.objects.filter(
                daily_plan=plan,
                meal_type=meal_type,
            ).first()
        else:
            if not name:
                return Response(
                    {"error": "name es requerido para eliminar snack o suplemento"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            plan_meal = PlanMeal.objects.filter(
                daily_plan=plan,
                meal_type=meal_type,
                name=name,
            ).first()

        if plan_meal is None:
            return Response(
                {"error": "Comida no encontrada"},
                status=status.HTTP_404_NOT_FOUND,
            )

        plan_meal.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
