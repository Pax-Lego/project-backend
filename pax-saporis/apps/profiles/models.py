from django.db import models
from apps.accounts.models import CustomUser


class UserProfile(models.Model):

    class Sex(models.TextChoices):
        MALE = 'male', 'Masculino'
        FEMALE = 'female', 'Femenino'

    class ActivityLevel(models.TextChoices):
        SEDENTARY = 'sedentary', 'Sedentario (poco o nada de ejercicio)'
        LIGHT = 'light', 'Ligero (ejercicio 1-3 días/semana)'
        MODERATE = 'moderate', 'Moderado (ejercicio 3-5 días/semana)'
        ACTIVE = 'active', 'Activo (ejercicio 6-7 días/semana)'
        VERY_ACTIVE = 'very_active', 'Muy activo (ejercicio intenso diario)'

    class Goal(models.TextChoices):
        LOSE_WEIGHT = 'lose_weight', 'Bajar de peso'
        MAINTAIN = 'maintain', 'Mantener peso'
        GAIN_WEIGHT = 'gain_weight', 'Subir de peso'
        BUILD_MUSCLE = 'build_muscle', 'Construir músculo'

    class DietaryRestriction(models.TextChoices):
        VEGAN = 'vegan', 'Vegano'
        VEGETARIAN = 'vegetarian', 'Vegetariano'
        GLUTEN_FREE = 'gluten_free', 'Sin gluten'
        LACTOSE_FREE = 'lactose_free', 'Sin lactosa'
        NUT_FREE = 'nut_free', 'Sin nueces'
        HALAL = 'halal', 'Halal'
        KOSHER = 'kosher', 'Kosher'
        LOW_SODIUM = 'low_sodium', 'Bajo en sodio'
        DIABETIC = 'diabetic', 'Diabético'

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    sex = models.CharField(max_length=10, choices=Sex.choices, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    height_cm = models.FloatField(null=True, blank=True, help_text="Altura en centímetros")
    activity_level = models.CharField(max_length=20, choices=ActivityLevel.choices, null=True, blank=True)
    goal = models.CharField(max_length=20, choices=Goal.choices, null=True, blank=True)
    dietary_restrictions = models.JSONField(default=list, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Perfil de {self.user.email}"

    @property
    def age(self):
        if not self.date_of_birth:
            return None
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )

    @property
    def current_weight(self):
        entry = self.weight_history.order_by('-date').first()
        return entry.weight_kg if entry else None

    @property
    def bmr(self):
        """Mifflin-St Jeor"""
        weight = self.current_weight
        if not all([weight, self.height_cm, self.age, self.sex]):
            return None
        if self.sex == self.Sex.MALE:
            return (10 * weight) + (6.25 * self.height_cm) - (5 * self.age) + 5
        return (10 * weight) + (6.25 * self.height_cm) - (5 * self.age) - 161

    @property
    def tdee(self):
        if not self.bmr or not self.activity_level:
            return None
        multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'active': 1.725,
            'very_active': 1.9,
        }
        return round(self.bmr * multipliers[self.activity_level], 2)

    @property
    def recommended_calories(self):
        if not self.tdee or not self.goal:
            return None
        adjustments = {
            'lose_weight': -500,
            'maintain': 0,
            'gain_weight': +300,
            'build_muscle': +250,
        }
        return round(self.tdee + adjustments[self.goal], 2)

    @property
    def recommended_macros(self):
        calories = self.recommended_calories
        if not calories or not self.goal:
            return None

        # Distribución de macros según objetivo
        distributions = {
            'lose_weight':    {'protein': 0.40, 'carbs': 0.35, 'fat': 0.25},
            'maintain':       {'protein': 0.30, 'carbs': 0.40, 'fat': 0.30},
            'gain_weight':    {'protein': 0.25, 'carbs': 0.50, 'fat': 0.25},
            'build_muscle':   {'protein': 0.35, 'carbs': 0.45, 'fat': 0.20},
        }
        dist = distributions[self.goal]

        return {
            'calories': calories,
            'protein_g': round((calories * dist['protein']) / 4, 1),
            'carbs_g':   round((calories * dist['carbs'])   / 4, 1),
            'fat_g':     round((calories * dist['fat'])     / 9, 1),
        }


class WeightEntry(models.Model):
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='weight_history')
    weight_kg = models.FloatField()
    date = models.DateField()
    notes = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        unique_together = ('profile', 'date')

    def __str__(self):
        return f"{self.profile.user.email} - {self.weight_kg}kg ({self.date})"