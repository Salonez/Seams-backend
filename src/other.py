from src.data_store import data_store
from src.error import AccessError, InputError

def clear_v1():
    store = data_store.get()
    store['users'] = []
    store['channels'] = []
    store['dms'] = []
    store['standups'] = []
    store['user_stats'] = {}
    store['workspace_stats'] = {}
    store['notifications'] = {}
    data_store.set(store)
    return {}
