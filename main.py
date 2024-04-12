from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackContext, ContextTypes, ApplicationBuilder, CallbackQueryHandler
from return_list import return_list  # Assuming this file contains the return_list function
import pandas as pd
from return_list import return_df


# # Load DataFrame from CSV file
df = return_df()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command."""
    welcome_message = (
        "به ربات آشپز باشی خوش اومدی، کمک ات میکنم بهت پیشنهاد بدم با مواد اولیه ای که داری چی بپزی.👨🏻‍🍳"
    )
    await context.bot.send_message(text=welcome_message, chat_id=update.message.from_user.id)

async def get_user_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_choice = update.effective_message.text
    query = return_list(str(user_choice))
    options = []
    for _, row in df.iloc[query].iterrows():
        button = InlineKeyboardButton(str(row["title"]), callback_data=str(row["id"]))
        options.append([button])
    reply_markup = InlineKeyboardMarkup(options)
    await context.bot.send_message(text="من با توجه به مواد اولیه ای که بهم دادی تونستم این غذا های خوشمزه ایرانی رو برات پیدا کنم،روی عنوان هر کدوم کلیک کن تا نحوه پخت رو در اختیارت بذارم 👨🏻‍🍳", chat_id=update.message.from_user.id, reply_markup=reply_markup)


async def button_click(update: Update, context: CallbackContext):
    query = update.callback_query
    chosen_option_index = int(query.data)
    print(query.data)
    # Now you can use the chosen_option_index to get the selected option from your dataframe
# Extracting relevant information from the dataframe

    chosen_option_data = df.iloc[chosen_option_index - 1]
    
    # Creating a detailed response message
    response_message = f"شما {chosen_option_data['title']} را انتخاب کردید.\n\n"
    response_message += f"مواد لازم: {chosen_option_data['mavad']}\n\n"
    response_message += f"طریقه آماده سازی: {chosen_option_data['instruction']}\n\n"
    response_message += f"زمان پخت: {chosen_option_data['cook_time']} "

    # Sending the detailed response to the user
    await context.bot.send_message(text=response_message, chat_id=query.message.chat_id)
    await context.bot.send_message(text="برای شروع دوباره /start رو تایپ کن یا از منوی پایین انتخاب کن👨🏻‍🍳", chat_id=query.message.chat_id)
    
    
    # Your existing logic for processing button_data
if __name__ == "__main__":
    # Create an application using the Telegram bot token
    application = ApplicationBuilder().token("7064472895:AAE22KqqkA7Wa9WqkE2B5cVdHbk_EZfZTE8").build()

    start_handler = CommandHandler('start', start)
    message_handler = MessageHandler(filters.TEXT, get_user_choice)
    button_handler = CallbackQueryHandler(button_click)

    application.add_handler(start_handler)
    application.add_handler(message_handler)
    application.add_handler(button_handler)
    application.run_polling()