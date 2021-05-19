import graphene
from graphene_django.types import DjangoObjectType
from .models import Movie


class MovieType(DjangoObjectType):
    class Meta:
        model = Movie

    movie_age = graphene.String()

    def resolve_movie_age(self, info):
        return "old movie" if self.year < 2000 else "new movie"


class Query(graphene.ObjectType):
    all_movies = graphene.List(MovieType)
    movie = graphene.Field(
        MovieType,
        id = graphene.Int(),
        title = graphene.String()
    )

    def resolve_all_movies(self, info, **kwargs):
        return Movie.objects.all()

    def resolve_movie(self, info, **kwargs):
        id = kwargs.get("id")
        title = kwargs.get("tile")

        if id is not None:
            return Movie.objects.get(pk=id)

        if title is not None:
            return Movie.objects.get(title=title)