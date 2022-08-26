from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CustomUserViewSet, FavoriteViewSet, FollowCreateDestroyViewSet,
    FollowListViewSet, IngredientViewSet, RecipeViewSet,
    ShoppingCartCreateDestroyViewSet, ShoppingCartDownloadAPIView, TagViewSet
)

app_name = 'api'

router = DefaultRouter()

router.register(
    'users/subscriptions',
    FollowListViewSet,
    basename='subscriptions'
)
router.register(
    r'users/(?P<user_id>\d+)/subscribe',
    FollowCreateDestroyViewSet,
    basename='subscribe'
)
router.register('users', CustomUserViewSet, basename='users')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register(
    r'recipes/(?P<recipe_id>\d+)/favorite',
    FavoriteViewSet,
    basename='favorite'
)
router.register(
    r'recipes/(?P<recipe_id>\d+)/shopping_cart',
    ShoppingCartCreateDestroyViewSet,
    basename='shopping_cart'
)


urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path(
        'recipes/download_shopping_cart/',
        ShoppingCartDownloadAPIView.as_view()
    ),
    path('', include(router.urls)),
    path('', include('djoser.urls.base')),
]
