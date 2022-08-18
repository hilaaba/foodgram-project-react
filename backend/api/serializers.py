from djoser.serializers import (
    PasswordSerializer,
    UserCreateSerializer,
    UserSerializer
)
from drf_extra_fields.fields import Base64ImageField
from rest_framework.generics import get_object_or_404
from rest_framework.serializers import (
    CharField,
    CurrentUserDefault,
    HiddenField,
    IntegerField,
    ListField,
    ModelSerializer,
    PrimaryKeyRelatedField,
    ReadOnlyField,
    SerializerMethodField,
    ValidationError,
)

from recipes.models import (
    Favorite,
    Ingredient,
    IngredientRecipe,
    Recipe,
    ShoppingCart,
    Tag,
    TagRecipe
)
from users.models import Follow, User


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password')
        required_fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
        )


class CustomUserSerializer(UserSerializer):
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return (user.is_authenticated and Follow.objects.filter(
            user=user,
            author=obj,
        ).exists())


class CustomPasswordSerializer(PasswordSerializer):
    current_password = CharField(required=True)


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientInRecipePostSerializer(ModelSerializer):
    id = IntegerField()
    amount = IntegerField()

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')
        required_fields = ('id', 'amount')


class RecipePostSerializer(ModelSerializer):
    ingredients = IngredientInRecipePostSerializer(many=True)
    tags = ListField(child=PrimaryKeyRelatedField(queryset=Tag.objects.all()))
    author = HiddenField(default=CurrentUserDefault())
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = '__all__'
        required_fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)

        for tag in tags:
            TagRecipe.objects.create(tag=tag, recipe=recipe)

        for ingredient in ingredients:
            IngredientRecipe.objects.create(
                ingredient=get_object_or_404(
                    Ingredient,
                    id=ingredient.get('id'),
                ),
                amount=ingredient.get('amount'),
                recipe=recipe,
            )
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time,
        )
        instance.save()

        TagRecipe.objects.filter(recipe=instance).delete()
        for tag in tags:
            TagRecipe.objects.create(
                tag=get_object_or_404(
                    Tag,
                    id=tag.id),
                recipe=instance,
            )

        IngredientRecipe.objects.filter(recipe=instance).delete()
        for ingredient in ingredients:
            IngredientRecipe.objects.filter(recipe=instance).create(
                ingredient=get_object_or_404(
                    Ingredient,
                    id=ingredient.get('id'),
                ),
                amount=ingredient.get('amount'),
                recipe=instance,
            )
        return instance


class IngredientInRecipeGetSerializer(ModelSerializer):
    id = IntegerField(source='ingredient.id')
    name = CharField(source='ingredient.name')
    measurement_unit = CharField(source='ingredient.measurement_unit')

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeGetSerializer(ModelSerializer):
    ingredients = IngredientInRecipeGetSerializer(
        many=True,
        source='ingredient',
    )
    tags = TagSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return user.is_authenticated and Favorite.objects.filter(
            user=user,
            favorite_recipe=obj,
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return user.is_authenticated and ShoppingCart.objects.filter(
            user=user,
            recipe=obj,
        ).exists()


class RecipeInFollowSerializer(ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(ModelSerializer):
    email = CharField(
        source='author.email',
        read_only=True,
    )
    id = IntegerField(
        source='author.id',
        read_only=True,
    )
    username = CharField(
        source='author.username',
        read_only=True,
    )
    first_name = CharField(
        source='author.first_name',
        read_only=True,
    )
    last_name = CharField(
        source='author.last_name',
        read_only=True,
    )
    is_subscribed = SerializerMethodField()
    recipes = SerializerMethodField()
    recipes_count = ReadOnlyField(source='author.recipes.count')

    class Meta:
        model = Follow
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def validate(self, data):
        user = User.objects.get(id=self.context['request'].user.id)
        author = User.objects.get(id=self.context['author_id'])
        if user == author:
            raise ValidationError('Нельзя подписаться на самого себя!')
        if Follow.objects.filter(user=user, author=author).exists():
            raise ValidationError('Вы уже подписаны на этого автора!')
        return data

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(
            user=self.context['request'].user,
            author=obj.author,
        ).exists()

    def get_recipes(self, obj):
        queryset = Recipe.objects.filter(author=obj.author)
        limit = self.context.get('request').query_params.get('recipes_limit')
        if limit:
            try:
                limit = int(limit)
                queryset = queryset[:limit]
            except ValueError:
                pass
        serializer = RecipeInFollowSerializer(queryset, many=True)
        return serializer.data


class FavoriteSerializer(ModelSerializer):
    id = IntegerField(
        source='favorite_recipe.id',
        read_only=True,
    )
    name = CharField(
        source='favorite_recipe.name',
        read_only=True,
    )
    image = CharField(
        source='favorite_recipe.image',
        read_only=True,
    )
    cooking_time = IntegerField(
        source='favorite_recipe.cooking_time',
        read_only=True,
    )

    class Meta:
        model = Favorite
        fields = ('id', 'name', 'image', 'cooking_time')

    def validate(self, data):
        user = User.objects.get(id=self.context['request'].user.id)
        favorite_recipe = Recipe.objects.get(id=self.context['recipe_id'])
        if Favorite.objects.filter(
                user=user,
                favorite_recipe=favorite_recipe,
        ).exists():
            raise ValidationError('Этот товар уже есть у вас в избранном!')
        return data


class ShoppingCartCreateDestroySerializer(ModelSerializer):
    id = IntegerField(source='recipe.id', read_only=True)
    name = CharField(source='recipe.name', read_only=True)
    image = CharField(source='recipe.image', read_only=True)
    cooking_time = IntegerField(source='recipe.cooking_time', read_only=True)

    class Meta:
        model = ShoppingCart
        fields = ('id', 'name', 'image', 'cooking_time')

    def validate(self, data):
        user = User.objects.get(id=self.context['request'].user.id)
        recipe = Recipe.objects.get(id=self.context['recipe_id'])
        if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            raise ValidationError(
                'Этот товар уже есть в вашем списке покупок!'
            )
        return data
