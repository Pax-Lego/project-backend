from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q
from apps.plans.models import DailyPlan, PlanMeal
from apps.plans.serializers import (
    DailyPlanSerializer, DailyPlanDetailSerializer, PlanMealSerializer
)
from apps.recipes.models import Recipe


class DailyPlanViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return DailyPlan.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DailyPlanDetailSerializer
        return DailyPlanSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def add_meal(self, request, pk=None):
        plan = self.get_object()
        meal_type = request.data.get('meal_type')
        name = request.data.get('name')
        recipe_id = request.data.get('recipe_id')

        # Validar meal_type
        valid_types = [choice[0] for choice in PlanMeal.MealType.choices]
        if not meal_type or meal_type not in valid_types:
            return Response(
                {'error': f"meal_type debe ser uno de: {', '.join(valid_types)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validar name para snack y supplement
        if meal_type in ['snack', 'supplement'] and not name:
            return Response(
                {'error': 'El campo name es requerido para snack y supplement'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Buscar receta
        recipe = None
        if recipe_id:
            try:
                recipe = Recipe.objects.get(
                    Q(user=request.user) | Q(is_default=True), id=recipe_id
                )
            except Recipe.DoesNotExist:
                return Response(
                    {'error': 'Receta no encontrada'},
                    status=status.HTTP_404_NOT_FOUND
                )

        # Crear o actualizar
        if meal_type in PlanMeal.UNIQUE_MEAL_TYPES:
            plan_meal, created = PlanMeal.objects.get_or_create(
                daily_plan=plan,
                meal_type=meal_type,
                defaults={'recipe': recipe}
            )
            if not created:
                plan_meal.recipe = recipe
                plan_meal.save()
        else:
            plan_meal, created = PlanMeal.objects.get_or_create(
                daily_plan=plan,
                meal_type=meal_type,
                name=name,
                defaults={'recipe': recipe}
            )
            if not created:
                plan_meal.recipe = recipe
                plan_meal.save()

        return Response(PlanMealSerializer(plan_meal).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['delete'])
    def remove_meal(self, request, pk=None):
        plan = self.get_object()
        meal_type = request.data.get('meal_type')
        name = request.data.get('name')

        if not meal_type:
            return Response(
                {'error': 'meal_type es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            if meal_type in PlanMeal.UNIQUE_MEAL_TYPES:
                plan_meal = PlanMeal.objects.get(daily_plan=plan, meal_type=meal_type)
            else:
                if not name:
                    return Response(
                        {'error': 'name es requerido para eliminar snack o supplement'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                plan_meal = PlanMeal.objects.get(daily_plan=plan, meal_type=meal_type, name=name)

            plan_meal.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except PlanMeal.DoesNotExist:
            return Response(
                {'error': 'Comida no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['get'])
    def nutritional_summary(self, request, pk=None):
        plan = self.get_object()
        return Response({
            'total_calories': plan.total_calories,
            'total_protein': plan.total_protein,
            'total_carbs': plan.total_carbs,
            'total_fat': plan.total_fat,
        })