from __future__ import annotations

from typing import Dict, Type, TypeVar, Optional


T = TypeVar("T")


class Actor:
    """
    一个“游戏对象”，只是一个组件容器：
    - add(component)
    - get(ComponentType)
    """

    def __init__(self) -> None:
        self._components: Dict[Type, object] = {}

    def add(self, component: object) -> None:
        self._components[type(component)] = component

    def get(self, comp_type: Type[T]) -> Optional[T]:
        return self._components.get(comp_type)  # type: ignore[return-value]

    def has(self, comp_type: Type) -> bool:
        return comp_type in self._components
