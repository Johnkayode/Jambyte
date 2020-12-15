import os
from faunadb import query as q
from faunadb.objects import Ref
from faunadb.client import FaunaClient

def get_client():
    client = FaunaClient(secret=os.environ.get('fauna'))

    return client