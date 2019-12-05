import graphene
import graphql_jwt

import website.links.schema as LinkSchema
import website.users.schema as UserSchema


class Query(LinkSchema.Query, UserSchema.Query, graphene.ObjectType):
    pass


class Mutation(LinkSchema.Mutation, UserSchema.Mutation, graphene.ObjectType):
    token_auth    = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token  = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
