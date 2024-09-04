import telebot
from telebot import custom_filters, StateMemoryStorage
from telebot.states import StatesGroup, State
from telebot.types import ReplyKeyboardRemove, CallbackQuery

from scrap import *
from functools import wraps
from config import TELEGRAM_BOT_TOKEN, ALLOWED_USER_IDS
from buttons import start_markup, select_delete_unit_markup, cancel_inline_markup, lesson_search_markup

state_storage = StateMemoryStorage()

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN, state_storage=state_storage)


class MyStates(StatesGroup):
    last_message = State()

    waiting_for_input = State()
    waiting_for_lesson_group_code = State()

    lesson_code = State()
    lesson_group_code = State()
    cancel_status = State()


def restrict_access(func):
    @wraps(func)
    def wrapped(message, *args, **kwargs):
        if message.from_user.id not in ALLOWED_USER_IDS:
            bot.reply_to(message, "شما اجازه دسترسی به این ربات را ندارید.")
            return
        return func(message, *args, **kwargs)

    return wrapped


@bot.message_handler(func=lambda message: message.text == "انتخاب واحد")
@restrict_access
def unit_selection(message):
    msg = bot.send_message(
        message.chat.id,
        text="""گزینه موردنظر را انتخاب کنید:""",
        reply_markup=select_delete_unit_markup()
    )
    with bot.retrieve_data(message.from_user.id) as user_data:
        user_data["last_message"] = msg
    bot.register_next_step_handler(msg, unit_selection_action)


@restrict_access
def unit_selection_action(message):
    with bot.retrieve_data(message.from_user.id) as user_data:
        print(user_data.get("cancel_status"))
        if message.text == "بازگشت به منو اصلی":
            bot.send_message(message.chat.id, "شما به منوی اصلی بازگشتید.", reply_markup=start_markup())
            return
        if message.text in ["افزودن درس", "حذف درس"]:
            user_data["lesson_action"] = "add_lesson" if message.text == "افزودن درس" else "remove_lesson"
            bot.set_state(message.from_user.id, MyStates.waiting_for_input)
            msg = bot.send_message(
                chat_id=message.chat.id,
                text="کد درس را وارد کنید:",
                reply_markup=cancel_inline_markup()
            )
            user_data["last_message"] = msg
        else:
            msg = bot.send_message(
                chat_id=message.chat.id,
                text="ورودی نادرست است!\nمیخوایی درس حذف کنی یا برداری؟",
                reply_markup=select_delete_unit_markup()
            )
            bot.register_next_step_handler(message, unit_selection_action)


@bot.message_handler(state=MyStates.waiting_for_input)
@restrict_access
def get_lesson_code(message):
    with bot.retrieve_data(message.from_user.id) as user_data:
        print(user_data)
        last_message = user_data.get("last_message")
        lesson_code = message.text
        bot.edit_message_reply_markup(
            chat_id=last_message.chat.id,
            message_id=last_message.id,
            reply_markup=None
        )
        if lesson_code.isdigit():
            user_data["lesson_code"] = message.text
            msg = bot.reply_to(message, text=f"کد درس انتخاب شده:{lesson_code} "
                                             "\nکد گروه را وارد نمایید:", reply_markup=cancel_inline_markup())
            # bot.register_next_step_handler(msg, get_group_code)
            bot.delete_state(message.from_user.id, message.chat.id)
            bot.set_state(message.from_user.id, MyStates.waiting_for_lesson_group_code)

        elif lesson_code == "بازگشت":
            msg = bot.reply_to(message, "عملیات لغو شد.")
            bot.delete_state(message.from_user.id, message.chat.id)
        else:
            msg = bot.send_message(message.chat.id, text="ورودی نامعتبر است!\nمجددا تلاش کنید:",
                                   reply_markup=cancel_inline_markup())
        # bot.register_next_step_handler(message, get_lesson_code)
        user_data["last_message"] = msg


@bot.message_handler(state=MyStates.waiting_for_lesson_group_code)
@restrict_access
def get_group_code(message):
    with bot.retrieve_data(message.from_user.id) as user_data:
        bot.edit_message_reply_markup(
            chat_id=user_data["last_message"].chat.id,
            message_id=user_data["last_message"].id, reply_markup=None
        )
        if message.text.isdigit():
            msg = bot.reply_to(
                message,
                text=f"کد درس انتخاب شده:{user_data['lesson_code']} \n:کد گروه انتخاب شده{message.text}\n{user_data['lesson_action']}",
                reply_markup=start_markup()
            )
            bot.delete_state(message.from_user.id, message.chat.id)
            # TODO: Select or Remove lesson
        else:
            msg = bot.send_message(
                chat_id=message.chat.id, text="ورودی نامعتبر است!\nمجددا تلاش کنید:",
                reply_markup=cancel_inline_markup()
            )
        user_data["last_message"] = msg


@bot.message_handler(func=lambda message: message.text == "دروس ارائه شده")
@restrict_access
def get_lesson(message):
    bot.send_message(message.chat.id, "جستجو در بین...", reply_markup=lesson_search_markup())
    bot.register_next_step_handler(message, get_lesson_status_search)


def get_lesson_status_search(message, ):
    if message.text in ["دروس دارای ظرفیت", "دروس تکمیل"]:
        bot.reply_to(message, text="کد یا نام درس را وارد کنید (حداقل 3 حرف):")
        bot.register_next_step_handler(message, get_lesson_name, message.text)
    else:
        bot.send_message(message.chat.id, text="ورودی نادرست است!")
        return


def get_lesson_name(message, lesson_status):
    if len(message.text) < 3:
        bot.send_message(message.chat.id, text="ورودی باید حداقل دارای 3 حرف باشد!")
        return
    bot.send_message(chat_id=message.chat.id, text="درحال دریافت اطلاعات...")
    lesson = message.text
    lesson_status = "NotComplete" if lesson_status == "دروس دارای ظرفیت" else "Complete"
    for val in get_lessons(lesson, lesson_status):
        if type(val["message"]) == str:
            bot.send_message(message.chat.id, text=val["message"], reply_markup=start_markup())
        elif type(val["message"]) == list:
            for i in val["message"]:
                bot.send_message(message.chat.id, text=i, reply_markup=start_markup())



@bot.message_handler(func=lambda message: message.text == "دروس دانشجو در نیمسال")
@restrict_access
def lessons_in_semester(message):
    text = get_my_courses_in_this_semester()
    bot.send_message(message.chat.id, text=text)


@bot.message_handler(func=lambda message: message.text == "دریافت کارنامه موقت")
@restrict_access
def get_temporary_work_report(message):
    bot.send_message(message.chat.id, get_lesson_temporary_work_report())


@bot.message_handler(func=lambda message: message.text == "تائیدیه انتخاب واحد")
@restrict_access
def unit_select_confirmation(message):
    response = get_unit_confirmation(user_id=None)
    if response["status"] == "Error":
        bot.send_message(message.chat.id, text=response["message"])
        return
    with open(response["file_address"], 'rb') as file:
        bot.send_document(message.chat.id, file)


@bot.callback_query_handler(func=lambda call: call.data == "cancel")
@restrict_access
def handel_inline_buttons(call: CallbackQuery):
    bot.delete_state(call.from_user.id, call.message.chat.id)
    bot.send_message(call.message.chat.id, "شما به منوی اصلی بازگشتید.", reply_markup=start_markup())
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)


@bot.message_handler(func=lambda x: True)
@restrict_access
def send_welcome(message):
    if message.from_user.id not in ALLOWED_USER_IDS:
        bot.reply_to(message, "متأسفانه شما مجاز به استفاده از این ربات نیستید.")
        return
    bot.reply_to(message, "خب چیکار میخوایی بکنی؟", reply_markup=start_markup())


bot.add_custom_filter(custom_filters.StateFilter(bot))

bot.infinity_polling(none_stop=True)

get_lesson_temporary_work_report()