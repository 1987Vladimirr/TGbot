from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
import datetime
from telegram.ext import (Application,CommandHandler,CallbackContext,MessageHandler,filters,)

# ID администратора (замените на ваш Telegram ID)
ADMIN_ID = 1978304524 #1009629774 - id женя
Token = "7697134194:AAEzttiNl1821D0_ifa4JP5PhG_NKuxqrw0"

STEP_SERVICE = "выбор услуги"
STEP_DATE = "выбор даты"
STEP_TIME = "выбор времени"
STEP_NAME = "ввод имени"
STEP_PHONE = "ввод телефона"

# Данные пользователя
user_data = {}
# Список занятых слотов (пример: {(дата, время): True})
occupied_slots = {}

# Команда /start
async def start(update: Update, context: CallbackContext):
    user_data[update.message.chat.id] = {}
    keyboard = [["Депиляция", "Электроэпиляция"],["Моделирование фигуры", "Лифтинг лица"],["Отмена"],]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text("Здравствуйте! Выберите услугу для записи:", reply_markup=reply_markup)
    user_data[update.message.chat.id]["step"] = STEP_SERVICE

# Обработка сообщений
async def handle_message(update: Update, context: CallbackContext):
    chat_id = update.message.chat.id
    text = update.message.text

    # Убедимся, что chat_id существует в user_data
    if chat_id not in user_data:
        await update.message.reply_text("Пожалуйста, начните процесс заново, введя /start.")
        return

    if user_data[chat_id].get("step") == STEP_SERVICE:
        if text in ["Депиляция", "Электроэпиляция", "Моделирование фигуры", "Лифтинг лица"]:
            user_data[chat_id]["service"] = text
            user_data[chat_id]["step"] = STEP_DATE

            await update.message.reply_text(f"Вы выбрали услугу: {text}\nТеперь выберите дату записи (например, 25.03.2025):")
            
        elif text == "Отмена":
            await update.message.reply_text("Запись отменена. Для нового сеанса введите /start.",reply_markup=ReplyKeyboardRemove())
            
            user_data.pop(chat_id, None)
        else:
            await update.message.reply_text("Пожалуйста, выберите услугу из списка.")

    elif user_data[chat_id].get("step") == STEP_DATE:
        user_data[chat_id]["date"] = text
        user_data[chat_id]["step"] = STEP_TIME

        keyboard = [["09:00", "10:00", "12:00", "14:00", "16:00"] ,  ["18:00", "20:00", "Отмена"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("Выберите какой период времени удобный для Вас:", reply_markup=reply_markup)

    elif user_data[chat_id].get("step") == STEP_TIME:
        selected_date = user_data[chat_id].get("date")
        if text in ["09:00", "10:00", "12:00", "14:00", "16:00", "18:00", "20:00"]:
            if (selected_date, text) in occupied_slots:
                await update.message.reply_text("Извините, выбранное время уже занято. Пожалуйста, выберите другое время.")
            else:
                user_data[chat_id]["time"] = text
                user_data[chat_id]["step"] = STEP_NAME
                await update.message.reply_text("Пожалуйста, введите ваше имя:")
        elif text == "Отмена":
            await update.message.reply_text("Запись отменена. Для нового сеанса введите /start.",reply_markup=ReplyKeyboardRemove())
            user_data.pop(chat_id, None)

    elif user_data[chat_id].get("step") == STEP_NAME:
        user_data[chat_id]["name"] = text
        user_data[chat_id]["step"] = STEP_PHONE
        await update.message.reply_text("Пожалуйста, введите ваш номер телефона:")

    elif user_data[chat_id].get("step") == STEP_PHONE:
        user_data[chat_id]["phone"] = text

        # Теперь проверяем, что все поля заполнены
        service = user_data[chat_id].get("service", "")
        selected_date = user_data[chat_id].get("date", "")
        time = user_data[chat_id].get("time", "")
        name = user_data[chat_id].get("name", "")
        phone = user_data[chat_id].get("phone", "")

        if all([service, selected_date, time, name, phone]):
            # Помечаем выбранный слот как занятый
            occupied_slots[(selected_date, time)] = True


        # Завершение записи
        await update.message.reply_text(
            f"Спасибо за запись! ✅\n"
            f"✨ *Вы записаны на:* _{service}_\n"
            f"📅 *Дата:* _{selected_date}_\n"
            f"⏰ *Предварительное время:* _{time}_\n"
            f"🙋‍♂️ *Имя:* _{name}_\n"
            f"📞 *Телефон:* _{phone}_\n"
            f"Для согласования времени мастер с вами свяжется! 📞💖",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardRemove()
           
        )
            

        await update.message.reply_text(
            "Запись оформлена. Для нового сеанса введите /start.",)

        # Уведомление администратора
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                f"🌟 *Новая запись!* 🌟\n"
                f"🛠 *Услуга:* _{service}_\n"
                f"📅 *Дата:* _{selected_date}_\n"
                f"⏰ *Удобное время:* _{time}_\n"
                f"🙋‍♂️ *Имя клиента:* _{name}_\n"
                f"📞 *Телефон:* _{phone}_\n" "Свяжитесь с клиентом для согласования удобного для Вас времени!"),
            parse_mode="Markdown")

        # Очистка данных пользователя
        user_data.pop(chat_id, None)
        
#         # # Планируем напоминание за 1 день до записи
#         reminder_time = datetime.datetime.strptime(user_data[chat_id]["date"], "%d.%m.%Y") - datetime.timedelta(days=1)
#         new_func(context, chat_id, reminder_time)
#         user_data.pop(chat_id, None)

# def new_func(context, chat_id, reminder_time):
#     context.job_queue.run_once(send_reminder, when=reminder_time, context=chat_id)



# async def send_reminder(context: CallbackContext):
#     chat_id = context.job.context
#     keyboard = [["Подтвердить", "Отменить"]]
#     reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
#     await context.bot.send_message(
#         chat_id=chat_id,
#         text="Напоминаем о вашей записи. Пожалуйста, подтвердите или отмените:",
#         reply_markup=reply_markup
#     )

# async def handle_confirmation(update: Update, context: CallbackContext):
#     chat_id = update.message.chat.id
#     text = update.message.text
#     if text == "Подтвердить":
#         await update.message.reply_text(
#             "Спасибо за подтверждение! Ждем вас на приеме.",
#             reply_markup=ReplyKeyboardRemove()
#         )
#     elif text == "Отменить":
#         # Удаляем запись
#         for slot in occupied_slots.keys():
#             if slot[0] == user_data[chat_id]["date"] and slot[1] == user_data[chat_id]["time"]:
#                 del occupied_slots[slot]
#                 break
#         await update.message.reply_text(
#             "Ваша запись была отменена.",
#             reply_markup=ReplyKeyboardRemove()
        #)

def main():
    application = Application.builder().token(Token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    #application.add_handler(MessageHandler(filters.TEXT & filters.Regex("^(Подтвердить|Отменить)$"), handle_confirmation))

    application.run_polling()

if __name__ == "__main__":
    main()
    