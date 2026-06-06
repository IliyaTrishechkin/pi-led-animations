import os
import logging
import traceback
import threading
from pathlib import Path
from dotenv import load_dotenv
from LED_animations import leds, type_list, LED_logic
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters

led_thread = None
stop_event = None

load_dotenv(Path(__file__).parent / '.env', encoding='utf-8-sig')
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_IDENT"))

MENU_EDIT, TIME_EDIT, LEN_EDIT, QUANTITY_EDIT = range(4)


async def error_handler(update, context):
    print(f"Ошибка: {context.error}")
    tb = "".join(traceback.format_exception(None, context.error, context.error.__traceback__))
    try:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"⚠️ Ошибка в боте:\n\n<pre>{tb}</pre>",
            parse_mode="HTML"
        )
    except Exception as e:
        print(f"Не удалось отправить сообщение админу: {e}")
    if update and getattr(update, "message", None):
        try:
            await update.message.reply_text("Произошла ошибка 😔. Администратор уже уведомлен.")
        except Exception:
            pass


def main_menu_text():
    text_mes = """
💡 LED Animations Controller

This bot allows you to manage LED animation modes running on your Raspberry Pi.

Please select an animation mode:
"""
    return text_mes


def main_menu_kb():
    kb = [[InlineKeyboardButton(i, callback_data=f"LED_mode|{i}")] for i in type_list]
    kb.append([InlineKeyboardButton("Stop animation", "action|stop")])
    return kb


async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(main_menu_text(), reply_markup=InlineKeyboardMarkup(main_menu_kb()))


async def show_menu_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cfg = context.user_data["config"]
    text_mes = "📌 Parameters:\n\n" + "\n".join(f"{k}: {v}" for k, v in cfg.items())
    kb = [
        [InlineKeyboardButton("Edit Time", callback_data="edit|time")],
        [InlineKeyboardButton("Edit Len", callback_data="edit|len")],
        [InlineKeyboardButton("Edit Quantity", callback_data="edit|quantity")],
        [InlineKeyboardButton("Run code -->", "edit|run")],
        [InlineKeyboardButton(" <-- Back", "action|back")]
    ]

    await update.message.reply_text(text_mes, reply_markup=InlineKeyboardMarkup(kb))
    return MENU_EDIT


async def edit_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        value = float(update.message.text)
    except ValueError:
        await update.message.reply_text("❌ Must be a float number")
        return TIME_EDIT

    context.user_data["config"]["time"] = value
    return await show_menu_edit(update, context)


async def edit_len(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        value = int(update.message.text)
        if value >= len(leds):
            await update.message.reply_text(f"❌ Error: The specified length ({value}) exceeds the number of available LED pins ({len(leds)}).")
            return LEN_EDIT
    except ValueError:
        await update.message.reply_text("❌ Must be integer number")
        return LEN_EDIT

    context.user_data["config"]["len"] = value
    return await show_menu_edit(update, context)


async def edit_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        value = int(update.message.text)
    except ValueError:
        await update.message.reply_text("❌ Must be integer number")
        return QUANTITY_EDIT

    context.user_data["config"]["quantity"] = value
    return await show_menu_edit(update, context)


async def ClikButton(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    cmd, arg = q.data.split("|")

    match cmd:
        case "LED_mode":
            context.user_data["config"] = {
                "type": arg,
                "time": 0.5,
                "len": 1,
                "quantity": 5
            }
            cfg = context.user_data["config"]
            text_mes = "📌 Parameters:\n\n" + "\n".join(f"{k}: {v}" for k, v in cfg.items())
            kb = [
                [InlineKeyboardButton("Edit Time", callback_data="edit|time")],
                [InlineKeyboardButton("Edit Len", callback_data="edit|len")],
                [InlineKeyboardButton("Edit Quantity", callback_data="edit|quantity")],
                [InlineKeyboardButton("Run code -->", "edit|run")],
                [InlineKeyboardButton(" <-- Back", "action|back")]
            ]

            await q.edit_message_text(text_mes, reply_markup=InlineKeyboardMarkup(kb))
            return MENU_EDIT
        
        case "edit":
            match arg:
                case "time":
                    await q.edit_message_text("Enter TIME value:")
                    return TIME_EDIT
                
                case "len":
                    await q.edit_message_text("Enter LEN value:")
                    return LEN_EDIT
                
                case "quantity":
                    await q.edit_message_text("Enter QUANTITY value:")
                    return QUANTITY_EDIT
                
                case "run":
                    global led_thread, stop_event

                    if led_thread and led_thread.is_alive():
                        stop_event.set()
                        led_thread.join()

                    cfg = context.user_data["config"]
                    stop_event = threading.Event()
                    led_thread = threading.Thread(
                        target=LED_logic,
                        args=(cfg["type"], cfg["time"], cfg["len"], cfg["quantity"], stop_event),
                        daemon=True
                    )

                    led_thread.start()
                    kb = [[InlineKeyboardButton(" <-- Back", "action|back")]]
                    await q.edit_message_text("Run code!", reply_markup=InlineKeyboardMarkup(kb))
                    return ConversationHandler.END
                
                case "back":
                    await q.edit_message_text(main_menu_text(), reply_markup=InlineKeyboardMarkup(main_menu_kb()))
                    return ConversationHandler.END
        
        case "action":
            match arg:
                case "stop":
                    global led_thread, stop_event

                    if led_thread and led_thread.is_alive() and stop_event:
                        stop_event.set()
                        led_thread.join()

                        led_thread = None
                        stop_event = None

                    await q.edit_message_text("Animation stopped\n\n" + main_menu_text(),  reply_markup=InlineKeyboardMarkup(main_menu_kb()))
                
                case "back":
                    await q.edit_message_text(main_menu_text(), reply_markup=InlineKeyboardMarkup(main_menu_kb()))



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(TOKEN).build()


    conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(ClikButton, pattern="^LED_mode\\|")],
        states={
            MENU_EDIT: [CallbackQueryHandler(ClikButton, pattern="^edit\\|")],
            TIME_EDIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_time)],
            LEN_EDIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_len)],
            QUANTITY_EDIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_quantity)],
        },
        fallbacks=[]
    )


    app.add_handler(conv)
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CallbackQueryHandler(ClikButton, pattern="^(LED_mode|edit|action)\|"))
    app.add_error_handler(error_handler)


    app.run_polling(drop_pending_updates=True)
