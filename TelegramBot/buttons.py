import telebot
from telebot.types import InlineKeyboardButton


def authentication_markup():
    kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.row(
        InlineKeyboardButton("احراز هویت", callback_data="authentication"),
    )
    return kb


def start_markup():
    kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.row(
        InlineKeyboardButton("دروس ارائه شده", callback_data="get_lesson"),
        InlineKeyboardButton("انتخاب واحد", callback_data="unit_selection"),
    )
    kb.add(InlineKeyboardButton("دروس دانشجو در نیمسال", callback_data="lessons_in_semester"))
    kb.add(InlineKeyboardButton("تائیدیه انتخاب واحد", callback_data="unit_select_confirmation"))
    kb.add(InlineKeyboardButton("دریافت کارنامه موقت", callback_data="lesson_term_work_report"))
    return kb


def select_delete_unit_markup():
    kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    kb.row(
        InlineKeyboardButton("حذف درس", callback_data="remove_lesson"),
        InlineKeyboardButton("افزودن درس", callback_data="add_lesson"),
    )
    kb.add(InlineKeyboardButton("بازگشت به منو اصلی", callback_data="rollback_to_menu"))
    return kb


def cancel_inline_markup():
    kb = telebot.types.InlineKeyboardMarkup()
    kb.row(
        InlineKeyboardButton("انصراف", callback_data="cancel"),
    )
    return kb


def rollback_to_menu_markup():
    kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    kb.row(
        InlineKeyboardButton("بازگشت به منو اصلی", callback_data="rollback_to_menu"),
    )
    return kb


def lesson_search_markup():
    kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    kb.row(
        InlineKeyboardButton("دروس دارای ظرفیت", callback_data="not_completed_lessons"),
        InlineKeyboardButton("دروس تکمیل", callback_data="completed_courses"),
    )
    return kb
