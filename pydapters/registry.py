_registry = {}


def add(adapter: type):
    name = adapter.__name__

    assert name not in _registry, f'Adapter with such name already exists {_registry[name]}'

    _registry[name] = adapter


def get(name: str):
    assert name in _registry

    return _registry[name]
