from src.other import clear_v1
from src.data_store import data_store

# Test clearing internal data
def test_clear_v1():
    clear_v1()
    store = data_store.get()
    assert len(store['users']) == 0
    assert len(store['channels']) == 0
    assert len(store['dms']) == 0


def test_clear_v1_output_type():
    # Test and see if the response variables have the appropriate types
    output = clear_v1()

    # Check if its an dictionary
    assert isinstance(output, dict)

    # Check if the dictionary is empty
    assert not bool(output)
