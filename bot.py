import os
import io
import base64
import requests
from telegrask import Telegrask
from telegram import Update
from telegram.ext import CallbackContext
import forecasts
from dotenv import load_dotenv

load_dotenv()

bot = Telegrask(os.getenv("API_KEY"))

info_message="""
useful links:
live report - https://obserwatorzy.info/
dynamic map from IMGW - https://meteo.imgw.pl/dyn/
IMGW warnings - https://meteo.imgw.pl/dyn/?osmet=true
IMGW forecast - https://meteo.imgw.pl/
live lightnings map - https://www.lightningmaps.org/ 
"""

@bot.command("info", help='usefull links')
def info(update: Update, context: CallbackContext):
    update.message.reply_text(info_message)

@bot.command("flist", help='list all avaliable foreasts')
def all_forecasts_command(update: Update, context: CallbackContext):
    res = forecasts.get_all_as_text()
    update.message.reply_text(res)

@bot.command("fmap", help = "get forecast map")
def forecats_map(update: Update, context: CallbackContext):
    index = get_arg(context.args)
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
def forecast_info(update: Update, context: CallbackContext):
    index = get_arg(context.args)
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


@bot.command('laststate', help='last state from IMGW (use "desc" as an argument to get also description)')
def last_imgw_state(update: Update, context: CallbackContext):
    last_state = forecasts.get_last_imgw_state()
    image = last_state['forecast']['forecast']['images']['asPng']['asBase64']
    image_as_bytes = io.BytesIO(base64.b64decode(image))
    caption = ''
    if len(context.args) > 0 and context.args[0] == "desc":
        caption = last_state['forecast']['forecast']['keys']['ogólnie']
    
    update.message.reply_photo(photo=image_as_bytes, caption=caption)


@bot.command('lightnings', help='get lightnings map from obserwatorzy.info')
def lightnings_map(update: Update, context: CallbackContext):
    res = requests.get("https://obserwatorzy.info/maps/statyczna.jpg", stream=True)
    update.message.reply_photo(photo=res.raw)

def get_arg(args: list[str]):
    if len(args) < 1:
        return None
    if args[0] == "current":
        return 0
    try:
        return int(args[0]) if int(args[0]) >= 0 else None
    except ValueError:
        return None


if __name__ == "__main__":
    bot.run(debug=True)