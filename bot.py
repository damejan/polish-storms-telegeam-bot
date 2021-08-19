import os
import io
import base64
from telegrask import Telegrask
from telegram import Update
import forecasts
from dotenv import load_dotenv

load_dotenv()

bot = Telegrask(os.getenv("API_KEY"))

help_message="""
/help - display this message
/flist - list all avaliable foreasts
/fmap - get forecast map
/finfo - get forecast description
"""

@bot.custom_help_command
def help_command(update: Update, context, descriptions):
    update.message.reply_text(help_message)

@bot.command("flist", help='list all avaliable foreasts')
def all_forecasts_command(update: Update, context):
    res = forecasts.get_all_as_text()
    update.message.reply_text(res)

@bot.command("fmap", help = "get forecast map")
def forecats_map(update: Update, context):
    index = get_arg(update.message.text)
    if index is None:
        update.message.reply_text("invalid command")
        return

    forecast = forecasts.get_forecast(index)
    if forecast is None:
        update.message.reply_text("the forecast for this index doesn't exist")

    image = forecast['forecast']['forecast']['images']['asPng']['asBase64']
    caption = forecast['forecast']['forecast']['keys']['ogólnie']
    image_as_bytes = io.BytesIO(base64.b64decode(image))
    update.message.reply_photo(photo=image_as_bytes, caption=caption)

@bot.command("finfo", help = "get forecast description")
def forecast_info(update: Update, context):
    index = get_arg(update.message.text)
    if index is None:
        update.message.reply_text("invalid command")
        return
    
    forecast = forecasts.get_forecast(index)
    if forecast is None:
        update.message.reply_text("the forecast for this index doesn't exist")

    info = forecast['forecast']['forecast']['keys']['szczegółowo']
    if not info:
        update.message.reply_text("this forecast has no description")
        return

    update.message.reply_text(info)


def get_arg(message: str):
    arg = message.split(" ")
    if len(arg) < 2:
        return None
    if arg[1] == "current":
        return 0
    try:
        return int(arg[1]) if int(arg[1]) >= 0 else None
    except ValueError:
        return None


if __name__ == "__main__":
    bot.run(debug=True)