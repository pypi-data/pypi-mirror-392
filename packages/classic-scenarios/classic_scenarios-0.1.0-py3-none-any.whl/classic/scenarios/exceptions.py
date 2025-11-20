

class Return(Exception):
    """
    Исключение, нужное для остановки сценария и возврата результата.
    Декоратор scenario ожидает исключения этого типа,
    и возвращает наружу содержимое исключения.
    Пример:

    >>> from classic.scenarios import scenario
    ... class SomeCls:
    ...     @scenario
    ...     def run(self):
    ...         raise Return('SomeValue')
    ...
    ... assert SomeCls().run() == 'SomeValue'
    """

    def __init__(self, result: object):
        self.result = result
