# Commented due to the lack of need for it at the moment. However, it might be useful in the future

# from src.data_store import data_store

# # Test for schema
# def test_data_store_schema():
#     store = data_store.get()

#     # Ensure the object schema is as intended
#     assert 'users' in store
#     assert 'channels' in store
#     assert 'messages' in store

#     if len(store['users']) > 0:
#         assert type(store['users'][0]['user_id']) == int
#         assert type(store['users'][0]['email']) == str
#         assert type(store['users'][0]['password']) == str
#         assert type(store['users'][0]['name_first']) == str
#         assert type(store['users'][0]['name_last']) == str
#         assert type(store['users'][0]['handle_str']) == str

#     if len(store['channels']) > 0:
#         assert type(store['channels'][0]['channel_id']) == int
#         assert type(store['channels'][0]['name']) == str
#         assert type(store['channels'][0]['is_public']) == bool
#         assert type(store['channels'][0]['owner_members_id']) == list
#         assert type(store['channels'][0]['all_members_id']) == list
#         assert type(store['channels'][0]['messages']) == list

#         if len(store['channels'][0]['messages']) > 0:
#             assert type(store['channels'][0]['messages'][0]['message_id']) == int
#             assert type(store['channels'][0]['messages'][0]['message']) == str
#             assert type(store['channels'][0]['messages'][0]['u_id']) == int
#             assert type(store['channels'][0]['messages'][0]['time_sent']) == int
