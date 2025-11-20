from nnl import parse_nnl, dump_nnl
import json

def test_simple_roundtrip():
    txt = """
    user contains:
      name is Alice.
      age is 30.
      roles are admin, editor.
    """
    obj = parse_nnl(txt)
    assert obj['user']['name'] == 'Alice'
    assert obj['user']['age'] == 30
    assert obj['user']['roles'] == ['admin','editor']
    # round-trip
    out = dump_nnl(obj)
    obj2 = parse_nnl(out)
    assert obj == obj2

def test_array_of_objects_and_matrix():
    txt = """
    project contains:
      title is Atlas.
      items are:
        - contains:
            id is 1.
            tags are alpha, beta.
        - contains:
            id is 2.
            tags are gamma.
      matrix are:
        - 1, 2, 3.
        - 4, 5, 6.
    """
    obj = parse_nnl(txt)
    assert obj['project']['items'][0]['id'] == 1
    assert obj['project']['matrix'][1] == [4,5,6]
    # json conversion
    j = json.dumps(obj)
    assert isinstance(j, str)
