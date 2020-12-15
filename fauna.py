from faunadb import query as q
from faunadb.objects import Ref
from faunadb.client import FaunaClient

def get_client():
    client = FaunaClient(secret="fnAD89XSsYACAZQjKdEkNolUekVOQW7YGYA2KNLl")

    return client