import discord
from discord.ext import commands
import json
import urllib
import os

# メッセージ内容を読み取るためのインテントを設定
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)
bot.remove_command("help")

# 47都道府県の都市コード
citycodes = {
    "北海道":"016010",
    "青森":"020010",
    "岩手":"030010",
    "宮城":"040010",
    "秋田":"050010",
    "山形":"060010",
    "福島":"070010",
    "茨城":"080010",
    "栃木":"090010",
    "群馬":"100010",
    "埼玉":"110010",
    "千葉":"120010",
    "東京":"130010",
    "神奈川":"140010",
    "新潟":"150010",
    "富山":"160010",
    "石川":"170010",
    "福井":"180010",
    "長野":"200010",
    "岐阜":"210010",
    "静岡":"220010",
    "愛知":"230010",
    "三重":"240010",
    "滋賀":"250010",
    "京都":"260010",
    "大阪":"270000",
    "兵庫":"280010",
    "奈良":"290010",
    "和歌山":"300010",
    "鳥取":"310010",
    "島根":"320010",
    "岡山":"330010",
    "広島":"340010",
    "山口":"350010",
    "徳島":"360010",
    "香川":"370000",
    "愛媛":"380010",
    "高知":"390010",
    "福岡":"400010",
    "佐賀":"410010",
    "長崎":"420010",
    "熊本":"430010",
    "大分":"440010",
    "宮崎":"450010",
    "鹿児島":"460010",
    "沖縄":"471010",    
}

@bot.event
async def on_ready():
    print(f"起動完了: {bot.user}")

# 天気確認コマンドの作成 (/tenki 都道府県名)
@bot.command(name="tenki")
async def tenki(ctx, city: str = None):
    if not city:
        await ctx.send("地域を指定してください。例: `/tenki 東京`")
        return

    if city in citycodes:
        citycode = citycodes[city]
        resp = urllib.request.urlopen(f"https://weather.tsukumijima.net/api/forecast/city/{citycode}").read()
        resp = json.loads(resp.decode("utf-8"))
        msg = "__【お天気情報：**" + resp["location"]["city"] + "**】__\n"
        for f in resp["forecasts"]:
          msg += f["dateLabel"] + "：**" + f["telop"] + "**\n"
        msg += "```" + resp["description"]["bodyText"] + "```"

        await ctx.send(msg)
    else:
        await ctx.send("そこの天気はわかりません...")

# Renderの環境変数からDiscordトークンを読み込む
TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)
