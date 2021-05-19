import graphene
from graphene import relay
import graphql_jwt
from graphql_jwt.decorators import login_required
from graphene_django.types import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql_relay import from_global_id

from .models import Movie, Director


class MovieType(DjangoObjectType):
    class Meta:
        model = Movie

    movie_age = graphene.String()

    def resolve_movie_age(self, info):
        return "old movie" if self.year < 2000 else "new movie"


# Special object type for Relay
class MovieNode(DjangoObjectType):
    class Meta:
        model = Movie
        filter_fields = {
            'title': ['exact', 'icontains', 'istartswith'],
            'year': ['exact', ]
        }
        interfaces = (relay.Node, )

    movie_age = graphene.String()

    def resolve_movie_age(self, info):
        return "old movie" if self.year < 2000 else "new movie"


class DirectorType(DjangoObjectType):
    class Meta:
        model = Director


class Query(graphene.ObjectType):
    # all_movies = graphene.List(MovieType)
    # Relay con django-filter
    all_movies = DjangoFilterConnectionField(MovieNode)
    # movie = graphene.Field(
    #     MovieType,
    #     id = graphene.Int(),
    #     title = graphene.String()
    # )

    # Relay implementation
    movie = relay.Node.Field(MovieNode)

    # esto es necesario cuando no se implementa Relay
    # def resolve_all_movies(self, info, **kwargs):
    #     user = info.context.user
    #     # This is the same that decorate the resolver with the
    #     # login_required decorator.
    #     if not user.is_authenticated:
    #         raise Exception('Auth credential were not provided')
    #     return Movie.objects.all()

    # def resolve_movie(self, info, **kwargs):
    #     id = kwargs.get("id")
    #     title = kwargs.get("tile")
    #
    #     if id is not None:
    #         return Movie.objects.get(pk=id)
    #
    #     if title is not None:
    #         return Movie.objects.get(title=title)

    all_directors = graphene.List(DirectorType)

    @login_required
    def resolve_all_directors(self, info, **kwargs):
        return Director.objects.all()


class MovieCreateMutation(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        year = graphene.Int(required=True)

    movie = graphene.Field(MovieType)

    # Se puede usar en lugar de title, year los Kwargs
    def mutate(self, info, title, year):
        movie = Movie.objects.create(title=title, year=year)

        return MovieCreateMutation(movie=movie)


class MovieUpdateMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        title = graphene.String()
        year = graphene.Int()

    movie = graphene.Field(MovieType)

    # Se puede usar en lugar de title, year los Kwargs
    def mutate(self, info, id, title, year):
        movie = Movie.objects.get(pk=id)
        if title is not None:
            movie.title = title

        if year is not None:
            movie.year = year

        movie.save()

        return MovieUpdateMutation(movie=movie)


# Relay implementation
class MovieUpdateMutationRelay(relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        title = graphene.String()

    movie = graphene.Field(MovieType)

    @classmethod
    def mutate_and_get_payload(cls, root, info, id, title):
        movie = Movie.objects.get(pk=from_global_id(id)[1])
        if title is not None:
            movie.title = title

        movie.save()

        return MovieUpdateMutationRelay(movie=movie)


class MovieDeleteMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    movie = graphene.Field(MovieType)

    # Se puede usar en lugar de title, year los Kwargs
    def mutate(self, info, id):
        movie = Movie.objects.get(pk=id)
        movie.delete()

        return MovieDeleteMutation(movie=None)


class Mutation:
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()

    create_movie = MovieCreateMutation.Field()
    update_movie = MovieUpdateMutation.Field()
    update_movie_relay = MovieUpdateMutationRelay.Field()
    delete_movie = MovieDeleteMutation.Field()
