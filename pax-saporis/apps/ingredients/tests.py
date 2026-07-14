from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.core.exceptions import ObjectDoesNotExist
from django.test import SimpleTestCase, TestCase
from rest_framework import status
from rest_framework.test import APIClient, APIRequestFactory, force_authenticate

from apps.accounts.models import CustomUser
from apps.ingredients.models import Ingredient
from apps.ingredients.views import IngredientViewSet
from apps.recipes.views import RecipeViewSet


class TestAddIngredientValidationView(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = RecipeViewSet.as_view({"post": "add_ingredient"})
        self.user = SimpleNamespace(id=1, is_authenticated=True, is_active=True)
        self.mock_recipe = MagicMock()
        self.mock_recipe.id = 1

    def test_missing_quantity_returns_400(self):
        payload = {"ingredient_id": 1}

        with patch.object(RecipeViewSet, "get_object", return_value=self.mock_recipe):
            request = self.factory.post(
                "/api/recipes/1/add_ingredient/", payload, format="json"
            )
            force_authenticate(request, user=self.user)
            response = self.view(request, pk=1)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_missing_ingredient_id_returns_400(self):
        payload = {"quantity": 100}

        with patch.object(RecipeViewSet, "get_object", return_value=self.mock_recipe):
            request = self.factory.post(
                "/api/recipes/1/add_ingredient/", payload, format="json"
            )
            force_authenticate(request, user=self.user)
            response = self.view(request, pk=1)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_missing_both_fields_returns_400(self):
        payload = {}

        with patch.object(RecipeViewSet, "get_object", return_value=self.mock_recipe):
            request = self.factory.post(
                "/api/recipes/1/add_ingredient/", payload, format="json"
            )
            force_authenticate(request, user=self.user)
            response = self.view(request, pk=1)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_ingredient_not_found_returns_404(self):
        payload = {"ingredient_id": 999, "quantity": 100}

        with patch.object(RecipeViewSet, "get_object", return_value=self.mock_recipe):
            with patch("apps.recipes.views.Ingredient") as mock_ingredient_model:
                mock_does_not_exist = type("DoesNotExist", (ObjectDoesNotExist,), {})
                mock_ingredient_model.DoesNotExist = mock_does_not_exist
                mock_ingredient_model.objects.get.side_effect = mock_does_not_exist(
                    "Not found"
                )

                request = self.factory.post(
                    "/api/recipes/1/add_ingredient/", payload, format="json"
                )
                force_authenticate(request, user=self.user)
                response = self.view(request, pk=1)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error", response.data)


class TestAddIngredientSuccessView(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = RecipeViewSet.as_view({"post": "add_ingredient"})
        self.user = SimpleNamespace(id=1, is_authenticated=True, is_active=True)
        self.mock_recipe = MagicMock()
        self.mock_recipe.id = 1

    def _make_mock_recipe_ingredient(self, created=True):
        mock_ri = MagicMock()
        mock_ri.id = 1
        mock_ri.quantity = 150.0
        return mock_ri, created

    def test_add_new_ingredient_returns_200(self):
        payload = {"ingredient_id": 1, "quantity": 150}
        mock_ingredient = MagicMock()
        mock_ri = MagicMock()
        mock_ri.id = 1

        with patch.object(RecipeViewSet, "get_object", return_value=self.mock_recipe):
            with patch("apps.recipes.views.Ingredient") as mock_ingredient_model:
                mock_ingredient_model.objects.get.return_value = mock_ingredient
                with patch("apps.recipes.views.RecipeIngredient") as mock_ri_model:
                    mock_ri_model.objects.get_or_create.return_value = (mock_ri, True)
                    with patch(
                        "apps.recipes.views.RecipeIngredientSerializer"
                    ) as mock_serializer_cls:
                        mock_serializer_cls.return_value.data = {
                            "id": 1,
                            "quantity": 150,
                        }

                        request = self.factory.post(
                            "/api/recipes/1/add_ingredient/", payload, format="json"
                        )
                        force_authenticate(request, user=self.user)
                        response = self.view(request, pk=1)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_add_existing_ingredient_updates_quantity(self):
        payload = {"ingredient_id": 1, "quantity": 200}
        mock_ingredient = MagicMock()
        mock_ri = MagicMock()
        mock_ri.quantity = 100.0

        with patch.object(RecipeViewSet, "get_object", return_value=self.mock_recipe):
            with patch("apps.recipes.views.Ingredient") as mock_ingredient_model:
                mock_ingredient_model.objects.get.return_value = mock_ingredient
                with patch("apps.recipes.views.RecipeIngredient") as mock_ri_model:
                    mock_ri_model.objects.get_or_create.return_value = (mock_ri, False)
                    with patch(
                        "apps.recipes.views.RecipeIngredientSerializer"
                    ) as mock_serializer_cls:
                        mock_serializer_cls.return_value.data = {
                            "id": 1,
                            "quantity": 200,
                        }

                        request = self.factory.post(
                            "/api/recipes/1/add_ingredient/", payload, format="json"
                        )
                        force_authenticate(request, user=self.user)
                        response = self.view(request, pk=1)

        self.assertEqual(mock_ri.quantity, 200)
        mock_ri.save.assert_called_once()

    def test_add_ingredient_calls_get_or_create_with_correct_args(self):
        payload = {"ingredient_id": 5, "quantity": 75}
        mock_ingredient = MagicMock()
        mock_ri = MagicMock()

        with patch.object(RecipeViewSet, "get_object", return_value=self.mock_recipe):
            with patch("apps.recipes.views.Ingredient") as mock_ingredient_model:
                mock_ingredient_model.objects.get.return_value = mock_ingredient
                with patch("apps.recipes.views.RecipeIngredient") as mock_ri_model:
                    mock_ri_model.objects.get_or_create.return_value = (mock_ri, True)
                    with patch(
                        "apps.recipes.views.RecipeIngredientSerializer"
                    ) as mock_serializer_cls:
                        mock_serializer_cls.return_value.data = {}

                        request = self.factory.post(
                            "/api/recipes/1/add_ingredient/", payload, format="json"
                        )
                        force_authenticate(request, user=self.user)
                        self.view(request, pk=1)

        mock_ri_model.objects.get_or_create.assert_called_once_with(
            recipe=self.mock_recipe,
            ingredient=mock_ingredient,
            defaults={"quantity": 75},
        )


class TestDefaultIngredientEditableView(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="editdefault", email="editdefault@example.com", password="testpass123"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.ingredient = Ingredient.objects.create(
            name="Default Tomato",
            is_default=True,
            calories_per_100g=18.0,
            protein_g=0.9,
            carbs_g=3.9,
            fat_g=0.2,
        )

    def test_update_default_ingredient_succeeds(self):
        response = self.client.patch(
            f"/api/ingredients/{self.ingredient.id}/",
            {"calories_per_100g": 20.0},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.ingredient.refresh_from_db()
        self.assertEqual(self.ingredient.calories_per_100g, 20.0)

    def test_delete_default_ingredient_succeeds(self):
        response = self.client.delete(f"/api/ingredients/{self.ingredient.id}/")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Ingredient.objects.filter(id=self.ingredient.id).exists())


class TestRecipeIngredientMacroCalculation(SimpleTestCase):
    def _make_recipe_ingredient(
        self, calories_per_100g, protein_g, carbs_g, fat_g, quantity
    ):
        from apps.recipes.models import RecipeIngredient

        ri = RecipeIngredient.__new__(RecipeIngredient)
        ri.ingredient = MagicMock()
        ri.ingredient.calories_per_100g = calories_per_100g
        ri.ingredient.protein_g = protein_g
        ri.ingredient.carbs_g = carbs_g
        ri.ingredient.fat_g = fat_g
        ri.quantity = quantity
        return ri

    def test_calories_calculated_correctly(self):
        ri = self._make_recipe_ingredient(
            calories_per_100g=18.0,
            protein_g=0.9,
            carbs_g=3.9,
            fat_g=0.2,
            quantity=200.0,
        )
        self.assertAlmostEqual(ri.calories, 36.0)

    def test_all_macros_calculated_correctly(self):
        ri = self._make_recipe_ingredient(
            calories_per_100g=165.0,
            protein_g=31.0,
            carbs_g=0.0,
            fat_g=3.6,
            quantity=150.0,
        )
        self.assertAlmostEqual(ri.protein, 46.5)
        self.assertAlmostEqual(ri.carbs, 0.0)
        self.assertAlmostEqual(ri.fat, 5.4)

    def test_zero_quantity_returns_zero_macros(self):
        ri = self._make_recipe_ingredient(
            calories_per_100g=100.0,
            protein_g=10.0,
            carbs_g=10.0,
            fat_g=5.0,
            quantity=0.0,
        )
        self.assertEqual(ri.calories, 0.0)
        self.assertEqual(ri.protein, 0.0)
        self.assertEqual(ri.carbs, 0.0)
        self.assertEqual(ri.fat, 0.0)

    def test_decimal_precision(self):
        ri = self._make_recipe_ingredient(
            calories_per_100g=52.0,
            protein_g=0.3,
            carbs_g=13.8,
            fat_g=0.2,
            quantity=120.0,
        )
        self.assertAlmostEqual(ri.calories, 62.4, places=1)
        self.assertAlmostEqual(ri.carbs, 16.56, places=1)

    def test_large_quantity_scales_correctly(self):
        ri = self._make_recipe_ingredient(
            calories_per_100g=200.0,
            protein_g=20.0,
            carbs_g=30.0,
            fat_g=10.0,
            quantity=1000.0,
        )
        self.assertAlmostEqual(ri.calories, 2000.0)
        self.assertAlmostEqual(ri.protein, 200.0)
        self.assertAlmostEqual(ri.carbs, 300.0)
        self.assertAlmostEqual(ri.fat, 100.0)


class TestRecipeIngredientUnitMacroCalculation(TestCase):
    """Integration tests using real DB objects: RecipeIngredient.__new__() + a
    mocked .ingredient FK breaks under this project's Django version (see the
    pre-existing failures in TestRecipeIngredientMacroCalculation above), so
    unit-based coverage is written against real model instances instead."""

    def setUp(self):
        from apps.accounts.models import CustomUser
        from apps.ingredients.models import Ingredient
        from apps.recipes.models import Recipe, RecipeIngredient

        user = CustomUser.objects.create_user(
            username="unitmacrouser", email="unitmacro@example.com", password="testpass123"
        )
        self.egg = Ingredient.objects.create(
            user=user,
            name="Egg",
            measurement_type=Ingredient.MeasurementType.UNIT,
            unit_label="egg",
            calories_per_unit=70.0,
            protein_per_unit=6.0,
            carbs_per_unit=1.0,
            fat_per_unit=5.0,
        )
        self.recipe = Recipe.objects.create(user=user, name="Boiled eggs")
        self.RecipeIngredient = RecipeIngredient

    def test_unit_based_macros_calculated_correctly(self):
        ri = self.RecipeIngredient.objects.create(
            recipe=self.recipe, ingredient=self.egg, quantity=2
        )
        self.assertAlmostEqual(ri.calories, 140.0)
        self.assertAlmostEqual(ri.protein, 12.0)
        self.assertAlmostEqual(ri.carbs, 2.0)
        self.assertAlmostEqual(ri.fat, 10.0)

    def test_unit_based_zero_quantity_returns_zero_macros(self):
        ri = self.RecipeIngredient.objects.create(
            recipe=self.recipe, ingredient=self.egg, quantity=0
        )
        self.assertEqual(ri.calories, 0.0)
        self.assertEqual(ri.protein, 0.0)


class TestIngredientSerializerValidation(SimpleTestCase):
    def _make_serializer(self, data):
        from apps.ingredients.serializers import IngredientSerializer

        return IngredientSerializer(data=data)

    def test_weight_ingredient_missing_macro_field_is_invalid(self):
        serializer = self._make_serializer(
            {
                "name": "Tomato",
                "measurement_type": "weight",
                "calories_per_100g": 18.0,
                "protein_g": 0.9,
                "carbs_g": 3.9,
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("fat_g", serializer.errors)

    def test_weight_ingredient_with_all_fields_is_valid(self):
        serializer = self._make_serializer(
            {
                "name": "Tomato",
                "measurement_type": "weight",
                "calories_per_100g": 18.0,
                "protein_g": 0.9,
                "carbs_g": 3.9,
                "fat_g": 0.2,
            }
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_unit_ingredient_missing_unit_label_is_invalid(self):
        serializer = self._make_serializer(
            {
                "name": "Egg",
                "measurement_type": "unit",
                "calories_per_unit": 70.0,
                "protein_per_unit": 6.0,
                "carbs_per_unit": 1.0,
                "fat_per_unit": 5.0,
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("unit_label", serializer.errors)

    def test_unit_ingredient_with_all_fields_is_valid(self):
        serializer = self._make_serializer(
            {
                "name": "Egg",
                "measurement_type": "unit",
                "unit_label": "egg",
                "calories_per_unit": 70.0,
                "protein_per_unit": 6.0,
                "carbs_per_unit": 1.0,
                "fat_per_unit": 5.0,
            }
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
