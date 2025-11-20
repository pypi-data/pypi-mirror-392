





# properties = [
#     {"name" : "integer", "value_type" : Integer(), "default" : 5},
#     {"name" : "minmax", "value_type" : MinMax(3, 8), "default" : 5},
# ]

# def validate():
#     for property in properties:
#         value = None
#         while value is None:
#             response = input("input a " + property["name"])
#             if not response:
#                 value = property["default"]
#                 continue
#             value = property["value_type"].validate(response)
#         print(value)

# validate()