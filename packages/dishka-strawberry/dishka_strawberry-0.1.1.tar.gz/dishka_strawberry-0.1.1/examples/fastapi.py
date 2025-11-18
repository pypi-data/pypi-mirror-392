from typing import NewType

import strawberry
from dishka import Scope, make_async_container, provide
from dishka.integrations.fastapi import FastapiProvider, setup_dishka
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from dishka_strawberry.fastapi import FromDishka, inject

Message = NewType("Message", str)


@strawberry.type(name="Message")
class MessageGQL:
    message: str


@strawberry.type
class Query:
    @strawberry.field
    @inject
    def answer(self, message: FromDishka[Message]) -> MessageGQL:
        return MessageGQL(message=message)


class AppProvider(FastapiProvider):
    @provide(scope=Scope.REQUEST)
    def get_message(self) -> Message:
        return Message("42")


def create_app() -> FastAPI:
    schema = strawberry.Schema(query=Query)
    graphql_router = GraphQLRouter(schema)

    app = FastAPI()
    app.include_router(graphql_router, prefix="/graphql")

    container = make_async_container(AppProvider())
    setup_dishka(container, app)

    return app
