from django.core.management import call_command
from django.test import TestCase
from rest_framework.test import APIClient

from apps.accounts.models import CustomUser
from apps.ingredients.models import Ingredient
from apps.lists.models import IngredientList, RecipeList
from apps.recipes.models import Recipe


class IngredientListCrudTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="listowner", email="listowner@example.com", password="testpass123"
        )
        self.other_user = CustomUser.objects.create_user(
            username="otherlistuser",
            email="otherlistuser@example.com",
            password="testpass123",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_and_list_own_list(self):
        response = self.client.post(
            "/api/lists/ingredients/", {"name": "Breakfast"}, format="json"
        )
        self.assertEqual(response.status_code, 201)

        response = self.client.get("/api/lists/ingredients/")
        names = [item["name"] for item in response.json()]
        self.assertIn("Breakfast", names)

    def test_rename_own_list(self):
        list_obj = IngredientList.objects.create(user=self.user, name="Old name")
        response = self.client.patch(
            f"/api/lists/ingredients/{list_obj.id}/", {"name": "New name"}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        list_obj.refresh_from_db()
        self.assertEqual(list_obj.name, "New name")

    def test_delete_own_list(self):
        list_obj = IngredientList.objects.create(user=self.user, name="To delete")
        response = self.client.delete(f"/api/lists/ingredients/{list_obj.id}/")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(IngredientList.objects.filter(id=list_obj.id).exists())

    def test_duplicate_name_for_same_user_returns_400(self):
        IngredientList.objects.create(user=self.user, name="Keto")
        response = self.client.post(
            "/api/lists/ingredients/", {"name": "Keto"}, format="json"
        )
        self.assertEqual(response.status_code, 400)

    def test_same_name_allowed_for_different_users(self):
        IngredientList.objects.create(user=self.other_user, name="Keto")
        response = self.client.post(
            "/api/lists/ingredients/", {"name": "Keto"}, format="json"
        )
        self.assertEqual(response.status_code, 201)

    def test_cannot_see_other_users_private_list(self):
        other_list = IngredientList.objects.create(user=self.other_user, name="Private")
        response = self.client.get(f"/api/lists/ingredients/{other_list.id}/")
        self.assertEqual(response.status_code, 404)

    def test_builtin_list_visible_to_everyone(self):
        builtin = IngredientList.objects.get(is_builtin=True)
        response = self.client.get(f"/api/lists/ingredients/{builtin.id}/")
        self.assertEqual(response.status_code, 200)

    def test_builtin_list_cannot_be_renamed(self):
        builtin = IngredientList.objects.get(is_builtin=True)
        response = self.client.patch(
            f"/api/lists/ingredients/{builtin.id}/", {"name": "Hacked"}, format="json"
        )
        self.assertEqual(response.status_code, 403)

    def test_builtin_list_cannot_be_deleted(self):
        builtin = IngredientList.objects.get(is_builtin=True)
        response = self.client.delete(f"/api/lists/ingredients/{builtin.id}/")
        self.assertEqual(response.status_code, 403)
        self.assertTrue(IngredientList.objects.filter(id=builtin.id).exists())


class IngredientListMembershipTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="memberowner", email="memberowner@example.com", password="testpass123"
        )
        self.other_user = CustomUser.objects.create_user(
            username="otherowner", email="otherowner@example.com", password="testpass123"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.list_obj = IngredientList.objects.create(user=self.user, name="My list")
        self.ingredient = Ingredient.objects.create(
            user=self.user,
            name="Tomato",
            calories_per_100g=18.0,
            protein_g=0.9,
            carbs_g=3.9,
            fat_g=0.2,
        )
        self.default_ingredient = Ingredient.objects.create(
            name="Rice",
            is_default=True,
            calories_per_100g=130.0,
            protein_g=2.7,
            carbs_g=28.0,
            fat_g=0.3,
        )

    def test_add_ingredient_to_list(self):
        response = self.client.post(
            f"/api/lists/ingredients/{self.list_obj.id}/add_ingredient/",
            {"ingredient_id": self.ingredient.id},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.ingredient, self.list_obj.ingredients.all())

    def test_add_default_ingredient_to_custom_list_allowed(self):
        response = self.client.post(
            f"/api/lists/ingredients/{self.list_obj.id}/add_ingredient/",
            {"ingredient_id": self.default_ingredient.id},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.default_ingredient, self.list_obj.ingredients.all())

    def test_remove_ingredient_from_list_is_idempotent(self):
        self.list_obj.ingredients.add(self.ingredient)
        response = self.client.delete(
            f"/api/lists/ingredients/{self.list_obj.id}/remove_ingredient/",
            {"ingredient_id": self.ingredient.id},
            format="json",
        )
        self.assertEqual(response.status_code, 204)
        self.assertNotIn(self.ingredient, self.list_obj.ingredients.all())

        # removing again should not error
        response = self.client.delete(
            f"/api/lists/ingredients/{self.list_obj.id}/remove_ingredient/",
            {"ingredient_id": self.ingredient.id},
            format="json",
        )
        self.assertEqual(response.status_code, 204)

    def test_add_other_users_private_ingredient_returns_404(self):
        private_ingredient = Ingredient.objects.create(
            user=self.other_user,
            name="Secret sauce",
            calories_per_100g=100.0,
            protein_g=1.0,
            carbs_g=1.0,
            fat_g=1.0,
        )
        response = self.client.post(
            f"/api/lists/ingredients/{self.list_obj.id}/add_ingredient/",
            {"ingredient_id": private_ingredient.id},
            format="json",
        )
        self.assertEqual(response.status_code, 404)

    def test_add_ingredient_to_builtin_list_returns_403(self):
        builtin = IngredientList.objects.get(is_builtin=True)
        response = self.client.post(
            f"/api/lists/ingredients/{builtin.id}/add_ingredient/",
            {"ingredient_id": self.ingredient.id},
            format="json",
        )
        self.assertEqual(response.status_code, 403)

    def test_remove_ingredient_from_builtin_list_returns_403(self):
        builtin = IngredientList.objects.get(is_builtin=True)
        builtin.ingredients.add(self.default_ingredient)
        response = self.client.delete(
            f"/api/lists/ingredients/{builtin.id}/remove_ingredient/",
            {"ingredient_id": self.default_ingredient.id},
            format="json",
        )
        self.assertEqual(response.status_code, 403)


class RecipeListMembershipTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="recipelistowner",
            email="recipelistowner@example.com",
            password="testpass123",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.list_obj = RecipeList.objects.create(user=self.user, name="My recipes")
        self.recipe = Recipe.objects.create(user=self.user, name="Chicken bowl")

    def test_add_and_remove_recipe(self):
        response = self.client.post(
            f"/api/lists/recipes/{self.list_obj.id}/add_recipe/",
            {"recipe_id": self.recipe.id},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.recipe, self.list_obj.recipes.all())

        response = self.client.delete(
            f"/api/lists/recipes/{self.list_obj.id}/remove_recipe/",
            {"recipe_id": self.recipe.id},
            format="json",
        )
        self.assertEqual(response.status_code, 204)
        self.assertNotIn(self.recipe, self.list_obj.recipes.all())


class SyncBuiltinListsCommandTests(TestCase):
    def test_sync_attaches_all_default_ingredients_and_recipes(self):
        Ingredient.objects.create(
            name="Default A",
            is_default=True,
            calories_per_100g=100.0,
            protein_g=10.0,
            carbs_g=10.0,
            fat_g=1.0,
        )
        Ingredient.objects.create(
            name="Default B",
            is_default=True,
            calories_per_100g=200.0,
            protein_g=20.0,
            carbs_g=20.0,
            fat_g=2.0,
        )
        Ingredient.objects.create(
            name="Not default",
            is_default=False,
            calories_per_100g=50.0,
            protein_g=5.0,
            carbs_g=5.0,
            fat_g=0.5,
        )
        Recipe.objects.create(name="Default recipe", is_default=True)
        Recipe.objects.create(name="Not default recipe", is_default=False)

        call_command("sync_builtin_lists")

        ing_list = IngredientList.objects.get(is_builtin=True)
        rec_list = RecipeList.objects.get(is_builtin=True)

        self.assertEqual(
            set(ing_list.ingredients.values_list("name", flat=True)),
            {"Default A", "Default B"},
        )
        self.assertEqual(
            set(rec_list.recipes.values_list("name", flat=True)),
            {"Default recipe"},
        )

    def test_sync_is_idempotent(self):
        Ingredient.objects.create(
            name="Default A",
            is_default=True,
            calories_per_100g=100.0,
            protein_g=10.0,
            carbs_g=10.0,
            fat_g=1.0,
        )
        call_command("sync_builtin_lists")
        call_command("sync_builtin_lists")

        self.assertEqual(IngredientList.objects.filter(is_builtin=True).count(), 1)
        ing_list = IngredientList.objects.get(is_builtin=True)
        self.assertEqual(ing_list.ingredients.count(), 1)
