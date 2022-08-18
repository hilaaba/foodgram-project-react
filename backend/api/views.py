from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import mixins, permissions, status, views, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS
from rest_framework.response import Response

from recipes.models import (
    Favorite,
    Ingredient,
    IngredientRecipe,
    Recipe,
    ShoppingCart,
    Tag,
)
from users.models import Follow, User

from .filters import IngredientSearchFilter, RecipesFilter
from .pagination import LimitPageNumberPagination
from .permissions import (
    AdminPermission,
    CurrentUserPermission,
    ReadOnlyPermission
)
from .serializers import (
    CustomPasswordSerializer,
    CustomUserCreateSerializer,
    CustomUserSerializer,
    FavoriteSerializer,
    FollowSerializer,
    IngredientSerializer,
    RecipeGetSerializer,
    RecipePostSerializer,
    ShoppingCartCreateDestroySerializer,
    TagSerializer
)


class CustomUserViewSet(UserViewSet):

    def get_serializer_class(self):
        if self.action == 'create':
            return CustomUserCreateSerializer
        elif self.action == 'set_password':
            return CustomPasswordSerializer
        return CustomUserSerializer

    def get_permissions(self):
        if self.action == 'retrieve':
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    def get_queryset(self):
        return User.objects.all()


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AdminPermission | ReadOnlyPermission,)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AdminPermission | ReadOnlyPermission,)
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (
        AdminPermission | CurrentUserPermission | ReadOnlyPermission,
    )
    pagination_class = LimitPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipesFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeGetSerializer
        return RecipePostSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        serializer = RecipeGetSerializer(
            instance=serializer.instance,
            context={'request': self.request}
        )
        return Response(
            serializer.data, status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        serializer = RecipeGetSerializer(
            instance=serializer.instance,
            context={'request': self.request}
        )
        return Response(
            serializer.data, status=status.HTTP_200_OK
        )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class FollowBaseViewSet(viewsets.GenericViewSet):
    serializer_class = FollowSerializer

    def get_queryset(self):
        return self.request.user.follower.all()


class FollowListViewSet(mixins.ListModelMixin, FollowBaseViewSet):
    pagination_class = LimitPageNumberPagination


class FollowCreateDestroyViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    FollowBaseViewSet
):
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['author_id'] = self.kwargs.get('user_id')
        return context

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            author=get_object_or_404(
                User, id=self.kwargs.get('user_id')
            ))

    @action(methods=['delete'], detail=True)
    def delete(self, request, user_id):
        get_object_or_404(
            Follow,
            user=request.user,
            author_id=user_id
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = FavoriteSerializer

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['recipe_id'] = self.kwargs.get('recipe_id')
        return context

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            favorite_recipe=get_object_or_404(
                Recipe, id=self.kwargs.get('recipe_id')
            ))

    @action(methods=['delete'], detail=True)
    def delete(self, request, recipe_id):
        get_object_or_404(
            Favorite,
            user=request.user,
            favorite_recipe_id=recipe_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartCreateDestroyViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartCreateDestroySerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['recipe_id'] = self.kwargs.get('recipe_id')
        return context

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            recipe=get_object_or_404(
                Recipe, id=self.kwargs.get('recipe_id')
            ))

    @action(methods=['delete'], detail=True)
    def delete(self, request, recipe_id):
        get_object_or_404(
            ShoppingCart,
            user=request.user,
            recipe_id=recipe_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartDownloadAPIView(views.APIView):

    def get_queryset(self):
        return ShoppingCart.objects.filter(user=self.request.user)

    def get(self, request):
        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )
        return self._create_shopping_list(self.get_queryset(), response)

    def _create_shopping_list(self, queryset, response):
        ingredients_and_amount = {}
        response.write('Список продуктов:\n')
        for item in queryset:
            ingredients_recipe = IngredientRecipe.objects.filter(
                recipe=item.recipe
            )
            for row in ingredients_recipe:
                ingredient = row.ingredient
                amount = row.amount
                if ingredient in ingredients_and_amount:
                    ingredients_and_amount[ingredient] += amount
                else:
                    ingredients_and_amount[ingredient] = amount
        for ingredient, amount in ingredients_and_amount.items():
            response.write(f'\n{ingredient.name}')
            response.write((f' ({ingredient.measurement_unit})'))
            response.write(f' - {amount}')
        return response

