import unittest
from unittest.mock import MagicMock, PropertyMock, patch


def make_mock_recipe(calories, protein, carbs, fat):
    """Helper: crea una receta mock con macros definidos."""
    recipe = MagicMock()
    type(recipe).total_calories = PropertyMock(return_value=calories)
    type(recipe).total_protein = PropertyMock(return_value=protein)
    type(recipe).total_carbs = PropertyMock(return_value=carbs)
    type(recipe).total_fat = PropertyMock(return_value=fat)
    return recipe


def make_mock_plan_meal(recipe=None, calories=0, protein=0, carbs=0, fat=0):
    """Helper: crea un PlanMeal mock con propiedades de macros."""
    meal = MagicMock()
    type(meal).calories = PropertyMock(return_value=calories)
    type(meal).protein = PropertyMock(return_value=protein)
    type(meal).carbs = PropertyMock(return_value=carbs)
    type(meal).fat = PropertyMock(return_value=fat)
    return meal


class TestPlanMealCalories(unittest.TestCase):
    """
    Prueba 1: Un PlanMeal con receta asignada calcula correctamente
    sus macros basándose en la receta.
    """

    def test_plan_meal_calories_with_recipe(self):
        """PlanMeal con receta retorna los macros de la receta."""
        from apps.plans.models import PlanMeal

        recipe = make_mock_recipe(
            calories=350.0,
            protein=30.0,
            carbs=40.0,
            fat=8.0
        )

        meal = PlanMeal.__new__(PlanMeal)
        meal.recipe = recipe

        self.assertAlmostEqual(meal.calories, 350.0)
        self.assertAlmostEqual(meal.protein, 30.0)
        self.assertAlmostEqual(meal.carbs, 40.0)
        self.assertAlmostEqual(meal.fat, 8.0)

    def test_plan_meal_calories_with_decimal_values(self):
        """PlanMeal maneja correctamente valores decimales en macros."""
        from apps.plans.models import PlanMeal

        recipe = make_mock_recipe(
            calories=123.456,
            protein=15.789,
            carbs=22.111,
            fat=4.333
        )

        meal = PlanMeal.__new__(PlanMeal)
        meal.recipe = recipe

        self.assertAlmostEqual(meal.calories, 123.46, places=1)
        self.assertAlmostEqual(meal.protein, 15.79, places=1)


class TestPlanMealWithoutRecipe(unittest.TestCase):
    """
    Prueba 2: Un PlanMeal sin receta asignada retorna 0
    en todos sus macros — caso límite esencial.
    """

    def test_plan_meal_calories_without_recipe(self):
        """PlanMeal sin receta retorna 0 en calorías."""
        from apps.plans.models import PlanMeal

        meal = PlanMeal.__new__(PlanMeal)
        meal.recipe = None

        self.assertEqual(meal.calories, 0)

    def test_plan_meal_all_macros_without_recipe(self):
        """PlanMeal sin receta retorna 0 en todos los macros."""
        from apps.plans.models import PlanMeal

        meal = PlanMeal.__new__(PlanMeal)
        meal.recipe = None

        self.assertEqual(meal.calories, 0)
        self.assertEqual(meal.protein, 0)
        self.assertEqual(meal.carbs, 0)
        self.assertEqual(meal.fat, 0)


class TestDailyPlanTotals(unittest.TestCase):
    """
    Prueba 3: DailyPlan suma correctamente los macros
    de todos sus PlanMeals.
    """

    def test_daily_plan_total_calories_multiple_meals(self):
        """DailyPlan suma calorías de múltiples comidas correctamente."""
        from apps.plans.models import DailyPlan

        meals = [
            make_mock_plan_meal(calories=350.0, protein=30.0, carbs=40.0, fat=8.0),
            make_mock_plan_meal(calories=600.0, protein=45.0, carbs=70.0, fat=15.0),
            make_mock_plan_meal(calories=200.0, protein=10.0, carbs=30.0, fat=5.0),
        ]

        plan = DailyPlan.__new__(DailyPlan)

        with patch.object(type(plan), 'plan_meals', new_callable=PropertyMock) as mock_meals:
            mock_meals.return_value.all.return_value = meals

            self.assertAlmostEqual(plan.total_calories, 1150.0)
            self.assertAlmostEqual(plan.total_protein, 85.0)
            self.assertAlmostEqual(plan.total_carbs, 140.0)
            self.assertAlmostEqual(plan.total_fat, 28.0)

    def test_daily_plan_total_empty_plan(self):
        """DailyPlan sin comidas retorna 0 en todos los totales."""
        from apps.plans.models import DailyPlan

        plan = DailyPlan.__new__(DailyPlan)

        with patch.object(type(plan), 'plan_meals', new_callable=PropertyMock) as mock_meals:
            mock_meals.return_value.all.return_value = []

            self.assertEqual(plan.total_calories, 0)
            self.assertEqual(plan.total_protein, 0)
            self.assertEqual(plan.total_carbs, 0)
            self.assertEqual(plan.total_fat, 0)


class TestDailyPlanMixedMeals(unittest.TestCase):
    """
    Prueba 4: DailyPlan con mezcla de comidas con y sin receta
    — caso límite real en uso cotidiano.
    """

    def test_daily_plan_totals_with_empty_meals(self):
        """DailyPlan suma correctamente cuando algunos meals no tienen receta."""
        from apps.plans.models import DailyPlan

        meals = [
            make_mock_plan_meal(calories=500.0, protein=40.0, carbs=50.0, fat=12.0),
            make_mock_plan_meal(calories=0, protein=0, carbs=0, fat=0),  # sin receta
            make_mock_plan_meal(calories=300.0, protein=25.0, carbs=35.0, fat=7.0),
        ]

        plan = DailyPlan.__new__(DailyPlan)

        with patch.object(type(plan), 'plan_meals', new_callable=PropertyMock) as mock_meals:
            mock_meals.return_value.all.return_value = meals

            self.assertAlmostEqual(plan.total_calories, 800.0)
            self.assertAlmostEqual(plan.total_protein, 65.0)
            self.assertAlmostEqual(plan.total_carbs, 85.0)
            self.assertAlmostEqual(plan.total_fat, 19.0)

    def test_daily_plan_single_meal(self):
        """DailyPlan con una sola comida retorna exactamente sus macros."""
        from apps.plans.models import DailyPlan

        meals = [
            make_mock_plan_meal(calories=450.0, protein=35.0, carbs=55.0, fat=10.0),
        ]

        plan = DailyPlan.__new__(DailyPlan)

        with patch.object(type(plan), 'plan_meals', new_callable=PropertyMock) as mock_meals:
            mock_meals.return_value.all.return_value = meals

            self.assertAlmostEqual(plan.total_calories, 450.0)
            self.assertAlmostEqual(plan.total_protein, 35.0)