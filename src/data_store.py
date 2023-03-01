'''
data_store.py

This contains a definition for a Datastore class which you should use to store your data.
You don't need to understand how it works at this point, just how to use it :)

The data_store variable is global, meaning that so long as you import it into any
python file in src, you can access its contents.

Example usage:

    from data_store import data_store

    store = data_store.get()
    print(store) # Prints { 'names': ['Nick', 'Emily', 'Hayden', 'Rob'] }

    names = store['names']

    names.remove('Rob')
    names.append('Jake')
    names.sort()

    print(store) # Prints { 'names': ['Emily', 'Hayden', 'Jake', 'Nick'] }
    data_store.set(store)
'''
import pickle

## YOU SHOULD MODIFY THIS OBJECT BELOW
initial_object = {
    'users': [],
    'channels': [],
    'dms' : [],
    'standups': [],
    'user_stats': {},
    'workspace_stats': {},
    'notifications': {},
}
## YOU SHOULD MODIFY THIS OBJECT ABOVE

## YOU ARE ALLOWED TO CHANGE THE BELOW IF YOU WISH
class Datastore:
        # def __init__(self):
        #     self.__store = initial_object

        # def get(self):
        #     return self.__store

        # def set(self, store):
        #     if not isinstance(store, dict):
        #         raise TypeError('store must be of type dictionary')
        #     self.__store = store

    def __init__(self):
        # Check and see if there is a datastore file
        # TODO: Check if the file is in the right state
        try:
            self.__store = pickle.load(open("datastore.p", "rb"))
        # If file is not found, generate one
        except FileNotFoundError:
            with open('datastore.p', 'wb') as FILE:
                pickle.dump(initial_object, FILE)
            self.__store = initial_object

    def get(self):
        self.__store = pickle.load(open("datastore.p", "rb"))
        return self.__store
    
    def set(self, store):
        if not isinstance(store, dict):
            raise TypeError(description ='store must be of type dictionary')

        with open('datastore.p', 'wb') as FILE:
            pickle.dump(store, FILE)
        self.__store = store


print('Loading Datastore...')

global data_store
data_store = Datastore()
