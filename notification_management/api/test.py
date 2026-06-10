result = {
   "update_id": 553493979,
   "callback_query": {
     "id": "4860094626454253283",
     "from": {
       "id": 1131578960,
       "is_bot": False,
       "first_name": "\u0645\u0631\u0648\u0627\u0646",
       "username": "Marwan408",
       "language_code": "ar"
     },
     "message": {
       "message_id": 115,
       "from": {
         "id": 8758948322,
         "is_bot": True,
         "first_name": "Frappe Bot",
         "username": "marwan_frappe_bot"
       },
       "chat": {
         "id": 1131578960,
         "first_name": "\u0645\u0631\u0648\u0627\u0646",
         "username": "Marwan408",
         "type": "private"
       },
       "date": 1781019852,
       "text": "after insert\n\ndocname : ACC-SINV-2026-00010\nuser : Administrator\ncurrentdate : 2026-06-09",
       "reply_markup": {
         "inline_keyboard": [
           [
             {
               "text": "Submit",
               "callback_data": "submit:Sales Invoice:ACC-SINV-2026-00010"
             },
             {
               "text": "Cancel",
               "callback_data": "cancel:Sales Invoice:ACC-SINV-2026-00010"
             }
           ]
         ]
       }
     },
     "chat_instance": "31227151496650532",
     "data": "submit:Sales Invoice:ACC-SINV-2026-00010"
   }
 }

data = result.get("callback_query").get("data")
sep_data = data.split(":")
# print(sep_data[1])

chat_id = result.get("callback_query").get("message").get("chat_id")

my_dict = {
    "name":'marwan',
    "prop": {
        "tall":23,
        "weight":59
    }
}
print(result.get("callback_query").get("message").get("chat").get("id"))