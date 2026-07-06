from django import forms
from django.contrib import admin

from apps.profiles.models import UserProfile, WeightEntry


class UserProfileAdminForm(forms.ModelForm):
    dietary_restrictions = forms.MultipleChoiceField(
        choices=UserProfile.DietaryRestriction.choices,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model = UserProfile
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.initial["dietary_restrictions"] = (
                self.instance.dietary_restrictions or []
            )

    def clean_dietary_restrictions(self):
        return self.cleaned_data.get("dietary_restrictions", [])


class WeightEntryInline(admin.TabularInline):
    model = WeightEntry
    extra = 1


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    form = UserProfileAdminForm
    list_display = [
        "user",
        "sex",
        "goal",
        "activity_level",
        "current_weight",
        "tdee",
        "recommended_calories",
    ]
    readonly_fields = [
        "age",
        "current_weight",
        "bmr",
        "tdee",
        "recommended_calories",
        "recommended_macros",
        "created_at",
        "updated_at",
    ]
    inlines = [WeightEntryInline]


@admin.register(WeightEntry)
class WeightEntryAdmin(admin.ModelAdmin):
    list_display = ["profile", "weight_kg", "date"]
