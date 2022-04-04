from json import JSONDecodeError

import graphene
from graphql import GraphQLError


class JSONString(graphene.JSONString):
    @staticmethod
    def parse_literal(node):
        try:
            print(node)
            return graphene.JSONString.parse_literal(node)
        except JSONDecodeError as e:
            print(e)
            raise GraphQLError(f"{str(node.value)[:20]}... is not a valid JSONString")


class PositiveDecimal(graphene.Decimal):
    """Positive Decimal scalar implementation.

    Should be used in places where value must be positive.
    """

    @staticmethod
    def parse_value(value):
        value = super(PositiveDecimal, PositiveDecimal).parse_value(value)
        if value and value < 0:
            raise GraphQLError(
                f"Value cannot be lower than 0. Unsupported value: {value}"
            )
        return value


class GeoInput(graphene.InputObjectType):
    lat = JSONString(required=True)
    lng = PositiveDecimal(required=True)

    @property
    def latlng(self):
        return f"({self.lat},{self.lng})"


class Address(graphene.ObjectType):
    latlng = graphene.String()


class Query(graphene.ObjectType):
    address = graphene.Field(Address, geo=GeoInput(required=True))

    def resolve_address(root, info, geo):
        return Address(latlng=geo.latlng)


class CreateAddress(graphene.Mutation):
    class Arguments:
        geo = GeoInput(required=True)

    Output = Address

    def mutate(root, info, geo):
        return Address(latlng=geo.latlng)


class Mutation(graphene.ObjectType):
    create_address = CreateAddress.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
mutation = """
    mutation addAddress{
      createAddress(geo: {lat: "[1,2,3,4]", lng:12}) {
        latlng
      }
    }
"""

if __name__ == "__main__":
    result = schema.execute(mutation)
    print(result)