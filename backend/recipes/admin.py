from django.contrib import admin

from .models import Favorite, Ingredient, Recipe, Tag


class RecipeAdmin(admin.ModelAdmin):
    def recipe_in_favorites_count(self, obj):
        return Favorite.objects.filter(favorite_recipe=obj).count()

    recipe_in_favorites_count.short_description = 'In favorites count'
    list_display = ('name', 'author', 'recipe_in_favorites_count')
    list_filter = ('name', 'author__username', 'tags__name')
    search_fields = ('name',)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    # list_filter = ('name',)
    search_fields = ('name',)


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color')
    search_fields = ('name', 'slug')


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
