from typing import Any

from telebot.async_telebot import AsyncTeleBot
from telebot.util import extract_command

from .models import User


class FilterExpression:
    def __init__(self, field: str, value: Any) -> None:
        self._field = field
        self.value = value

    def _get_field_value(self, update: Any, update_type: str) -> Any:
        match self._field:
            case "update_type":
                return update_type
            case "content_type":
                return getattr(update, "content_type", None)
            case "text":
                if update_type != "message":
                    return None
                if getattr(update, "content_type", None) != "text":
                    return None
                return update.text
            case "command":
                if update_type != "message":
                    return None
                if getattr(update, "content_type", None) != "text":
                    return None
                return extract_command(getattr(update, "text", None))
            case "callback_data":
                if update_type != "callback_query":
                    return None
                return getattr(update, "data", None)
            case _:
                return None

    def check(  # type: ignore
        self,
        update: Any,
        update_type: str,
        bot: AsyncTeleBot,
        chat_id: int,
        user: User,
    ) -> dict[str, Any] | bool:
        pass

    def __and__(self, other: Any) -> Any:
        """Implement & operator for combining filters with AND logic"""
        return AndFilter(self, other)

    def __or__(self, other: Any) -> Any:
        """Implement | operator for combining filters with OR logic"""
        return OrFilter(self, other)

    # def __invert__(self):
    #     """Implement ~ operator for NOT logic"""
    #     return NotFilter(self)
    #
    # def __repr__(self):
    #     return f"{self.__class__.__name__}(...)"


class FilterFactory:
    def __getattr__(self, field: Any) -> Any:
        return Filter(field)


F = FilterFactory()


class Filter:
    """The main Magic Filter class that creates filter expressions"""

    def __init__(self, field: str) -> None:
        self._field = field

    def __eq__(self, other: object) -> Any:
        """Create an equality filter"""
        return EqualityFilter(self._field, other)

    # def __ne__(self, other):
    #     """Create a not-equal filter"""
    #     return NotFilter(EqualityFilter(self._field_path, other))
    #
    # def __lt__(self, other):
    #     """Create a less-than filter"""
    #     return LessThanFilter(self._field_path, other)
    #
    # def __gt__(self, other):
    #     """Create a greater-than filter"""
    #     return GreaterThanFilter(self._field_path, other)
    #
    def startswith(self, prefix: str) -> Any:
        """Create a startswith filter"""
        return StartsWithFilter(self._field, prefix)

    #
    # def endswith(self, suffix):
    #     """Create an endswith filter"""
    #     return EndsWithFilter(self._field_path, suffix)
    #
    def in_(self, items: Any) -> Any:
        """Create a contains filter"""
        return InFilter(self._field, items)

    # def matches(self, pattern):
    #     """Create a regex matching filter"""
    #     return RegexFilter(self._field_path, pattern)
    #
    # def __repr__(self):
    #     if self._field_path:
    #         return f"MagicFilter({'.'.join(self._field_path)})"
    #     return "MagicFilter()"


class InFilter(FilterExpression):
    def check(
        self,
        update: Any,
        update_type: str,
        bot: AsyncTeleBot,
        chat_id: int,
        user: User,
    ) -> dict[str, Any] | bool:
        field_value = self._get_field_value(update, update_type)
        return field_value in self.value


class StartsWithFilter(FilterExpression):
    def check(
        self,
        update: Any,
        update_type: str,
        bot: AsyncTeleBot,
        chat_id: int,
        user: User,
    ) -> dict[str, Any] | bool:
        field_value = self._get_field_value(update, update_type)
        if not isinstance(field_value, str):
            return False
        return field_value.startswith(self.value)


class EqualityFilter(FilterExpression):
    def check(
        self,
        update: Any,
        update_type: str,
        bot: AsyncTeleBot,
        chat_id: int,
        user: User,
    ) -> dict[str, Any] | bool:
        field_value = self._get_field_value(update, update_type)
        return field_value == self.value


class OrFilter(FilterExpression):
    """Combines two filters with OR logic"""

    def __init__(self, left: Any, right: Any) -> None:
        self.left = left
        self.right = right

    def check(self, *args: Any, **kwargs: Any) -> bool:
        return self.left.check(*args, **kwargs) or self.right.check(*args, **kwargs)

    def __repr__(self) -> str:
        return f"({self.left} | {self.right})"


class AndFilter(FilterExpression):
    """Combines two filters with OR logic"""

    def __init__(self, left: Any, right: Any) -> None:
        self.left = left
        self.right = right

    def check(self, *args: Any, **kwargs: Any) -> bool:
        return self.left.check(*args, **kwargs) and self.right.check(*args, **kwargs)

    def __repr__(self) -> str:
        return f"({self.left} | {self.right})"
