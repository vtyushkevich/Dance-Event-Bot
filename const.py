# Callback data
START, ARCHIVE, START_OVER, MANAGEMENT, EDIT, CREATE, GO_BACK = (
    'START',
    'ARCHIVE',
    'START_OVER',
    'MANAGEMENT',
    'EDIT',
    'CREATE',
    'GO_BACK',
)

# Stages
TOP_LEVEL, CREATE_EVENT, CREATE_DATE, CREATE_PROPERTY, CREATE_PHOTO = range(5)

(
    EDIT_NAME,
    EDIT_CITY,
    EDIT_DESC,
    EDIT_DATE_START,
    EDIT_DATE_END,
    EDIT_COUNTRY,
    EDIT_PHOTO,
    EDIT_PREVIEW,
    PUBLISH_EVENT
) = (
    'EDIT_NAME',
    'EDIT_CITY',
    'EDIT_DESC',
    'EDIT_DATE_START',
    'EDIT_DATE_END',
    'EDIT_COUNTRY',
    'EDIT_PHOTO',
    'EDIT_PREVIEW',
    'PUBLISH_EVENT'
)

FLAG_RU, FLAG_TR, FLAG_HR = (
    "\U0001F1F7\U0001F1FA",
    "\U0001F1F9\U0001F1F7",
    "\U0001F1ED\U0001F1F7",
)

TEXT_REQUEST = {
    EDIT_NAME: "Укажите название события (до 50 символов)",
    EDIT_CITY: "Укажите город (до 50 символов)",
    EDIT_DESC: "Добавьте описание события (до 1000 символов)",
    EDIT_DATE_START: "Укажите дату начала события",
    EDIT_DATE_END: "Укажите дату окончания события",
    EDIT_COUNTRY: "Укажите страну (до 50 символов)",
    EDIT_PHOTO: "Добавьте картинку к описанию",
    CREATE_EVENT: "Пожалуйста, заполните данные о событии, которое вы планируете добавить в календарь \U0000270D",
}