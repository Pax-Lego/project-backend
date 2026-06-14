from rest_framework import serializers
from apps.profiles.models import UserProfile, WeightEntry


class WeightEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = WeightEntry
        fields = ['id', 'weight_kg', 'date', 'notes', 'created_at']
        read_only_fields = ['id', 'created_at']


class UserProfileSerializer(serializers.ModelSerializer):
    age = serializers.IntegerField(read_only=True)
    current_weight = serializers.FloatField(read_only=True)
    tdee = serializers.FloatField(read_only=True)
    recommended_calories = serializers.FloatField(read_only=True)
    recommended_macros = serializers.DictField(read_only=True)
    weight_history = WeightEntrySerializer(many=True, read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'id', 'sex', 'date_of_birth', 'age', 'height_cm',
            'activity_level', 'goal', 'dietary_restrictions',
            'current_weight', 'tdee', 'recommended_calories', 'recommended_macros',
            'weight_history', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at',
            'age', 'current_weight', 'tdee', 'recommended_calories', 'recommended_macros'
        ]

    def validate_dietary_restrictions(self, value):
        valid = [r[0] for r in UserProfile.DietaryRestriction.choices]
        for item in value:
            if item not in valid:
                raise serializers.ValidationError(
                    f"'{item}' no es válido. Opciones: {', '.join(valid)}"
                )
        return value