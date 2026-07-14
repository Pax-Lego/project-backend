import unittest
from datetime import date, timedelta
from unittest.mock import MagicMock, PropertyMock, patch

from django.test import TestCase
from rest_framework.test import APIClient

from apps.accounts.models import CustomUser
from apps.ingredients.models import Ingredient
from apps.plans.models import DailyPlan, PlanMeal
from apps.recipes.models import Recipe, RecipeIngredient


def make_mock_recipe(calories, protein, carbs, fat):
    recipe = MagicMock()
    type(recipe).total_calories = PropertyMock(return_value=calories)
    type(recipe).total_protein = PropertyMock(return_value=protein)
    type(recipe).total_carbs = PropertyMock(return_value=carbs)
    type(recipe).total_fat = PropertyMock(return_value=fat)
    return recipe


def make_mock_plan_meal(recipe=None, calories=0, protein=0, carbs=0, fat=0):
    meal = MagicMock()
    type(meal).calories = PropertyMock(return_value=calories)
    type(meal).protein = PropertyMock(return_value=protein)
    type(meal).carbs = PropertyMock(return_value=carbs)
    type(meal).fat = PropertyMock(return_value=fat)
    return meal


class TestPlanMealCalories(unittest.TestCase):
    def test_plan_meal_calories_with_recipe(self):
        from apps.plans.models import PlanMeal

        recipe = make_mock_recipe(calories=350.0, protein=30.0, carbs=40.0, fat=8.0)

        meal = PlanMeal.__new__(PlanMeal)
        meal.recipe = recipe

        self.assertAlmostEqual(meal.calories, 350.0)
        self.assertAlmostEqual(meal.protein, 30.0)
        self.assertAlmostEqual(meal.carbs, 40.0)
        self.assertAlmostEqual(meal.fat, 8.0)

    def test_plan_meal_calories_with_decimal_values(self):
        from apps.plans.models import PlanMeal

        recipe = make_mock_recipe(
            calories=123.456, protein=15.789, carbs=22.111, fat=4.333
        )

        meal = PlanMeal.__new__(PlanMeal)
        meal.recipe = recipe

        self.assertAlmostEqual(meal.calories, 123.46, places=1)
        self.assertAlmostEqual(meal.protein, 15.79, places=1)


class TestPlanMealWithoutRecipe(unittest.TestCase):
    def test_plan_meal_calories_without_recipe(self):
        from apps.plans.models import PlanMeal

        meal = PlanMeal.__new__(PlanMeal)
        meal.recipe = None

        self.assertEqual(meal.calories, 0)

    def test_plan_meal_all_macros_without_recipe(self):
        from apps.plans.models import PlanMeal

        meal = PlanMeal.__new__(PlanMeal)
        meal.recipe = None

        self.assertEqual(meal.calories, 0)
        self.assertEqual(meal.protein, 0)
        self.assertEqual(meal.carbs, 0)
        self.assertEqual(meal.fat, 0)


class TestDailyPlanTotals(unittest.TestCase):
    def test_daily_plan_total_calories_multiple_meals(self):
        from apps.plans.models import DailyPlan

        meals = [
            make_mock_plan_meal(calories=350.0, protein=30.0, carbs=40.0, fat=8.0),
            make_mock_plan_meal(calories=600.0, protein=45.0, carbs=70.0, fat=15.0),
            make_mock_plan_meal(calories=200.0, protein=10.0, carbs=30.0, fat=5.0),
        ]

        plan = DailyPlan.__new__(DailyPlan)

        with patch.object(
            type(plan), "plan_meals", new_callable=PropertyMock
        ) as mock_meals:
            mock_meals.return_value.all.return_value = meals

            self.assertAlmostEqual(plan.total_calories, 1150.0)
            self.assertAlmostEqual(plan.total_protein, 85.0)
            self.assertAlmostEqual(plan.total_carbs, 140.0)
            self.assertAlmostEqual(plan.total_fat, 28.0)

    def test_daily_plan_total_empty_plan(self):
        from apps.plans.models import DailyPlan

        plan = DailyPlan.__new__(DailyPlan)

        with patch.object(
            type(plan), "plan_meals", new_callable=PropertyMock
        ) as mock_meals:
            mock_meals.return_value.all.return_value = []

            self.assertEqual(plan.total_calories, 0)
            self.assertEqual(plan.total_protein, 0)
            self.assertEqual(plan.total_carbs, 0)
            self.assertEqual(plan.total_fat, 0)


class TestDailyPlanMixedMeals(unittest.TestCase):
    def test_daily_plan_totals_with_empty_meals(self):
        from apps.plans.models import DailyPlan

        meals = [
            make_mock_plan_meal(calories=500.0, protein=40.0, carbs=50.0, fat=12.0),
            make_mock_plan_meal(calories=0, protein=0, carbs=0, fat=0),
            make_mock_plan_meal(calories=300.0, protein=25.0, carbs=35.0, fat=7.0),
        ]

        plan = DailyPlan.__new__(DailyPlan)

        with patch.object(
            type(plan), "plan_meals", new_callable=PropertyMock
        ) as mock_meals:
            mock_meals.return_value.all.return_value = meals

            self.assertAlmostEqual(plan.total_calories, 800.0)
            self.assertAlmostEqual(plan.total_protein, 65.0)
            self.assertAlmostEqual(plan.total_carbs, 85.0)
            self.assertAlmostEqual(plan.total_fat, 19.0)

    def test_daily_plan_single_meal(self):
        from apps.plans.models import DailyPlan

        meals = [
            make_mock_plan_meal(calories=450.0, protein=35.0, carbs=55.0, fat=10.0),
        ]

        plan = DailyPlan.__new__(DailyPlan)

        with patch.object(
            type(plan), "plan_meals", new_callable=PropertyMock
        ) as mock_meals:
            mock_meals.return_value.all.return_value = meals

            self.assertAlmostEqual(plan.total_calories, 450.0)
            self.assertAlmostEqual(plan.total_protein, 35.0)


class DailyPlanHistoryAndDateFilterTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="historyuser", email="history@example.com", password="testpass123"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.ingredient = Ingredient.objects.create(
            user=self.user,
            name="Chicken breast",
            calories_per_100g=165,
            protein_g=31,
            carbs_g=0,
            fat_g=3.6,
        )
        self.recipe = Recipe.objects.create(user=self.user, name="Grilled chicken")
        RecipeIngredient.objects.create(
            recipe=self.recipe, ingredient=self.ingredient, quantity=200
        )

        self.today = date.today()
        self.yesterday = self.today - timedelta(days=1)
        self.old_date = self.today - timedelta(days=40)

        self.plan_today = DailyPlan.objects.create(
            user=self.user, name="Today", date=self.today
        )
        PlanMeal.objects.create(
            daily_plan=self.plan_today, meal_type="lunch", recipe=self.recipe
        )

        self.plan_yesterday = DailyPlan.objects.create(
            user=self.user, name="Yesterday", date=self.yesterday
        )
        PlanMeal.objects.create(
            daily_plan=self.plan_yesterday, meal_type="dinner", recipe=self.recipe
        )

        self.plan_old = DailyPlan.objects.create(
            user=self.user, name="Old", date=self.old_date
        )
        PlanMeal.objects.create(
            daily_plan=self.plan_old, meal_type="breakfast", recipe=self.recipe
        )

    def test_date_filter_returns_only_matching_plan(self):
        response = self.client.get("/api/plans/", {"date": self.today.isoformat()})
        self.assertEqual(response.status_code, 200)
        dates = [item["date"] for item in response.json()]
        self.assertEqual(dates, [self.today.isoformat()])

    def test_date_filter_no_match_returns_empty(self):
        far_future = (self.today + timedelta(days=365)).isoformat()
        response = self.client.get("/api/plans/", {"date": far_future})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_history_default_30_days_excludes_old_plan(self):
        response = self.client.get("/api/plans/history/")
        self.assertEqual(response.status_code, 200)
        dates = [item["date"] for item in response.json()]
        self.assertIn(self.today.isoformat(), dates)
        self.assertIn(self.yesterday.isoformat(), dates)
        self.assertNotIn(self.old_date.isoformat(), dates)

    def test_history_totals_match_recipe_nutrition(self):
        response = self.client.get("/api/plans/history/")
        data = response.json()
        today_entry = next(
            item for item in data if item["date"] == self.today.isoformat()
        )
        # 200g of chicken breast (165 kcal / 31g protein / 3.6g fat per 100g)
        self.assertAlmostEqual(today_entry["total_calories"], 330.0)
        self.assertAlmostEqual(today_entry["total_protein"], 62.0)
        self.assertAlmostEqual(today_entry["total_fat"], 7.2)

    def test_history_respects_days_param(self):
        response = self.client.get("/api/plans/history/", {"days": 45})
        dates = [item["date"] for item in response.json()]
        self.assertIn(self.old_date.isoformat(), dates)

    def test_history_only_returns_own_plans(self):
        other_user = CustomUser.objects.create_user(
            username="otheruser", email="other@example.com", password="testpass123"
        )
        DailyPlan.objects.create(user=other_user, name="Other", date=self.today)

        response = self.client.get("/api/plans/history/")
        data = response.json()
        self.assertEqual(len(data), 2)
