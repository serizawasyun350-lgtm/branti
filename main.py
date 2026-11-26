import discord
from discord.ext import commands
from discord import app_commands
import json
import urllib
import os

intents = discord.Intents.default()
intents.message_content = True

# botの定義
bot = commands.Bot(command_prefix="/", intents=intents)

# 47都道府県の都市コード
citycodes = {
    "北海道":"016010", "青森":"020010", "岩手":"030010", "宮城":"040010",
    "秋田":"050010", "山形":"060010", "福島":"070010", "茨城":"080010",
    "栃木":"090010", "群馬":"100010", "埼玉":"110010", "千葉":"120010",
    "東京":"130010", "神奈川":"140010", "新潟":"150010", "富山":"160010",
    "石川":"170010", "福井":"180010", "長野":"200010", "岐阜":"210010",
    "静岡":"220010", "愛知":"230010", "三重":"240010", "滋賀":"250010",
    "京都":"260010", "大阪":"270000", "兵庫":"280010", "奈良":"290010",
    "和歌山":"300010", "鳥取":"310010", "島根":"320010", "岡山":"330010",
    "広島":"340010", "山口":"350010", "徳島":"360010", "香川":"370000",
    "愛媛":"380010", "高知":"390010", "福岡":"400010", "佐賀":"410010",
    "長崎":"420010", "熊本":"430010", "大分":"440010", "宮崎":"450010",
    "鹿児島":"460010", "沖縄":"471010",    
}

SETTINGS_FILE = "user_settings.json"

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_settings(settings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=4)

user_settings = load_settings()

@bot.event
async def on_ready():
    # Discordへスラッシュコマンドを同期（登録）する
    try:
        synced = await bot.tree.sync()
        print(f"スラッシュコマンドを {len(synced)} 個同期しました。")
    except Exception as e:
        print(f"コマンドの同期に失敗しました: {e}")
    
    print(f"起動完了: {bot.user}")

# 1. 地域登録コマンド（スラッシュコマンド）
@bot.tree.command(name="set_city", description="自分のデフォルトの都道府県を設定します")
@app_commands.describe(city="設定する都道府県名（例: 東京）")
async def set_city(interaction: discord.Interaction, city: str):
    if city not in citycodes:
        await interaction.response.send_message("正しい都道府県名を指定してください。例: `/set_city 東京`", ephemeral=True)
        return

    user_id = str(interaction.user.id)
    if user_id not in user_settings:
        user_settings[user_id] = {"use_location": True, "city": city}
    else:
        user_settings[user_id]["city"] = city
        
    save_settings(user_settings)
    await interaction.response.send_message(f"あなたの地域を **{city}** に設定しました。（位置情報取得: ON）", ephemeral=True)

# 2. 位置情報設定コマンド（true / false）
@bot.tree.command(name="location_setting", description="登録した地域の自動使用を切り替えます")
@app_commands.describe(flag="true または false を選択してください")
@app_commands.choices(flag=[
    app_commands.Choice(name="true", value="true"),
    app_commands.Choice(name="false", value="false")
])
async def location_setting(interaction: discord.Interaction, flag: str):
    use_loc = (flag.lower() == "true")
    user_id = str(interaction.user.id)
    
    if user_id not in user_settings:
        user_settings[user_id] = {"use_location": use_loc, "city": None}
    else:
        user_settings[user_id]["use_location"] = use_loc

    save_settings(user_settings)
    status_text = "有効 (true)" if use_loc else "無効 (false)"
    await interaction.response.send_message(f"位置情報（登録地域）の自動取得を **{status_text}** にしました。", ephemeral=True)

# 3. 天気確認コマンド
@bot.tree.command(name="tenki", description="指定した地域、または登録した地域の天気を確認します")
@app_commands.describe(city="都道府県名（省略時は登録地域を使用）")
async def tenki(interaction: discord.Interaction, city: str = None):
    user_id = str(interaction.user.id)
    setting = user_settings.get(user_id, {"use_location": False, "city": None})

    if not city:
        if setting.get("use_location") and setting.get("city"):
            city = setting["city"]
        else:
            await interaction.response.send_message(
                "地域が指定されていません。\n`/set_city 都道府県名` で登録するか、`/tenki 東京` のように指定してください。", 
                ephemeral=True
            )
            return

    if city in citycodes:
        citycode = citycodes[city]
        try:
            resp = urllib.request.urlopen(f"https://weather.tsukumijima.net/api/forecast/city/{citycode}").read()
            resp = json.loads(resp.decode("utf-8"))
            msg = "__【お天気情報：**" + resp["location"]["city"] + "**】__\n"
            for f in resp["forecasts"]:
                msg += f["dateLabel"] + "：**" + f["telop"] + "**\n"
            msg += "```" + resp["description"]["bodyText"] + "```"

            await interaction.response.send_message(msg)
        except Exception as e:
            await interaction.response.send_message("天気情報の取得に失敗しました。", ephemeral=True)
    else:
        await interaction.response.send_message("そこの天気はわかりません...", ephemeral=True)

TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)
