from datetime import date, timedelta

import const as con


def validate_user_data(category: str, userdata=None, mimetype=None, checked_date=None, checked_sec_date=None):
    validation_passed, validation_comment = True, None
    if category == con.EDIT_NAME or category == con.EDIT_COUNTRY or category == con.EDIT_CITY:
        _name_len = 50
        validation_passed = len(userdata) < _name_len
        if not validation_passed:
            validation_comment = '\U0001F6AB Название не должно быть длиннее ' + str(_name_len) + ' символов'
            return validation_passed, validation_comment
    if category == con.EDIT_DESC:
        _name_len = 1000
        validation_passed = len(userdata) <= _name_len
        if not validation_passed:
            validation_comment = '\U0001F6AB Описание не должно быть длиннее ' + str(_name_len) + ' символов'
            return validation_passed, validation_comment
    if category == con.EDIT_PHOTO:
        if userdata:
            _name_len = 10485760
            validation_passed = userdata < _name_len
            if not validation_passed:
                validation_comment = '\U0001F6AB Картинка не должна весить более 10 Мб'
                return validation_passed, validation_comment
        if mimetype:
            validation_passed = mimetype == 'image/gif' or mimetype == 'image/jpeg' or mimetype == 'image/png' or mimetype == 'video/mp4'
            if not validation_passed:
                validation_comment = '\U0001F6AB Некорректный формат файла'
                return validation_passed, validation_comment
    if category == con.EDIT_DATE_START + '_dt' and checked_date is not None or \
            category == con.EDIT_DATE_END + '_dt' and checked_date is not None:
        validation_passed = checked_date >= date.today()
        if not validation_passed:
            validation_comment = '\U0001F6AB Дата события не должна быть в прошлом времени'
            return validation_passed, validation_comment
    if (category == con.EDIT_DATE_START + '_dt' or category == con.EDIT_DATE_END + '_dt') \
            and checked_date is not None and checked_sec_date is not None:
        _delta: timedelta = (checked_sec_date - checked_date)
        validation_passed = _delta.total_seconds() >= 0
        if not validation_passed:
            validation_comment = '\U0001F6AB Дата окончания события не должна быть раньше начала события'
            return validation_passed, validation_comment
    if category == con.PUBLISH_EVENT:
        validation_passed = userdata.user_data[con.EDIT_NAME] != "" \
                            and userdata.user_data[con.EDIT_CITY] != "" \
                            and userdata.user_data[con.EDIT_COUNTRY] != "" \
                            and userdata.user_data[con.EDIT_DESC] != "" \
                            and userdata.user_data[con.EDIT_DATE_START + '_dt'] is not None \
                            and userdata.user_data[con.EDIT_DATE_END + '_dt'] is not None
        if not validation_passed:
            validation_comment = '\U0001F6AB Не заполнены все поля события'
            return validation_passed, validation_comment
    return validation_passed, validation_comment