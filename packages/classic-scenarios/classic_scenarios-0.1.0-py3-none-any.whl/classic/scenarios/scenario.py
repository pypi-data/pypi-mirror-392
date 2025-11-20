from functools import wraps
import copy

from .exceptions import Return


def scenario(fn):
    """
    Декоратор для обертывания методов классов,
    обозначающий начало и конец сценария.
    Потокобезопасен. При вызове копирует self, передавая копию дальше по стеку,
    чтобы изолировать выполнение сценария в разных потоках,
    и предоставить объект из self в исходном, неизмененном состоянии.
    Это может привести к неожиданным результатам,
    если в полях объекта-владельца есть сложные объекты, вроде списков,
    созданные в конструкторе!

    Пример:
    >>> from classic.scenarios import scenario
    ... class SomeObj:
    ...     @scenario
    ...     def run(self):
    ...         self._do_something()
    ...         self._do_something_yet()
    ...
    ...     def _do_something(self):
    ...         'Первый шаг в сценариий'
    ...
    ...     def _do_something_yet(self):
    ...         'Второй шаг в сценарии'
    """

    @wraps(fn)
    def wrapper(self, **kwargs):
        try:
            new_self = copy.copy(self)
            for k, v in kwargs.items():
                setattr(new_self, k, v)
            return fn(new_self)
        except Return as exc:
            return exc.result

    return wrapper
