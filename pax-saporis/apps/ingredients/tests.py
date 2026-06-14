from types import SimpleNamespace
from unittest.mock import MagicMock, patch
 
from django.core.exceptions import ObjectDoesNotExist
from django.test import SimpleTestCase
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate
 
from apps.recipes.views import RecipeViewSet
from apps.ingredients.views import IngredientViewSet
 
 
# ---------------------------------------------------------------------------
# Funcionalidad 1: Agregar ingrediente a receta — validación de campos
# ---------------------------------------------------------------------------
 
class TestAddIngredientValidationView(SimpleTestCase):
    """
    Prueba 1: El endpoint add_ingredient valida que ingredient_id
    y quantity_g estén presentes antes de procesar la solicitud.
    """
 
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = RecipeViewSet.as_view({'post': 'add_ingredient'})
        self.user = SimpleNamespace(id=1, is_authenticated=True, is_active=True)
        self.mock_recipe = MagicMock()
        self.mock_recipe.id = 1
 
    def test_missing_quantity_returns_400(self):
        """Si falta quantity_g el endpoint retorna 400 con mensaje de error."""
        payload = {'ingredient_id': 1}
 
        with patch.object(RecipeViewSet, 'get_object', return_value=self.mock_recipe):
            request = self.factory.post(
                '/api/recipes/1/add_ingredient/', payload, format='json'
            )
            force_authenticate(request, user=self.user)
            response = self.view(request, pk=1)
 
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
 
    def test_missing_ingredient_id_returns_400(self):
        """Si falta ingredient_id el endpoint retorna 400 con mensaje de error."""
        payload = {'quantity_g': 100}
 
        with patch.object(RecipeViewSet, 'get_object', return_value=self.mock_recipe):
            request = self.factory.post(
                '/api/recipes/1/add_ingredient/', payload, format='json'
            )
            force_authenticate(request, user=self.user)
            response = self.view(request, pk=1)
 
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
 
    def test_missing_both_fields_returns_400(self):
        """Si faltan ambos campos el endpoint retorna 400."""
        payload = {}
 
        with patch.object(RecipeViewSet, 'get_object', return_value=self.mock_recipe):
            request = self.factory.post(
                '/api/recipes/1/add_ingredient/', payload, format='json'
            )
            force_authenticate(request, user=self.user)
            response = self.view(request, pk=1)
 
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
 
    def test_ingredient_not_found_returns_404(self):
        """Si el ingrediente no existe el endpoint retorna 404."""
        payload = {'ingredient_id': 999, 'quantity_g': 100}
 
        with patch.object(RecipeViewSet, 'get_object', return_value=self.mock_recipe):
            with patch('apps.recipes.views.Ingredient') as mock_ingredient_model:
                mock_does_not_exist = type('DoesNotExist', (ObjectDoesNotExist,), {})
                mock_ingredient_model.DoesNotExist = mock_does_not_exist
                mock_ingredient_model.objects.get.side_effect = mock_does_not_exist('Not found')
 
                request = self.factory.post(
                    '/api/recipes/1/add_ingredient/', payload, format='json'
                )
                force_authenticate(request, user=self.user)
                response = self.view(request, pk=1)
 
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
 
 
# ---------------------------------------------------------------------------
# Funcionalidad 2: Agregar ingrediente a receta — flujo exitoso
# ---------------------------------------------------------------------------
 
class TestAddIngredientSuccessView(SimpleTestCase):
    """
    Prueba 2: El endpoint add_ingredient crea o actualiza un
    RecipeIngredient correctamente cuando los datos son válidos.
    """
 
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = RecipeViewSet.as_view({'post': 'add_ingredient'})
        self.user = SimpleNamespace(id=1, is_authenticated=True, is_active=True)
        self.mock_recipe = MagicMock()
        self.mock_recipe.id = 1
 
    def _make_mock_recipe_ingredient(self, created=True):
        mock_ri = MagicMock()
        mock_ri.id = 1
        mock_ri.quantity_g = 150.0
        return mock_ri, created
 
    def test_add_new_ingredient_returns_200(self):
        """Agregar un ingrediente nuevo crea el RecipeIngredient y retorna 200."""
        payload = {'ingredient_id': 1, 'quantity_g': 150}
        mock_ingredient = MagicMock()
        mock_ri = MagicMock()
        mock_ri.id = 1
 
        with patch.object(RecipeViewSet, 'get_object', return_value=self.mock_recipe):
            with patch('apps.recipes.views.Ingredient') as mock_ingredient_model:
                mock_ingredient_model.objects.get.return_value = mock_ingredient
                with patch('apps.recipes.views.RecipeIngredient') as mock_ri_model:
                    mock_ri_model.objects.get_or_create.return_value = (mock_ri, True)
                    with patch('apps.recipes.views.RecipeIngredientSerializer') as mock_serializer_cls:
                        mock_serializer_cls.return_value.data = {'id': 1, 'quantity_g': 150}
 
                        request = self.factory.post(
                            '/api/recipes/1/add_ingredient/', payload, format='json'
                        )
                        force_authenticate(request, user=self.user)
                        response = self.view(request, pk=1)
 
        self.assertEqual(response.status_code, status.HTTP_200_OK)
 
    def test_add_existing_ingredient_updates_quantity(self):
        """
        Agregar un ingrediente que ya existe actualiza quantity_g
        y llama a save() — caso de actualización.
        """
        payload = {'ingredient_id': 1, 'quantity_g': 200}
        mock_ingredient = MagicMock()
        mock_ri = MagicMock()
        mock_ri.quantity_g = 100.0
 
        with patch.object(RecipeViewSet, 'get_object', return_value=self.mock_recipe):
            with patch('apps.recipes.views.Ingredient') as mock_ingredient_model:
                mock_ingredient_model.objects.get.return_value = mock_ingredient
                with patch('apps.recipes.views.RecipeIngredient') as mock_ri_model:
                    # created=False significa que ya existía
                    mock_ri_model.objects.get_or_create.return_value = (mock_ri, False)
                    with patch('apps.recipes.views.RecipeIngredientSerializer') as mock_serializer_cls:
                        mock_serializer_cls.return_value.data = {'id': 1, 'quantity_g': 200}
 
                        request = self.factory.post(
                            '/api/recipes/1/add_ingredient/', payload, format='json'
                        )
                        force_authenticate(request, user=self.user)
                        response = self.view(request, pk=1)
 
        # Cuando created=False el view actualiza quantity_g y llama save()
        self.assertEqual(mock_ri.quantity_g, 200)
        mock_ri.save.assert_called_once()
 
    def test_add_ingredient_calls_get_or_create_with_correct_args(self):
        """get_or_create se llama con la receta e ingrediente correctos."""
        payload = {'ingredient_id': 5, 'quantity_g': 75}
        mock_ingredient = MagicMock()
        mock_ri = MagicMock()
 
        with patch.object(RecipeViewSet, 'get_object', return_value=self.mock_recipe):
            with patch('apps.recipes.views.Ingredient') as mock_ingredient_model:
                mock_ingredient_model.objects.get.return_value = mock_ingredient
                with patch('apps.recipes.views.RecipeIngredient') as mock_ri_model:
                    mock_ri_model.objects.get_or_create.return_value = (mock_ri, True)
                    with patch('apps.recipes.views.RecipeIngredientSerializer') as mock_serializer_cls:
                        mock_serializer_cls.return_value.data = {}
 
                        request = self.factory.post(
                            '/api/recipes/1/add_ingredient/', payload, format='json'
                        )
                        force_authenticate(request, user=self.user)
                        self.view(request, pk=1)
 
        mock_ri_model.objects.get_or_create.assert_called_once_with(
            recipe=self.mock_recipe,
            ingredient=mock_ingredient,
            defaults={'quantity_g': 75}
        )
 
 
# ---------------------------------------------------------------------------
# Funcionalidad 3: Protección de ingredientes predeterminados
# ---------------------------------------------------------------------------
 
class TestDefaultIngredientProtectionView(SimpleTestCase):
    """
    Prueba 3: Los ingredientes predeterminados (is_default=True)
    no pueden ser editados ni eliminados por el usuario.
    """
 
    def setUp(self):
        self.factory = APIRequestFactory()
        self.update_view = IngredientViewSet.as_view({'patch': 'partial_update'})
        self.delete_view = IngredientViewSet.as_view({'delete': 'destroy'})
        self.user = SimpleNamespace(id=1, is_authenticated=True, is_active=True)
 
    def _make_mock_ingredient(self, is_default=True):
        ingredient = MagicMock()
        ingredient.id = 1
        ingredient.is_default = is_default
        ingredient.user = self.user
        return ingredient
 
    def test_update_default_ingredient_does_not_save(self):
        """Editar un ingrediente default no debe llamar a save()."""
        mock_ingredient = self._make_mock_ingredient(is_default=True)
        mock_serializer = MagicMock()
        mock_serializer.is_valid.return_value = True
        mock_serializer.data = {'id': 1, 'calories_per_100g': 200}
 
        with patch.object(IngredientViewSet, 'get_object', return_value=mock_ingredient):
            with patch.object(IngredientViewSet, 'get_serializer', return_value=mock_serializer):
                request = self.factory.patch(
                    '/api/ingredients/1/', {'calories_per_100g': 200}, format='json'
                )
                force_authenticate(request, user=self.user)
                self.update_view(request, pk=1)
 
        mock_serializer.save.assert_not_called()
 
    def test_update_non_default_ingredient_saves(self):
        """Editar un ingrediente no default sí debe llamar a save()."""
        mock_ingredient = self._make_mock_ingredient(is_default=False)
        mock_serializer = MagicMock()
        mock_serializer.is_valid.return_value = True
        mock_serializer.data = {'id': 1, 'calories_per_100g': 200}
 
        with patch.object(IngredientViewSet, 'get_object', return_value=mock_ingredient):
            with patch.object(IngredientViewSet, 'get_serializer', return_value=mock_serializer):
                request = self.factory.patch(
                    '/api/ingredients/1/', {'calories_per_100g': 200}, format='json'
                )
                force_authenticate(request, user=self.user)
                self.update_view(request, pk=1)
 
        mock_serializer.save.assert_called_once()
 
    def test_delete_default_ingredient_does_not_call_delete(self):
        """Eliminar un ingrediente default no debe llamar a instance.delete()."""
        mock_ingredient = self._make_mock_ingredient(is_default=True)
 
        with patch.object(IngredientViewSet, 'get_object', return_value=mock_ingredient):
            request = self.factory.delete('/api/ingredients/1/')
            force_authenticate(request, user=self.user)
            self.delete_view(request, pk=1)
 
        mock_ingredient.delete.assert_not_called()
 
    def test_delete_non_default_ingredient_calls_delete(self):
        """Eliminar un ingrediente no default sí debe llamar a instance.delete()."""
        mock_ingredient = self._make_mock_ingredient(is_default=False)
 
        with patch.object(IngredientViewSet, 'get_object', return_value=mock_ingredient):
            request = self.factory.delete('/api/ingredients/1/')
            force_authenticate(request, user=self.user)
            self.delete_view(request, pk=1)
 
        mock_ingredient.delete.assert_called_once()
 
 
# ---------------------------------------------------------------------------
# Funcionalidad 4: Cálculo de macros de RecipeIngredient
# ---------------------------------------------------------------------------
 
class TestRecipeIngredientMacroCalculation(SimpleTestCase):
    """
    Prueba 4: Las propiedades de cálculo de macros en RecipeIngredient
    retornan valores correctos según la cantidad en gramos.
    """
 
    def _make_recipe_ingredient(self, calories_per_100g, protein_g,
                                carbs_g, fat_g, quantity_g):
        """Helper: instancia RecipeIngredient sin pasar por la DB."""
        from apps.recipes.models import RecipeIngredient
        ri = RecipeIngredient.__new__(RecipeIngredient)
        ri.ingredient = MagicMock()
        ri.ingredient.calories_per_100g = calories_per_100g
        ri.ingredient.protein_g = protein_g
        ri.ingredient.carbs_g = carbs_g
        ri.ingredient.fat_g = fat_g
        ri.quantity_g = quantity_g
        return ri
 
    def test_calories_calculated_correctly(self):
        """Calorías = (calories_per_100g / 100) * quantity_g."""
        ri = self._make_recipe_ingredient(
            calories_per_100g=18.0, protein_g=0.9,
            carbs_g=3.9, fat_g=0.2, quantity_g=200.0
        )
        self.assertAlmostEqual(ri.calories, 36.0)
 
    def test_all_macros_calculated_correctly(self):
        """Proteína, carbos y grasa se calculan correctamente."""
        ri = self._make_recipe_ingredient(
            calories_per_100g=165.0, protein_g=31.0,
            carbs_g=0.0, fat_g=3.6, quantity_g=150.0
        )
        self.assertAlmostEqual(ri.protein, 46.5)
        self.assertAlmostEqual(ri.carbs, 0.0)
        self.assertAlmostEqual(ri.fat, 5.4)
 
    def test_zero_quantity_returns_zero_macros(self):
        """Con 0g de cantidad todos los macros deben ser 0 — caso límite."""
        ri = self._make_recipe_ingredient(
            calories_per_100g=100.0, protein_g=10.0,
            carbs_g=10.0, fat_g=5.0, quantity_g=0.0
        )
        self.assertEqual(ri.calories, 0.0)
        self.assertEqual(ri.protein, 0.0)
        self.assertEqual(ri.carbs, 0.0)
        self.assertEqual(ri.fat, 0.0)
 
    def test_decimal_precision(self):
        """Valores decimales se calculan con precisión de al menos 1 decimal."""
        ri = self._make_recipe_ingredient(
            calories_per_100g=52.0, protein_g=0.3,
            carbs_g=13.8, fat_g=0.2, quantity_g=120.0
        )
        self.assertAlmostEqual(ri.calories, 62.4, places=1)
        self.assertAlmostEqual(ri.carbs, 16.56, places=1)
 
    def test_large_quantity_scales_correctly(self):
        """Cantidades grandes escalan linealmente — caso límite de escala."""
        ri = self._make_recipe_ingredient(
            calories_per_100g=200.0, protein_g=20.0,
            carbs_g=30.0, fat_g=10.0, quantity_g=1000.0
        )
        self.assertAlmostEqual(ri.calories, 2000.0)
        self.assertAlmostEqual(ri.protein, 200.0)
        self.assertAlmostEqual(ri.carbs, 300.0)
        self.assertAlmostEqual(ri.fat, 100.0)
 