from rest_framework import serializers

from apps.ingredients.models import Ingredient


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = [
            "id",
            "name",
            "is_default",
            "measurement_type",
            "calories_per_100g",
            "protein_g",
            "carbs_g",
            "fat_g",
            "unit_label",
            "calories_per_unit",
            "protein_per_unit",
            "carbs_per_unit",
            "fat_per_unit",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "is_default"]

    def validate(self, data):
        measurement_type = data.get(
            "measurement_type",
            getattr(self.instance, "measurement_type", Ingredient.MeasurementType.WEIGHT),
        )

        def field_value(name):
            if name in data:
                return data[name]
            return getattr(self.instance, name, None)

        if measurement_type == Ingredient.MeasurementType.WEIGHT:
            required = ["calories_per_100g", "protein_g", "carbs_g", "fat_g"]
        else:
            required = [
                "unit_label",
                "calories_per_unit",
                "protein_per_unit",
                "carbs_per_unit",
                "fat_per_unit",
            ]

        missing = [f for f in required if field_value(f) in (None, "")]
        if missing:
            raise serializers.ValidationError(
                {
                    field: "Este campo es requerido para el tipo de medición seleccionado."
                    for field in missing
                }
            )
        return data
