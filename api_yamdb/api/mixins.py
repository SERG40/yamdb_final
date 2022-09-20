from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet


class GenreCategModelViewSet(mixins.CreateModelMixin,
                             mixins.DestroyModelMixin,
                             mixins.ListModelMixin,
                             GenericViewSet, ):
    """
    Отдельный вьюсет, для вьюсета категориии и жанра
    """
