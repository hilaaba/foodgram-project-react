from django_filters.rest_framework import (
    BooleanFilter, FilterSet, ModelMultipleChoiceFilter,
)
from rest_framework.filters import SearchFilter

from recipes.models import Recipe, Tag


class RecipesFilter(FilterSet):
    tags = ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug'
    )
    is_favorited = BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = BooleanFilter(
        method='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(favorite_recipe__user=user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(recipe_in_shopping_cart__user=user)
        return queryset


class IngredientSearchFilter(SearchFilter):
    search_param = 'name'
