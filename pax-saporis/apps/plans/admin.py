from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet
from apps.plans.models import DailyPlan, PlanMeal


class PlanMealFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        unique_types = {'breakfast', 'lunch', 'dinner'}
        seen = set()
        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                meal_type = form.cleaned_data.get('meal_type')
                if meal_type in unique_types:
                    if meal_type in seen:
                        raise ValidationError(
                            f'Solo puede haber un "{meal_type}" por plan.'
                        )
                    seen.add(meal_type)


class PlanMealInline(admin.TabularInline):
    model = PlanMeal
    formset = PlanMealFormSet
    extra = 1
    readonly_fields = ['calories', 'protein', 'carbs', 'fat']


@admin.register(DailyPlan)
class DailyPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'date', 'total_calories', 'total_protein', 'total_carbs', 'total_fat']
    readonly_fields = ['total_calories', 'total_protein', 'total_carbs', 'total_fat', 'created_at', 'updated_at']
    inlines = [PlanMealInline]


@admin.register(PlanMeal)
class PlanMealAdmin(admin.ModelAdmin):
    list_display = ['meal_type', 'name', 'daily_plan', 'recipe', 'calories', 'protein', 'carbs', 'fat']
    readonly_fields = ['calories', 'protein', 'carbs', 'fat']