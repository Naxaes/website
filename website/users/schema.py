from django.contrib.auth import get_user_model

import graphene
from graphene_django import DjangoObjectType


User = get_user_model()


class UserType(DjangoObjectType):
    class Meta:
        model = User


class Query(graphene.ObjectType):
    me    = graphene.Field(UserType)
    users = graphene.List(UserType)

    def resolve_me(self, info, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Not logged in!')

        return user

    def resolve_users(self, info, **kwargs):
        return User.objects.all()


class CreateUser(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        email    = graphene.String(required=True)

    def mutate(self, info, username, password, email):
        user = User(
            username=username,
            email=email,
        )
        user.set_password(password)
        user.save()

        return CreateUser(user=user)


class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
