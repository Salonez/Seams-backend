channel_details_v1
- It is assumed that owners and all members are listed in ascending id number.

channel_messages_v1
- Assuming that messages are inserted to the front of the list so that the most recent message in any given channel is the first in the list

All Functions that requires token
- An AccessError will be thrown if there is not json payload

dm/create
- Creator is not in u_ids

user_stats
- only care about channels and dms user is currently in

Standup
- The packaged message counts as 1 message for workspace stats and 1 message for the person's stats that started it.