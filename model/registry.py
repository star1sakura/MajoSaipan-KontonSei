"""
通用注册表基础设施
使用装饰器模式实现工厂函数的自动注册，符合开闭原则。
"""
from __future__ import annotations

from typing import Callable, Dict, TypeVar, Generic, Optional
from enum import Enum

T = TypeVar('T', bound=Enum)


class Registry(Generic[T]):
    """
    通用注册表类，支持使用装饰器注册枚举键到工厂函数的映射。

    用法示例:
        enemy_registry = Registry[EnemyKind]("enemy")

        @enemy_registry.register(EnemyKind.FAIRY_SMALL)
        def spawn_fairy_small(state, x, y, hp=5):
            ...
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self._registry: Dict[T, Callable] = {}

    def register(self, key: T) -> Callable[[Callable], Callable]:
        """
        装饰器：将函数注册到指定的枚举键。

        Args:
            key: 枚举类型的键

        Returns:
            装饰器函数

        Raises:
            ValueError: 如果键已被注册
        """
        def decorator(fn: Callable) -> Callable:
            if key in self._registry:
                raise ValueError(
                    f"{self.name} registry: {key} already registered"
                )
            self._registry[key] = fn
            return fn
        return decorator

    def get(self, key: T) -> Optional[Callable]:
        """
        获取注册的工厂函数。

        Args:
            key: 枚举类型的键

        Returns:
            对应的工厂函数，如果未注册则返回 None
        """
        return self._registry.get(key)

    def keys(self) -> list:
        """返回所有已注册的键。"""
        return list(self._registry.keys())

    def __contains__(self, key: T) -> bool:
        """支持 `key in registry` 语法。"""
        return key in self._registry
