from pydapters import Adapter, NestedField, preprocess, postprocess


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


def test_simple():
    s = SimpleAdapter()
    r = s.adapt({'a': {'b': 'c'}})

    assert r == {'a': {'b': 'c', 'z': {'x': 'y'}, 'g': 2}}
