import inspect
from collections.abc import Awaitable, Callable
from typing import Any, ParamSpec, TypeVar


P = ParamSpec("P")
R = TypeVar("R")


class StateGroup:
    def __init__(self) -> None:
        self.state_classes: list[type[State]] = []

    def register(self, state_class: type["State"]) -> None:
        """
        Register a state class in the group.
        """
        if not issubclass(state_class, State):
            exc_txt = f"{state_class.__name__} is not a subclass of State."
            raise TypeError(exc_txt)
        self.state_classes.append(state_class)


class State:
    def __init__(self) -> None:
        # MyCoroutineType = Callable[[int, str], Awaitable[bool]]
        # TODO replace many args with a single object
        self.handlers: list[Awaitable[Any]] = self._get_handlers()

    def _get_handlers(self) -> list[Awaitable[Any]]:
        handlers = []
        for _method_name, method in sorted(
            inspect.getmembers(self.__class__, predicate=lambda x: getattr(x, "is_handler", False)),
            key=lambda x: x[1].order_id,
        ):
            handlers.append(method)
        return handlers


class StateHandlerDec:
    order_id = 0

    # def __init__(self, filters: list[Filter] | None = None) -> None:
    #     self.filters = filters or []
    def __init__(self, filter_: Any = None) -> None:
        self.filter = filter_

    def __call__(self, func: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            return await func(*args, **kwargs)

        wrapper.is_handler = True  # type: ignore
        wrapper.filter = self.filter  # type: ignore
        wrapper.order_id = StateHandlerDec.order_id  # type: ignore
        StateHandlerDec.order_id += 1
        return wrapper


handler = StateHandlerDec
