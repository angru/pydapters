from pydapters import Adapter, NestedField, preprocess, postprocess, Field


class Ad(Adapter):
    @preprocess
    def prepare(self, data: dict, **kwargs):
        data['z'] = {}

        return data

    @postprocess
    def postpare(self, data: dict, **kwargs):
        data['z']['x'] = 'y'

        return data

    @postprocess
    def postpare_2(self, data: dict, **kwargs):
        data['g'] = 2

        return data


class SimpleAdapter(Adapter):
    a = NestedField(Ad)


def test_many():
    class A1(Adapter):
        @preprocess(many=True)
        def insert_before(self, data, **kwargs):
            data.append(1)

            return data

        @postprocess(many=True)
        def insert_after(self, data, **kwargs):
            data.append(2)

            return data

    assert A1().adapt([], many=True) == [1, 2]


def test_simple():
    s = SimpleAdapter()
    r = s.adapt({'a': {'b': 'c'}})

    assert r == {'a': {'b': 'c', 'z': {'x': 'y'}, 'g': 2}}


def test_field():
    class Address(Adapter):
        street = Field(destination='st.')
        number = Field(origin='nb.')

    assert Address().adapt({
        'street': 'First',
        'nb.': 1,
    }) == {
        'st.': 'First',
        'number': 1,
    }
