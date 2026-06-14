from types import SimpleNamespace
from unittest.mock import MagicMock, patch
 
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.test import SimpleTestCase
from rest_framework import serializers, status
from rest_framework.test import APIRequestFactory, force_authenticate
 
from apps.ingredients.views import IngredientViewSet
from apps.recipes.views import RecipeViewSet
 
 
# ---------------------------------------------------------------------------
# Funcionalidad 1: Crear ingrediente
# ---------------------------------------------------------------------------
 
class IngredientCreateViewUnitTests(SimpleTestCase):
 
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = IngredientViewSet.as_view({'post': 'create'})
        self.user = SimpleNamespace(id=1, is_authenticated=True, is_active=True)
 
    def _make_serializer_instance(self, valid=True, data=None, save_return=None,
                                  save_side_effect=None, is_valid_side_effect=None):
        instance = MagicMock()
        if is_valid_side_effect is not None:
            instance.is_valid.side_effect = is_valid_side_effect
        else:
            if valid:
                instance.is_valid.return_value = True
            else:
                def _invalid(raise_exception=False):
                    if raise_exception:
                        raise serializers.ValidationError(data or {})
                    return False
                instance.is_valid.side_effect = _invalid
 
        instance.save.return_value = save_return
        if save_side_effect is not None:
            instance.save.side_effect = save_side_effect
        instance.data = data or {}
        return instance
 
    def test_create_ingredient_success(self):
        """Crear ingrediente con datos válidos retorna 201 y los datos correctos."""
        payload = {
            'name': 'Tomato',
            'calories_per_100g': 18.0,
            'protein_g': 0.9,
            'carbs_g': 3.9,
            'fat_g': 0.2,
        }
        expected_response = {
            'id': 1, 'name': 'Tomato', 'calories_per_100g': 18.0,
            'protein_g': 0.9, 'carbs_g': 3.9, 'fat_g': 0.2,
            'is_default': False, 'created_at': None, 'updated_at': None,
        }
        mock_serializer = self._make_serializer_instance(valid=True, data=expected_response)
 
        with patch.object(IngredientViewSet, 'serializer_class', new=MagicMock(return_value=mock_serializer)):
            request = self.factory.post('/api/ingredients/', payload, format='json')
            force_authenticate(request, user=self.user)
            response = self.view(request)
 
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, expected_response)
        mock_serializer.save.assert_called_once_with(user=self.user, is_default=False)
 
    def test_create_ingredient_missing_required_field(self):
        """Crear ingrediente sin 'name' retorna 400 con detalle del error."""
        payload = {'calories_per_100g': 10.0, 'protein_g': 1.0, 'carbs_g': 2.0, 'fat_g': 0.5}
        error_detail = {'name': ['This field is required.']}
 
        def is_valid_side_effect(raise_exception=False):
            raise serializers.ValidationError(error_detail)
 
        mock_serializer = self._make_serializer_instance(
            valid=False, is_valid_side_effect=is_valid_side_effect
        )
 
        with patch.object(IngredientViewSet, 'serializer_class', new=MagicMock(return_value=mock_serializer)):
            request = self.factory.post('/api/ingredients/', payload, format='json')
            force_authenticate(request, user=self.user)
            response = self.view(request)
 
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, error_detail)
 
    def test_create_ingredient_invalid_data_type(self):
        """Crear ingrediente con tipo inválido en calories retorna 400."""
        payload = {'name': 'Salt', 'calories_per_100g': 'not_a_number',
                   'protein_g': 0.0, 'carbs_g': 0.0, 'fat_g': 0.0}
        error_detail = {'calories_per_100g': ['A valid number is required.']}
 
        def is_valid_side_effect(raise_exception=False):
            raise serializers.ValidationError(error_detail)
 
        mock_serializer = self._make_serializer_instance(
            valid=False, is_valid_side_effect=is_valid_side_effect
        )
 
        with patch.object(IngredientViewSet, 'serializer_class', new=MagicMock(return_value=mock_serializer)):
            request = self.factory.post('/api/ingredients/', payload, format='json')
            force_authenticate(request, user=self.user)
            response = self.view(request)
 
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, error_detail)
 
    def test_create_ingredient_is_default_enforced_false(self):
        """El campo is_default siempre se guarda como False aunque el cliente envíe True."""
        payload = {'name': 'Cucumber', 'calories_per_100g': 15.0,
                   'protein_g': 0.7, 'carbs_g': 3.6, 'fat_g': 0.1, 'is_default': True}
        expected_response = {
            'id': 2, 'name': 'Cucumber', 'calories_per_100g': 15.0,
            'protein_g': 0.7, 'carbs_g': 3.6, 'fat_g': 0.1,
            'is_default': False, 'created_at': None, 'updated_at': None,
        }
        mock_serializer = self._make_serializer_instance(valid=True, data=expected_response)
 
        with patch.object(IngredientViewSet, 'serializer_class', new=MagicMock(return_value=mock_serializer)):
            request = self.factory.post('/api/ingredients/', payload, format='json')
            force_authenticate(request, user=self.user)
            response = self.view(request)
 
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_serializer.save.assert_called_once_with(user=self.user, is_default=False)
 
    def test_create_ingredient_incorrect_content_type_returns_415(self):
        """Content-type no soportado retorna 415."""
        def is_valid_side_effect(raise_exception=False):
            raise serializers.ValidationError({})
 
        mock_serializer = self._make_serializer_instance(
            valid=False, is_valid_side_effect=is_valid_side_effect
        )
 
        with patch.object(IngredientViewSet, 'serializer_class', new=MagicMock(return_value=mock_serializer)):
            request = self.factory.post('/api/ingredients/', 'not-json', content_type='text/plain')
            force_authenticate(request, user=self.user)
            response = self.view(request)
 
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        self.assertIn('Unsupported media type', str(response.data.get('detail')))
 
 
# ---------------------------------------------------------------------------
# Funcionalidad 2: Crear receta
# ---------------------------------------------------------------------------
 
class RecipeCreateViewUnitTests(SimpleTestCase):
 
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = RecipeViewSet.as_view({'post': 'create'})
        self.user = SimpleNamespace(id=1, is_authenticated=True, is_active=True)
 
    def _make_serializer_instance(self, valid=True, data=None,
                                  save_return=None, is_valid_side_effect=None):
        instance = MagicMock()
        if is_valid_side_effect is not None:
            instance.is_valid.side_effect = is_valid_side_effect
        else:
            if valid:
                instance.is_valid.return_value = True
            else:
                def _invalid(raise_exception=False):
                    if raise_exception:
                        raise serializers.ValidationError(data or {})
                    return False
                instance.is_valid.side_effect = _invalid
 
        instance.save.return_value = save_return
        instance.data = data or {}
        return instance
 
    def test_create_recipe_success(self):
        """Crear receta con datos válidos retorna 201 y los datos correctos."""
        payload = {'name': 'Garden Salad', 'description': 'Fresh vegetables'}
        expected_response = {
            'id': 1, 'name': 'Garden Salad',
            'description': 'Fresh vegetables', 'is_default': False,
            'ingredients_rel': [], 'total_calories': 0.0,
            'total_protein': 0.0, 'total_carbs': 0.0, 'total_fat': 0.0,
            'created_at': None, 'updated_at': None,
        }
        mock_serializer = self._make_serializer_instance(valid=True, data=expected_response)
        mock_serializer_cls = MagicMock(return_value=mock_serializer)
 
        with patch.object(RecipeViewSet, 'get_serializer_class', return_value=mock_serializer_cls):
            request = self.factory.post('/api/recipes/', payload, format='json')
            force_authenticate(request, user=self.user)
            response = self.view(request)
 
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, expected_response)
        mock_serializer.save.assert_called_once_with(user=self.user, is_default=False)
 
    def test_create_recipe_missing_name_returns_400(self):
        """Crear receta sin 'name' retorna 400."""
        payload = {'description': 'Only description provided'}
        error_detail = {'name': ['This field is required.']}
 
        def is_valid_side_effect(raise_exception=False):
            raise serializers.ValidationError(error_detail)
 
        mock_serializer = self._make_serializer_instance(
            valid=False, is_valid_side_effect=is_valid_side_effect
        )
        mock_serializer_cls = MagicMock(return_value=mock_serializer)
 
        with patch.object(RecipeViewSet, 'get_serializer_class', return_value=mock_serializer_cls):
            request = self.factory.post('/api/recipes/', payload, format='json')
            force_authenticate(request, user=self.user)
            response = self.view(request)
 
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, error_detail)
 
    def test_create_recipe_invalid_name_type_returns_400(self):
        """Crear receta con nombre numérico retorna 400."""
        payload = {'name': 123, 'description': 'Invalid name type'}
        error_detail = {'name': ['Not a valid string.']}
 
        def is_valid_side_effect(raise_exception=False):
            raise serializers.ValidationError(error_detail)
 
        mock_serializer = self._make_serializer_instance(
            valid=False, is_valid_side_effect=is_valid_side_effect
        )
        mock_serializer_cls = MagicMock(return_value=mock_serializer)
 
        with patch.object(RecipeViewSet, 'get_serializer_class', return_value=mock_serializer_cls):
            request = self.factory.post('/api/recipes/', payload, format='json')
            force_authenticate(request, user=self.user)
            response = self.view(request)
 
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, error_detail)
 
    def test_create_recipe_is_default_enforced_false(self):
        """is_default siempre se guarda como False aunque el cliente envíe True."""
        payload = {'name': 'Custom Smoothie', 'is_default': True}
        expected_response = {
            'id': 2, 'name': 'Custom Smoothie', 'description': '',
            'is_default': False, 'ingredients_rel': [],
            'total_calories': 0.0, 'total_protein': 0.0,
            'total_carbs': 0.0, 'total_fat': 0.0,
            'created_at': None, 'updated_at': None,
        }
        mock_serializer = self._make_serializer_instance(valid=True, data=expected_response)
        mock_serializer_cls = MagicMock(return_value=mock_serializer)
 
        with patch.object(RecipeViewSet, 'get_serializer_class', return_value=mock_serializer_cls):
            request = self.factory.post('/api/recipes/', payload, format='json')
            force_authenticate(request, user=self.user)
            response = self.view(request)
 
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_serializer.save.assert_called_once_with(user=self.user, is_default=False)
 
    def test_create_recipe_incorrect_content_type_returns_415(self):
        """Content-type no soportado retorna 415."""
        mock_serializer_cls = MagicMock()
 
        with patch.object(RecipeViewSet, 'get_serializer_class', return_value=mock_serializer_cls):
            request = self.factory.post('/api/recipes/', 'not-json', content_type='text/plain')
            force_authenticate(request, user=self.user)
            response = self.view(request)
 
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        self.assertIn('Unsupported media type', str(response.data.get('detail')))
 
 
# ---------------------------------------------------------------------------
# Funcionalidad 3: Obtener detalle de receta
# ---------------------------------------------------------------------------
 
class RecipeDetailViewUnitTests(SimpleTestCase):
 
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = RecipeViewSet.as_view({'get': 'retrieve'})
        self.user = SimpleNamespace(id=1, is_authenticated=True, is_active=True)
 
    def _make_mock_recipe(self, recipe_id=1, name='Garden Salad', is_default=False):
        mock_recipe = MagicMock()
        mock_recipe.id = recipe_id
        mock_recipe.name = name
        mock_recipe.is_default = is_default
        mock_recipe.user = self.user
        return mock_recipe
 
    def test_retrieve_recipe_success(self):
        """Obtener receta existente retorna 200 con datos correctos."""
        recipe_data = {
            'id': 1, 'name': 'Garden Salad',
            'description': 'Fresh vegetables', 'is_default': False,
            'ingredients_rel': [], 'total_calories': 0.0,
            'total_protein': 0.0, 'total_carbs': 0.0, 'total_fat': 0.0,
            'created_at': '2026-01-01T10:00:00Z', 'updated_at': '2026-01-01T10:00:00Z',
        }
        mock_recipe = self._make_mock_recipe()
        mock_serializer = MagicMock()
        mock_serializer.data = recipe_data
 
        with patch.object(RecipeViewSet, 'get_object', return_value=mock_recipe):
            with patch.object(RecipeViewSet, 'get_serializer', return_value=mock_serializer):
                request = self.factory.get('/api/recipes/1/')
                force_authenticate(request, user=self.user)
                response = self.view(request, pk=1)
 
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, recipe_data)
 
    def test_retrieve_recipe_not_found_returns_404(self):
        """Obtener receta inexistente retorna 404."""
        with patch.object(RecipeViewSet, 'get_object', side_effect=Http404()):
            request = self.factory.get('/api/recipes/999/')
            force_authenticate(request, user=self.user)
            response = self.view(request, pk=999)
 
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
 
    def test_retrieve_recipe_with_ingredients_and_totals(self):
        """Receta con ingredientes retorna totales de macros correctos."""
        recipe_data = {
            'id': 2, 'name': 'Protein Smoothie', 'is_default': False,
            'ingredients_rel': [
                {'id': 1, 'ingredient_name': 'Banana', 'quantity_g': 100.0,
                 'calories': 89.0, 'protein': 1.09, 'carbs': 23.0, 'fat': 0.3},
                {'id': 2, 'ingredient_name': 'Milk', 'quantity_g': 200.0,
                 'calories': 134.0, 'protein': 6.8, 'carbs': 9.8, 'fat': 7.6},
            ],
            'total_calories': 223.0, 'total_protein': 7.89,
            'total_carbs': 32.8, 'total_fat': 7.9,
            'created_at': '2026-01-01T10:00:00Z', 'updated_at': '2026-01-01T10:00:00Z',
        }
        mock_recipe = self._make_mock_recipe(recipe_id=2, name='Protein Smoothie')
        mock_serializer = MagicMock()
        mock_serializer.data = recipe_data
 
        with patch.object(RecipeViewSet, 'get_object', return_value=mock_recipe):
            with patch.object(RecipeViewSet, 'get_serializer', return_value=mock_serializer):
                request = self.factory.get('/api/recipes/2/')
                force_authenticate(request, user=self.user)
                response = self.view(request, pk=2)
 
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['ingredients_rel']), 2)
        self.assertEqual(response.data['total_calories'], 223.0)
 
    def test_retrieve_default_recipe_shows_is_default_true(self):
        """Obtener receta default retorna is_default=True."""
        recipe_data = {
            'id': 3, 'name': 'Default Caesar Salad', 'is_default': True,
            'ingredients_rel': [], 'total_calories': 0.0,
            'total_protein': 0.0, 'total_carbs': 0.0, 'total_fat': 0.0,
            'created_at': '2026-01-01T10:00:00Z', 'updated_at': '2026-01-01T10:00:00Z',
        }
        mock_recipe = self._make_mock_recipe(recipe_id=3, is_default=True)
        mock_serializer = MagicMock()
        mock_serializer.data = recipe_data
 
        with patch.object(RecipeViewSet, 'get_object', return_value=mock_recipe):
            with patch.object(RecipeViewSet, 'get_serializer', return_value=mock_serializer):
                request = self.factory.get('/api/recipes/3/')
                force_authenticate(request, user=self.user)
                response = self.view(request, pk=3)
 
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_default'])
 
    def test_retrieve_recipe_response_includes_all_required_fields(self):
        """La respuesta incluye todos los campos esperados del serializer."""
        recipe_data = {
            'id': 4, 'name': 'Test Recipe', 'description': 'Testing',
            'is_default': False, 'ingredients_rel': [],
            'total_calories': 100.5, 'total_protein': 10.2,
            'total_carbs': 15.3, 'total_fat': 5.1,
            'created_at': '2026-01-01T10:00:00Z', 'updated_at': '2026-01-01T11:00:00Z',
        }
        mock_recipe = self._make_mock_recipe(recipe_id=4)
        mock_serializer = MagicMock()
        mock_serializer.data = recipe_data
 
        with patch.object(RecipeViewSet, 'get_object', return_value=mock_recipe):
            with patch.object(RecipeViewSet, 'get_serializer', return_value=mock_serializer):
                request = self.factory.get('/api/recipes/4/')
                force_authenticate(request, user=self.user)
                response = self.view(request, pk=4)
 
        required_fields = [
            'id', 'name', 'description', 'is_default', 'ingredients_rel',
            'total_calories', 'total_protein', 'total_carbs', 'total_fat',
            'created_at', 'updated_at'
        ]
        for field in required_fields:
            self.assertIn(field, response.data, msg=f"Missing field: {field}")
 
 
# ---------------------------------------------------------------------------
# Funcionalidad 4: Eliminar ingrediente de receta
# ---------------------------------------------------------------------------
 
class RecipeRemoveIngredientViewUnitTests(SimpleTestCase):
 
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = RecipeViewSet.as_view({'delete': 'remove_ingredient'})
        self.user = SimpleNamespace(id=1, is_authenticated=True, is_active=True)
        self.mock_recipe = MagicMock()
        self.mock_recipe.id = 1
 
    def _make_does_not_exist(self):
        return type('DoesNotExist', (ObjectDoesNotExist,), {})
 
    def test_remove_ingredient_success_returns_204(self):
        """Eliminar ingrediente existente retorna 204 y llama a delete()."""
        payload = {'recipe_ingredient_id': 1}
        mock_ri = MagicMock()
 
        with patch('apps.recipes.views.RecipeIngredient') as mock_ri_model:
            mock_ri_model.objects.get.return_value = mock_ri
            with patch.object(RecipeViewSet, 'get_object', return_value=self.mock_recipe):
                request = self.factory.delete(
                    '/api/recipes/1/remove_ingredient/', payload, format='json'
                )
                force_authenticate(request, user=self.user)
                response = self.view(request, pk=1)
 
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        mock_ri.delete.assert_called_once()
 
    def test_remove_ingredient_not_found_returns_404(self):
        """Eliminar ingrediente inexistente retorna 404 con mensaje de error."""
        payload = {'recipe_ingredient_id': 999}
        mock_does_not_exist = self._make_does_not_exist()
 
        with patch('apps.recipes.views.RecipeIngredient') as mock_ri_model:
            mock_ri_model.DoesNotExist = mock_does_not_exist
            mock_ri_model.objects.get.side_effect = mock_does_not_exist('Not found')
            with patch.object(RecipeViewSet, 'get_object', return_value=self.mock_recipe):
                request = self.factory.delete(
                    '/api/recipes/1/remove_ingredient/', payload, format='json'
                )
                force_authenticate(request, user=self.user)
                response = self.view(request, pk=1)
 
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
 
    def test_remove_ingredient_missing_id_returns_404(self):
        """Sin recipe_ingredient_id el get falla y retorna 404."""
        payload = {}
        mock_does_not_exist = self._make_does_not_exist()
 
        with patch('apps.recipes.views.RecipeIngredient') as mock_ri_model:
            mock_ri_model.DoesNotExist = mock_does_not_exist
            mock_ri_model.objects.get.side_effect = mock_does_not_exist('Not found')
            with patch.object(RecipeViewSet, 'get_object', return_value=self.mock_recipe):
                request = self.factory.delete(
                    '/api/recipes/1/remove_ingredient/', payload, format='json'
                )
                force_authenticate(request, user=self.user)
                response = self.view(request, pk=1)
 
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
 
    def test_remove_ingredient_invalid_id_type_returns_404(self):
        """ID como string inválido no encuentra el objeto y retorna 404."""
        payload = {'recipe_ingredient_id': 'not_a_number'}
        mock_does_not_exist = self._make_does_not_exist()
 
        with patch('apps.recipes.views.RecipeIngredient') as mock_ri_model:
            mock_ri_model.DoesNotExist = mock_does_not_exist
            mock_ri_model.objects.get.side_effect = mock_does_not_exist('Not found')
            with patch.object(RecipeViewSet, 'get_object', return_value=self.mock_recipe):
                request = self.factory.delete(
                    '/api/recipes/1/remove_ingredient/', payload, format='json'
                )
                force_authenticate(request, user=self.user)
                response = self.view(request, pk=1)
 
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
 
    def test_remove_ingredient_none_id_returns_404(self):
        """ID como None no encuentra el objeto y retorna 404."""
        payload = {'recipe_ingredient_id': None}
        mock_does_not_exist = self._make_does_not_exist()
 
        with patch('apps.recipes.views.RecipeIngredient') as mock_ri_model:
            mock_ri_model.DoesNotExist = mock_does_not_exist
            mock_ri_model.objects.get.side_effect = mock_does_not_exist('Not found')
            with patch.object(RecipeViewSet, 'get_object', return_value=self.mock_recipe):
                request = self.factory.delete(
                    '/api/recipes/1/remove_ingredient/', payload, format='json'
                )
                force_authenticate(request, user=self.user)
                response = self.view(request, pk=1)
 
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
 
    def test_remove_ingredient_recipe_not_found_returns_404(self):
        """Si la receta no existe retorna 404."""
        payload = {'recipe_ingredient_id': 1}
 
        with patch.object(RecipeViewSet, 'get_object', side_effect=Http404()):
            request = self.factory.delete(
                '/api/recipes/999/remove_ingredient/', payload, format='json'
            )
            force_authenticate(request, user=self.user)
            response = self.view(request, pk=999)
 
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
 
    def test_remove_ingredient_incorrect_content_type_returns_415(self):
        """Content-type no soportado retorna 415."""
        with patch.object(RecipeViewSet, 'get_object'):
            request = self.factory.delete(
                '/api/recipes/1/remove_ingredient/', 'not-json', content_type='text/plain'
            )
            force_authenticate(request, user=self.user)
            response = self.view(request, pk=1)
 
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
 