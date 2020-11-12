# pydapters

_Data transformation library_


[![build](https://github.com/angru/pydapters/workflows/build/badge.svg)](https://github.com/angru/pydapters/actions?query=workflow%3Abuild+branch%3Amaster++)
[![codecov](https://codecov.io/gh/angru/pydapters/branch/master/graph/badge.svg)](https://codecov.io/gh/angru/pydapters)


## Simple example

```python
from pydapters import Adapter, Field, preprocess, postprocess

class Address(Adapter):
    @preprocess
    def change_street(self, data: dict, **kwargs):
        data['street'] = 'Second'

        return data

    @postprocess
    def chnage_number(self, data: dict, **kwargs):
        data['number'] = 2

        return data

    street = Field(destination='st.')
    number = Field(origin='nb.')

assert Address().adapt({'street': 'First', 'nb.': 1}) == {
    'st.': 'Second', 'number': 2,
}
```
