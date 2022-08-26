from django.contrib import admin

from .models import (
    Favorite, Ingredient, Recipe, Tag, IngredientRecipe, ShoppingCart,
)


class IngredientRecipeInline(admin.TabularInline):
    model = Recipe.ingredients.through
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'recipe_in_favorites_count')
    list_filter = ('name', 'author__username', 'tags__name')
    search_fields = ('name',)
    inlines = (IngredientRecipeInline,)

    def recipe_in_favorites_count(self, recipe):
        return Favorite.objects.filter(favorite_recipe=recipe).count()

    recipe_in_favorites_count.short_description = 'In favorites count'


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color')
    search_fields = ('name', 'slug')


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'favorite_recipe')
    search_fields = ('user', 'favorite_recipe')


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user', 'favorite_recipe')


class IngredientRecipeAdmin(admin.ModelAdmin):
    list_display = ('ingredient', 'recipe', 'amount')


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(IngredientRecipe, IngredientRecipeAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Favorite, FavoriteAdmin)
