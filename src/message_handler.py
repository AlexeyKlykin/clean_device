from src.scheme_for_validation import StockBrokenDeviceData, StockDeviceData


class MessageDescription:
    def __init__(self, message_input: str | None) -> None:
        self.message_input = message_input

    @property
    def message_data(self):
        return self._message_data

    @message_data.setter
    def message_data(self, value):
        self._message_data = value

    def description(self) -> str:
        match self.message_input:
            case "add_lamp_type":
                if self._message_data:
                    return BUTTON_DESCRIPTION["add_lamp_type"].format(
                        lamp_type=self.message_data
                    )
                else:
                    return "Ошибка передачи данных о типе устройства"

            case "add_device_company":
                if self._message_data:
                    return BUTTON_DESCRIPTION["add_device_company"].format(
                        device_company=self.message_data
                    )
                else:
                    return "Ошибка в передаче данных о компании"

            case "type_for_device":
                if self._message_data:
                    return BUTTON_DESCRIPTION["type_for_device"].format(
                        type_for_device=self.message_data
                    )
                else:
                    return "Ошибка в передаче данных о приборе"

            case "update":
                if self._message_data:
                    return BUTTON_DESCRIPTION["update"].format(
                        update_data=self.message_data
                    )
                else:
                    return "Ошибка при обновлении данных прибора на складе"

            case "LED":
                if self._message_data:
                    return BUTTON_DESCRIPTION["LED"].format(lamp_led=self.message_data)
                else:
                    return "Ошибка добавления данных о приборе на складе c лампой led"

            case "FIL":
                if self.message_data:
                    return BUTTON_DESCRIPTION["FIL"].format(lamp_fil=self.message_data)
                else:
                    return "Ошибка передачи данных о приборе со складе с лампой накаливания"

            case "lamp_error":
                if isinstance(self._message_data, tuple):
                    return BUTTON_DESCRIPTION["lamp_error"].format(
                        lamp_error=self.message_data[0],
                        stock_device_data=self.message_data[1],
                    )

                else:
                    return "Ошибка передачи данных прибора"

            case "add_lamp_hours_from_stock_device":
                if self._message_data:
                    return BUTTON_DESCRIPTION[
                        "add_lamp_hours_from_stock_device"
                    ].format(lamp_hours=self.message_data)
                else:
                    return "Ошибка передачи данных о ресурсе лампы"

            case "max_lamp_hours":
                if self._message_data:
                    return BUTTON_DESCRIPTION["max_lamp_hours"].format(
                        max_hours=self.message_data
                    )

                else:
                    return "Ошибка передачи данных о максимальном ресурсе лампы"

            case "check_lamp_hours":
                if self._message_data:
                    return BUTTON_DESCRIPTION["check_lamp_hours"].format(
                        lamp_hours=self.message_data
                    )

                else:
                    return "Ошибка подсчета ресурса лампы"

            case "get_stock_device_at_date":
                if isinstance(self._message_data, list):
                    return "\n\n".join(
                        [
                            f"""<i>Id прибора</i>: <code>{item.stock_device_id}</code>
<i>Название прибора</i>: <code>{item.device_name}</code>
<i>Дата очистки</i>: <code>{item.at_clean_date}</code>"""
                            for item in self.message_data
                            if isinstance(item, StockBrokenDeviceData)
                        ]
                    )

                else:
                    return self.message_data

            case "get_broken_device":
                if isinstance(self._message_data, list):
                    return "\n\n".join(
                        [
                            f"""<i>ID прибора</i>: <code>{item.stock_device_id}</code>
<i>Название прибора</i>: <code>{item.device_name}</code>
<i>Дата очистки</i>: <code>{item.at_clean_date}</code>"""
                            for item in self.message_data
                            if isinstance(item, StockBrokenDeviceData)
                        ]
                    )
                else:
                    return f"Данные о приборе не найдены {self.message_data}"

            case "show_the_devices_found":
                if isinstance(self._message_data, StockDeviceData):
                    return f"""<i>Id прибора</i>: <code>{self.message_data.stock_device_id}</code>
<i>Название прибора</i>: <code>{self.message_data.device_name}</code>
<i>Компания производитель прибора</i>: <code>{self.message_data.company_name}</code>
<i>Тип прибора</i>: <code>{self.message_data.type_title}</code>
<i>Дата последней очистки</i>: <code>{self.message_data.at_clean_date}</code>\n"""
                else:
                    return "Данные о приборе по ID не найдены"

            case str(message):
                return BUTTON_DESCRIPTION[message]

            case _:
                return "<b>Переданное сообщение не известно</b>"


start = """<i>Бот поможет добавлять данные о чистых приборах со склада</i>
<b>/add</b> - <i>открывает меню с функционалом для добавления приборов и вспомогательной информации о приборах</i>
<b>/get</b> - <i>открывает меню с функционалом для вывода на экран различной информации о приборах и возможностью поместить тот или иной прибор в ремонт</i>"""

add = """<i>Вы в меню добавления информации о приборах</i>
<b>/add_stock_device</b> - <i>дает возможность добавить прибор на склад после ввода id и названия прибора.</i>
<b>/add_device</b> - <i>дает возможность добавить прибор в базу после ввода названия, выбора типа и компании производителя</i>
<b>/add_device_type</b> - <i>дает возможность добавить информацию о типе прибора после ввода названия и описания типа</i>
<b>/add_device_company</b> - <i>дает возможность добавить информацию о компании производителе после ввода названия, страны, и сайта</i>
<b>/replacement_lamp</b> - <i>дает возможность заменить лампу на приборе. Для этого нажмите кнопку, выберите id и название прибора, и введите максимальное количество часов работы лампы</i>"""

get = """<i>Вы в меню отображения информации о приборах</i>
<b>/get_stock_device</b> - <i>вывести на экран приборы со склада по id</i>
<b>/get_broken_device</b> - <i>вывести на экран приборы в ремонте за определенную дату</i>
<b>/get_devices</b> - <i>вывести на экран список приборов</i>
<b>/get_companies</b> - <i>вывести на экран список компаний производителей</i>
<b>/get_types</b> - <i>вывести на экран все типы приборов</i>
<b>/mark_device</b> - <i>поместить прибор в ремонт или вывести из ремонта</i>
<b>/stock_device_at_date</b> - <i>вывести на экран почищенные приборы за определенную дату</i>
<b>/check_lamp_hours</b> - <i>посмотреть оставшийся ресурс работы лампы</i>
<b>/cancel</b> - <i>выход и очистка памяти</i>"""

# get list components
get_devices = """<i>Вы в меню вывода на экран списка приборов доступных в базе</i>"""
get_companies = """<i>Вы в меню вывод на экран списка компаний производителей</i>"""
get_types = """<i>Вы в меню вывода на экран списка типов приборов</i>"""
cancel = """<i>Выход/Очистка</i>"""

# add device type
add_type_title = """<i>Вы в меню добавления типа прибора в базу. Следуйте инструкциям на экране.</i> <b>Введите название типа прибора</b>"""
add_description_type = "<i>Введите описание типа прибора</i>"
add_device_type = "<i>Выберите тип лампы</i>"
add_lamp_type = "<b>{lamp_type}</b>"

# add device company
add_device_company_name = """<i>Вы в меню добавления компании в базу данных. Следуйте инструкциям на экране.</i> <b>Введите название компании производителя</b>"""
add_producer_country = "<i>Введите название страны производителя</i>"
add_description_company = "<i>Введите описание или адрес сайта</i>"
add_device_company = "<b>{device_company}</b>"

# add device
add_device = """<i>Вы в меню добавления прибора в базу. Следуйте инструкциям на экране.</i> <b>Введите название прибора</b>"""
device_name = "<i>Введите компанию производитель прибора</i>"
company_for_device = "<i>Выберите тип прибора</i>"
type_for_device = "<code>{type_for_device}</code>"

# add stock device
add_stock_device = """<i>Вы в меню добавления или добавления чистого прибора на склад(е). Следуйте инструкциям на экране.</i> <b>Введите ID прибора на складе</b>"""
add_device_id_for_stock_device = "<i>Введите название прибора</i>"
device_stock_update = "Данные обновленны <b>{update_data}</b>"
device_stock_lamp_led = "Данные добавленны <code>{lamp_led}</code>"
device_stock_lamp_fil = "<b>У прибора лампа накаливания. {lamp_fil} Введите максимальное колличество часов</b>"
device_stock_lamp_error = (
    "В базе отсутствет запись {lamp_error} <code>{stock_device_data}</code>"
)
add_lamp_hours_from_stock_device = "Данные добавленны <code>{lamp_hours}</code>"

# replacement_lamp
replacement_lamp = """<i>Вы в меню замены лампы. Следуйте инструкциям на экране.</i> <b>Введите ID прибора на складе для которого нужно заменить лампу</b>"""
stock_device_id_from_lamp = "<b>Выберите имя прибора</b>"
device_name_from_lamp = "<b>Введите числовой ресурс лампы</b>"
max_lamp_hours = "<b>{max_hours}</b>"

# check lamp
start_check_lamp_hours = (
    """<i>Вы в меню расчета ресурса лампы.</i> <b>Введите ID прибора</b>"""
)
check_device_name = "<b>Выберите название прибора</b>"
check_device_FIL = "<b>Введите текущее количество часов на приборе</b>"
check_lamp_hours = "<i>Результат проверки:</i> <b>{lamp_hours}</b>"

# get stock device at date
start_get_stock_device_at_date = """<i>Вы в меню вывода на экран информации о приборах за определенную дату</i> <b>Введите дату в формате d-m-yyyy, чтобы вывести все устройства за эту дату или 0 чтобы вывести приборы за текущую дату</b>"""

# get broken device
start_get_broken_device = """<i>Вы в меню вывода на экран приборов в ремонте за определенную дату. Следуйте инструкциям на экране</i> <i>Введите дату а формате</i> <b>d-m-yyyy</b>. <i>Или введите</i> <code>0</code> <i>чтобы вывести приборы за текущую дату</i>"""

# mark device
mark_device = """<i>Вы можете поместить прибор в ремонт или вывести из ремонта. Следуйте инструкциям на экране</i> <b>Введите ID прибора</b>"""
mark_for_stock_device_id = "<i>Если вы хотите пометить прибор для ремонта введите</i> <b>0</b>. <i>Если он отремонтирован то</i> <b>1</b>"
mark_for_stock_device = "<i>Выберите прибор</i>"
mark_device_0 = "<b>Прибор помещен в ремонт</b>"
mark_device_1 = "<b>Прибор выведен из ремонта</b>"

# get stock device by id
get_stock_device = """<i>Вы в меню вывода на экран приборов на складе по ID. Следуйте инструкциям на экране</i>"""
choice_stock_device_name = "<i>Выберите прибор</i>"

BUTTON_DESCRIPTION = {
    # get stock device by id
    "/get_stock_device": get_stock_device,
    "choice_stock_device_name": choice_stock_device_name,
    # mark broken or not broken
    "/mark_device": mark_device,
    "mark_for_stock_device_id": mark_for_stock_device_id,
    "mark_for_stock_device": mark_for_stock_device,
    "0": mark_device_0,
    "1": mark_device_1,
    # get broken device
    "/get_broken_device": start_get_broken_device,
    # get_stock_device_handler
    "/stock_device_at_date": start_get_stock_device_at_date,
    # replacement_lamp
    "/replacement_lamp": replacement_lamp,
    "stock_device_id_from_lamp": stock_device_id_from_lamp,
    "device_name_from_lamp": device_name_from_lamp,
    "max_lamp_hours": max_lamp_hours,
    # check lamp
    "/check_lamp_hours": start_check_lamp_hours,
    "check_device_name": check_device_name,
    "check_device_FIL": check_device_FIL,
    "check_lamp_hours": check_lamp_hours,
    # add stock device
    "/add_stock_device": add_stock_device,
    "add_device_id_for_stock_device": add_device_id_for_stock_device,
    "update": device_stock_update,
    "LED": device_stock_lamp_led,
    "FIL": device_stock_lamp_fil,
    "lamp_error": device_stock_lamp_error,
    "add_lamp_hours_from_stock_device": add_lamp_hours_from_stock_device,
    # add_device_type
    "/add_device_type": add_type_title,
    "add_description_type": add_description_type,
    "add_device_type": add_device_type,
    "add_lamp_type": add_lamp_type,
    # add companys
    "/add_device_company": add_device_company_name,
    "add_producer_country": add_producer_country,
    "add_description_company": add_description_company,
    "add_device_company": add_device_company,
    # add device
    "/add_device": add_device,
    "device_name": device_name,
    "company_for_device": company_for_device,
    "type_for_device": type_for_device,
    # get
    "/get_devices": get_devices,
    "/get_types": get_types,
    "/get_companies": get_companies,
    "/start": start,
    "/add": add,
    "/get": get,
    "/cancel": cancel,
}
