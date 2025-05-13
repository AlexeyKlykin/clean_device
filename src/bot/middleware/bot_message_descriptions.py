class MessageDescription:
    def __init__(self, message_input) -> None: ...


# md = MessageDescription("/add")
# md.description() - """/add_type - это /add_company - это"""

# button_start = [
#     [
#         KeyboardButton(text="/add"),
#         KeyboardButton(text="/get"),
#     ],
# ]
#
# button_add = [
#     [KeyboardButton(text="/add_stock_device"), KeyboardButton(text="/add_device")],
#     [
#         KeyboardButton(text="/add_device_type"),
#         KeyboardButton(text="/add_device_company"),
#     ],
#     [
#         KeyboardButton(text="/replacement_lamp"),
#         KeyboardButton(text="/cancel"),
#     ],
# ]
#
# button_get = [
#     [
#         KeyboardButton(text="/get_stock_device"),
#         KeyboardButton(text="/get_broken_device"),
#     ],
#     [
#         KeyboardButton(text="/get_devices"),
#         KeyboardButton(text="/get_companies"),
#         KeyboardButton(text="/get_types"),
#     ],
#     [KeyboardButton(text="/mark_device"), KeyboardButton(text="/stock_device_at_date")],
#     [
#         KeyboardButton(text="/check_lamp_hours"),
#         KeyboardButton(text="/cancel"),
#     ],
# ]
start = """<i>Бот поможет добавлять данные о чистых приборах со склада</i>
<i>/add - открывает меню с функционалом для добавления приборов и вспомогательной информации о приборах</i>
<i>/get - открывает меню с функционалом для показа различной информации о приборах и возможностью поместить тот или иной прибор в ремонт</i>"""
add = """<i>Вы в меню добавления информации о приборах</i>
<i>/add_stock_device - дает возможность добавить прибор на склад после ввода id и названия прибора.</i>
<i>/add_device - дает возможность добавить прибор в базу после ввода названия, выбора типа и компании производителя</i>
<i>/add_device_type - дает возможность добавить информацию о типе прибора после ввода названия и описания типа</i>
<i>/add_device_company - дает возможность добавить информацию о компании производителе после ввода названия, страны, и сайта</i>
<i>/replacement_lamp - дает возможность заменить лампу на приборе. Для этого нажмите кнопку, выберите id и название прибора, и введите максимальное количество часов работы лампы</i>"""
get = """"""
button_description = {"/start": start, "/add": add, "get": get}
