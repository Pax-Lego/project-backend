from django.db.models import Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.ingredients.models import Ingredient
from apps.ingredients.serializers import IngredientSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    serializer_class = IngredientSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Ingredient.objects.filter(Q(user=self.request.user) | Q(is_default=True))

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, is_default=False)

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        instance.delete()

    @action(detail=False, methods=["get"])
    def defaults(self, request):
        ingredients = Ingredient.objects.filter(is_default=True)
        serializer = self.get_serializer(ingredients, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def mine(self, request):
        ingredients = Ingredient.objects.filter(user=request.user)
        serializer = self.get_serializer(ingredients, many=True)
        return Response(serializer.data)
