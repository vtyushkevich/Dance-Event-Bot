# Callback data
(
    START,
    ARCHIVE,
    START_OVER,
    MANAGEMENT,
    GO_BACK,
    CALENDAR,
) = (
    'START',
    'ARCHIVE',
    'START_OVER',
    'MANAGEMENT',
    'GO_BACK',
    'CALENDAR',
)

# Stages
TOP_LEVEL, CREATE_EVENT, CREATE_DATE, CREATE_PROPERTY, CREATE_PHOTO = range(5)

# Filters
(
    PROPERTY_TO_EDIT,
    EDIT_NAME,
    EDIT_CITY,
    EDIT_DESC,
    EDIT_DATE_START,
    EDIT_DATE_END,
    EDIT_COUNTRY,
    EDIT_PHOTO,
    EDIT_PREVIEW,
    PUBLISH_EVENT,
    DELETE_EVENT,
    DELETE_CONFIRMED,
    CALLBACK_QUERY,
    SELECT_ALM,
    SELECT_EVENT,
    BACK_LIST,
    FORWARD_LIST,
    CURRENT_EVENT_ID,
    DATE_COUNTER,
    PAGE_SLICE,
    START_PAGE,
    END_PAGE,
) = (
    'PROPERTY_TO_EDIT',
    'EDIT_NAME',
    'EDIT_CITY',
    'EDIT_DESC',
    'EDIT_DATE_START',
    'EDIT_DATE_END',
    'EDIT_COUNTRY',
    'EDIT_PHOTO',
    'EDIT_PREVIEW',
    'PUBLISH_EVENT',
    'DELETE_EVENT',
    'DELETE_CONFIRMED',
    'CALLBACK_QUERY',
    'SELECT_ALM',
    'SELECT_EVENT',
    'BACK_LIST',
    'FORWARD_LIST',
    'CURRENT_EVENT_ID',
    'DATE_COUNTER',
    'PAGE_SLICE',
    'START_PAGE',
    'END_PAGE',
)

# Messages to user
TEXT_REQUEST = {
    EDIT_NAME: "Укажите название события (до 50 символов)",
    EDIT_CITY: "Укажите город (до 50 символов)",
    EDIT_DESC: "Добавьте описание события (до 1000 символов)",
    EDIT_DATE_START: "Укажите дату начала события",
    EDIT_DATE_END: "Укажите дату окончания события",
    EDIT_COUNTRY: "Укажите страну (до 50 символов)",
    EDIT_PHOTO: "Добавьте картинку к описанию (JPG/JPEG, PNG, GIF, размер файла до 10 Мб)",
    CREATE_EVENT: "Пожалуйста, заполните данные о событии, которое вы планируете добавить в календарь \U0000270D",
    CALENDAR: 'Выберите период'
}

RU_LSTEP = {'y': 'год', 'm': 'месяц', 'd': 'день'}

RU_MONTH = {
    1: 'января',
    2: 'февраля',
    3: 'марта',
    4: 'апреля',
    5: 'мая',
    6: 'июня',
    7: 'июля',
    8: 'августа',
    9: 'сентября',
    10: 'октября',
    11: 'ноября',
    12: 'декабря',
}

RU_MONTH_CAPITALIZED = {
    1: 'Январь',
    2: 'Февраль',
    3: 'Март',
    4: 'Апрель',
    5: 'Май',
    6: 'Июнь',
    7: 'Июль',
    8: 'Август',
    9: 'Сентябрь',
    10: 'Октябрь',
    11: 'Ноябрь',
    12: 'Декабрь',
}

NUM_EVENTS_ON_PAGE = 5