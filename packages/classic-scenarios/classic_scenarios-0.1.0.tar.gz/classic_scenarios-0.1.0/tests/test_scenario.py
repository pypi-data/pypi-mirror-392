from dataclasses import field

from classic.components import component
from classic.scenarios import scenario, Return


@component
class SomeComponent:
    pass


SOME_VALUE = object()


@component
class SomeObj:
    dependency: SomeComponent
    prop: object = field(init=False, default=None)
    complex_prop: list[object] = field(init=False, default_factory=list)

    @scenario
    def run(self):
        self.prop = SOME_VALUE
        self.complex_prop.append(self.prop)
        return self.prop

    @scenario
    def run_and_return(self):
        raise Return(SOME_VALUE)


def test_scenario():
    obj = SomeObj(dependency=SomeComponent())

    assert obj.prop is None

    assert obj.run() == SOME_VALUE
    assert obj.prop is None

    # Сложные объекты из атрибутов сценария, созданные в конструкторе,
    # тоже будут скопированы, поэтому в исходном объекте будут видны изменения.
    # Авторы сценариев должны учитывать это.
    assert obj.complex_prop == [SOME_VALUE]


def test_scenario_returns():
    obj = SomeObj(dependency=SomeComponent())

    assert obj.run_and_return() == SOME_VALUE
