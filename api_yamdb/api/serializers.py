from datetime import datetime

from django.db.models import Avg
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ('id',)
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ('id',)
        model = Genre


class TitleSlugSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(queryset=Category.objects.all(),
                                            slug_field='slug', )
    genre = serializers.SlugRelatedField(queryset=Genre.objects.all(),
                                         slug_field='slug', many=True,
                                         )

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre',
                  'category')
        read_only_fields = ('rating',)


class TitleSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = serializers.SerializerMethodField(method_name='get_rating')

    def get_rating(self, title):
        scores = Review.objects.filter(
            title_id=title.id).aggregate(Avg('score'))
        if scores:
            return scores['score__avg']
        return None

    def validate_year(self, year):
        if year > datetime.now().year:
            raise ValidationError(
                f'Нельзя вводить год больше {datetime.now().year}.')
        return year

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating', 'description', 'genre',
                  'category')
        read_only_fields = ('rating',)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )
        ref_name = 'ReadOnlyUsers'


class SendConfirmationCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254, required=True)
    username = serializers.RegexField(
        max_length=150, required=True, regex=r"^[\w.@+-]+\Z"
    )

    class Meta:
        model = User
        fields = ('email', 'username')

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                f'Некорректный username = "{value}"'
            )
        return value


class SendTokenSerializer(serializers.Serializer):
    username = serializers.RegexField(
        max_length=150, required=True, regex=r"^[\w.@+-]+\Z"
    )
    confirmation_code = serializers.CharField(required=True)


class UpdateSelfSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=254, required=False)
    username = serializers.RegexField(
        max_length=150, required=False, regex=r"^[\w.@+-]+\Z"
    )

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio'
        )


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
    )

    title = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name',
    )

    def validate(self, data):
        request = self.context['request']
        author = request.user
        title_id = self.context['view'].kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        if request.method == 'POST':
            if Review.objects.filter(title=title, author=author).exists():
                raise ValidationError('Вы не можете добавить более'
                                      'одного отзыва на произведение')
        return data

    class Meta:
        fields = ('id', 'text', 'author', 'title', 'pub_date', 'score')
        model = Review


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
    )
    review = serializers.SlugRelatedField(
        read_only=True,
        slug_field='text',
    )

    class Meta:
        fields = ('id', 'author', 'review', 'text', 'pub_date')
        model = Comment
