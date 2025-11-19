import logging
import traceback
from collections.abc import Awaitable
from itertools import chain
from typing import Any

from telebot.async_telebot import AsyncTeleBot

from .db_service import UserDBService
from .models import User
from .state import State, StateGroup
from .utils import get_chat, get_from_user


logger = logging.getLogger(__name__)

# TODO: refine type hints


class PRTeleBotClient(AsyncTeleBot):
    def __init__(self, db_service: UserDBService, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.db_service = db_service

        self.states: dict[str, State] = {}
        self._global_handlers: list[Awaitable[Any]] = []

    def register_state(self, state_class: type[State]) -> None:
        """
        Register a state class and its handlers.
        """
        # self._handler_order_id = 0  # Reset order_id for each new state class
        if getattr(state_class, "is_global", False):
            self._global_handlers += state_class().handlers
        else:
            self.states[state_class.__name__] = state_class()

    def include(self, state_group: StateGroup) -> None:
        """
        Include a state group and register all its states.
        """
        for state_class in state_group.state_classes:
            self.register_state(state_class)

    async def _run_middlewares_and_handlers(
        self, message: Any, handlers: Any, middlewares: Any, update_type: str
    ) -> None:
        from_user = get_from_user(message)
        chat_id = get_chat(message).id

        user = await self.db_service.get_user(from_user.id)
        if not user:
            user = await self.db_service.create_user(User.model_validate(from_user))

        data = {}  # type: ignore
        state = self.states.get(user.state)
        state_handlers = state.handlers if state else ()

        for handler in chain(self._global_handlers, state_handlers):  # type: ignore
            filter_checked = False

            if handler.filter:  # type: ignore
                filter_checked = handler.filter.check(message, update_type, self, chat_id, user)  # type: ignore

            if not filter_checked:
                continue

            try:
                await handler(self, chat_id, message, user, data)  # type: ignore
            except Exception as e:
                logger.error("Error in handler %s: %s\n\n%s", handler, e, traceback.format_exc())
                # TODO add send error msg if feature enabled
            break
