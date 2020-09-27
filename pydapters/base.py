import copy
import functools
import inspect
import typing as t

from pydapters import registry


def preprocess(f=None):
    """Декоратор для методов-препроцессоров адаптера, будет вызван перед методом adapt,
        используется для предварительной обработки данных, переданых в адаптер.
        Можно обьявлять произвольное колличество препроцессоров, главное, чтобы они отличались по названию
    """
    def decorator(func):
        @functools.wraps(func)
        def wrap(ff):
            ff.__preprocessor__ = True

            return ff

        return wrap(func)

    if f is not None:
        return decorator(f)
    else:
        return decorator


def postprocess(f=None):
    """Декоратор для методов-постпроцессоров адаптера, будет вызван после метода adapt,
        используется для пост-обработки данных, возвращенных методом adapt.
        Можно обьявлять произвольное колличество постпроцессоров, главное, чтобы они отличались по названию

    """
    def decorator(func):
        @functools.wraps(func)
        def wrap(ff):
            ff.__postprocessor__ = True

            return ff

        return wrap(func)

    if f is not None:
        return decorator(f)
    else:
        return decorator


class Field:
    """Базовый класс поля адаптера, управляющий логикой обработки одного аттрибута данных,
        переданных в метод adapt адаптера"""
    _name: str = None

    many: bool = False

    def __init__(self, destination: str = None, origin: str = None):
        """
        :param destination: аттибут или ключ выходных данных, в который попадет значение, возвращаемое этим полем
        :param origin: аттрибут или ключ, по которому  из входных данных адаптера будет взято значение для обработки
            этого поля.
        """
        self.destination = destination
        self.origin = origin

    def apply(self, data, **kwargs):
        return data

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        assert self._name is None, (
            'Field instance already have name. You probably try to assign one field instance to multiple adapters'
        )

        self._name = value


class NestedField(Field):
    __parent_adapter__: t.Any

    def __init__(
        self,
        adapter: t.Union[t.Type['Adapter'], 'Adapter', str],
        many=False,
        destination: str = None,
        origin: str = None,
        **adapter_params,
    ):
        super().__init__(destination=destination, origin=origin)

        self.many = many

        if callable(adapter):
            self._adapter = adapter(**adapter_params)
        else:
            self._adapter = adapter

        self._adapter_params = adapter_params

    @property
    def adapter(self):
        if isinstance(self._adapter, str):
            adapter_name = self._adapter

            if adapter_name in (self.__parent_adapter__.__name__, 'self'):
                self._adapter = self.__parent_adapter__(**self._adapter_params)
            else:
                adapter = registry.get(adapter_name)
                self._adapter = adapter(**self._adapter_params)

        return self._adapter

    def apply(self, data: dict, **kwargs):
        item = data.pop(self.origin, None)

        if item is not None:
            data[self.destination] = self.adapter.adapt(
                item,
                many=self.many,
                **kwargs,
            )

        return data


def wrap_adapt(adapt, preprocessors: list, postprocessors: list):
    """Декоратор, оборачивающий матод adapt класса Adapter, таким образом чтобы сначала выполнялись превпроцессоры,
    определенные на этом адаптере потом сам метод adapt, а затем постпроцессоры"""

    if hasattr(adapt, '__base_info__'):
        adapt, base_preprocessors, base_postprocessors = adapt.__base_info__
        preprocessors = [*preprocessors, *base_preprocessors]
        postprocessors = [*postprocessors, *base_postprocessors]

    @functools.wraps(adapt)
    def wrapper(self, data, **kwargs):
        for preprocessor in preprocessors:
            data = preprocessor(self, data, **kwargs)

        data = adapt(self, data, **kwargs)

        for postprocessor in postprocessors:
            data = postprocessor(self, data, **kwargs)

        return data

    wrapper.__base_info__ = (adapt, preprocessors, postprocessors)

    return wrapper


class AdapterMeta(type):
    """Мета-класс для всех адаптеров, устанавливает правила обработки полей(Field), препроцессоров, постпроцессоров,
    определенных на классе адаптера"""
    def __new__(mcs, name, bases, attrs):
        fields = {}
        preprocessors = []
        postprocessors = []

        for base in bases:
            for attr_name, attr_value in inspect.getmembers(base):
                if isinstance(attr_value, Field):
                    fields[attr_name] = attr_value
                elif not issubclass(base, Adapter) and callable(attr_value):
                    if getattr(attr_value, '__preprocessor__', False):
                        preprocessors.append(attr_value)
                    elif getattr(attr_value, '__postprocessor__', False):
                        postprocessors.append(attr_value)

        for attr_name, attr_value in attrs.items():
            if inspect.isclass(attr_value) and issubclass(attr_value, Field):
                attr_value = attr_value()

            if isinstance(attr_value, Field):
                fields[attr_name] = attr_value

                attr_value.name = attr_name

                if attr_value.destination is None:
                    attr_value.destination = attr_name

                if attr_value.origin is None:
                    attr_value.origin = attr_name
            elif callable(attr_value):
                if getattr(attr_value, '__preprocessor__', False):
                    preprocessors.append(attr_value)
                elif getattr(attr_value, '__postprocessor__', False):
                    postprocessors.append(attr_value)

        klass = super().__new__(mcs, name, bases, attrs)

        registry.add(klass)

        klass.adapt = wrap_adapt(klass.adapt, preprocessors, postprocessors)

        for field in fields.values():
            if hasattr(field, '__parent_adapter__'):
                field = copy.deepcopy(field)

            field.__parent_adapter__ = klass

        klass._fields = list(fields.values())
        klass._preprocessors = preprocessors
        klass._postprocessors = postprocessors

        return klass


class Adapter(metaclass=AdapterMeta):
    """Базовый класс адаптера. Наследники должны реализовывать метод adapt"""
    def adapt(self, data: t.Any, many=False, **kwargs) -> t.Any:
        """Метод, управляющий процессом преобразования данных

        :param data: данные, которые должны быть преобразованы
        :return: преобразованные данные
        """
        if many:
            data = [self._adapt(item, **kwargs) for item in data]
        else:
            data = self._adapt(data, **kwargs)

        return data

    def _adapt(self, data: t.Any, **kwargs) -> t.Any:
        for field in self.fields:
            data = field.apply(data, **kwargs)

        return data

    @property
    def fields(self) -> t.List['Field']:
        """Список полей адаптера"""
        return self._fields
