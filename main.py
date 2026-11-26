import discord
from discord.ext import commands
from discord import app_commands
import json
import urllib.request
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- 1. Renderで「Live」にするための簡易Webサーバー設定 ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Discord Bot is alive!")
    def log_message(self, format, *args):
        pass

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

threading.Thread(target=run_web_server, daemon=True).start()

# --- 2. Discord Botの設定 ---
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)

# 都道府県および主要な市町村のコード一覧
citycodes = {
    # 北海道
    "札幌市": "016010", "函館市": "014010", "旭川市": "012010", "北海道": "016010",
    # 青森
    "青森市": "020010", "弘前市": "020020", "青森": "020010",
    # 岩手
    "盛岡市": "030010", "岩手": "030010",
    # 宮城
    "仙台市": "040010", "宮城": "040010",
    # 秋田
    "秋田市": "050010", "秋田": "050010",
    # 山形
    "山形市": "060010", "山形": "060010",
    # 福島
    "福島市": "070010", "いわき市": "070020", "福島": "070010",
    # 茨城
    "水戸市": "080010", "茨城": "080010",
    # 栃木
    "宇都宮市": "090010", "栃木": "090010",
    # 群馬
    "前橋市": "100010", "高崎市": "100020", "群馬": "100010",
    # 埼玉
    "さいたま市": "110010", "川越市": "110020", "熊谷市": "110030", "埼玉": "110010",
    # 千葉
    "千葉市": "120010", "船橋市": "120020", "千葉": "120010",
    # 東京
    "東京": "130010", "東京都": "130010", "千代田区": "130010", "新宿区": "130010",
    # 神奈川
    "横浜市": "140010", "川崎市": "140020", "相模原市": "140030", "鎌倉市": "140040", "神奈川": "140010",
    # 新潟
    "新潟市": "150010", "長岡市": "150020", "新潟": "150010",
    # 富山
    "富山市": "160010", "富山": "160010",
    # 石川
    "金沢市": "170010", "石川": "170010",
    # 福井
    "福井市": "180010", "福井": "180010",
    # 山梨
    "甲府市": "190010", "山梨": "190010",
    # 長野
    "長野市": "200010", "松本市": "200020", "長野": "200010",
    # 岐阜
    "岐阜市": "210010", "岐阜": "210010",
    # 静岡
    "静岡市": "220010", "浜松市": "220020", "静岡": "220010",
    # 愛知
    "名古屋市": "230010", "豊田市": "230020", "愛知": "230010",
    # 三重
    "津市": "240010", "四日市市": "240020", "三重": "240010",
    # 滋賀
    "大津市": "250010", "滋賀": "250010",
    # 京都
    "京都市": "260010", "京都": "260010",
    # 大阪
    "大阪市": "270000", "堺市": "270020", "大阪": "270000",
    # 兵庫
    "神戸市": "280010", "姫路市": "280020", "西宮市": "280030", "兵庫": "280010",
    # 奈良
    "奈良市": "290010", "奈良": "290010",
    # 和歌山
    "和歌山市": "300010", "和歌山": "300010",
    # 鳥取
    "鳥取市": "310010", "鳥取": "310010",
    # 島根
    "松江市": "320010", "島根": "320010",
    # 岡山
    "岡山市": "330010", "倉敷市": "330020", "岡山": "330010",
    # 広島
    "広島市": "340010", "福山市": "340020", "広島": "340010",
    # 山口
    "山口市": "350010", "下関市": "350020", "山口": "350010",
    # 徳島
    "徳島市": "360010", "徳島": "360010",
    # 香川
    "高松市": "370000", "香川": "370000",
    # 愛媛
    "松山市": "380010", "愛媛": "380010",
    # 高知
    "高知市": "390010", "高知": "390010",
    # 福岡
    "福岡市": "400010", "北九州市": "400020", "久留米市": "400030", "福岡": "400010",
    # 佐賀
    "佐賀市": "410010", "佐賀": "410010",
    # 長崎
    "長崎市": "420010", "佐世保市": "420020", "長崎": "420010",
    # 熊本
    "熊本市": "430010", "熊本": "430010",
    # 大分
    "大分市": "440010", "大分": "440010",
    # 宮崎
    "宮崎市": "450010", "宮崎": "450010",
    # 鹿児島
    "鹿児島市": "460010", "鹿児島": "460010",
    # 沖縄
    "那覇市": "471010", "沖縄": "471010"
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
    try:
        synced = await bot.tree.sync()
        print(f"スラッシュコマンドを {len(synced)} 個同期しました。")
    except Exception as e:
        print(f"コマンドの同期に失敗しました: {e}")
    
    print(f"起動完了: {bot.user}")

# 入力文字に応じてオートコンプリートで候補を表示（「市」や「都」で絞り込み可能）
async def city_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:
    return [
        app_commands.Choice(name=city, value=city)
        for city in citycodes.keys() if current in city
    ][:25]

@bot.tree.command(name="set_city", description="自分のデフォルトの地域（都道府県・市）を設定します")
@app_commands.describe(city="設定する地域名（例: 横浜市、東京）")
@app_commands.autocomplete(city=city_autocomplete)
async def set_city(interaction: discord.Interaction, city: str):
    if city not in citycodes:
        await interaction.response.send_message("登録されていない地域です。候補から選択してください。", ephemeral=True)
        return

    user_id = str(interaction.user.id)
    if user_id not in user_settings:
        user_settings[user_id] = {"use_location": True, "city": city}
    else:
        user_settings[user_id]["city"] = city
        
    save_settings(user_settings)
    await interaction.response.send_message(f"あなたの地域を **{city}** に設定しました。（位置情報取得: ON）", ephemeral=True)

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

@bot.tree.command(name="tenki", description="指定した地域、または登録した地域の天気を確認します")
@app_commands.describe(city="地域名（省略時は登録地域を使用）")
@app_commands.autocomplete(city=city_autocomplete)
async def tenki(interaction: discord.Interaction, city: str = None):
    user_id = str(interaction.user.id)
    setting = user_settings.get(user_id, {"use_location": False, "city": None})

    if not city:
        if setting.get("use_location") and setting.get("city"):
            city = setting["city"]
        else:
            await interaction.response.send_message(
                "地域が指定されていません。\n`/set_city 地域名` で登録するか、コマンドで地域を選択してください。", 
                ephemeral=True
            )
            return

    if city in citycodes:
        citycode = citycodes[city]
        try:
            url = f"https://weather.tsukumijima.net/api/forecast/city/{citycode}"
            req = urllib.request.Request(
                url, 
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            )
            
            with urllib.request.urlopen(req) as response:
                resp = json.loads(response.read().decode("utf-8"))
                
            msg = "__【お天気情報：**" + resp["location"]["city"] + "**】__\n"
            for f in resp["forecasts"]:
                msg += f["dateLabel"] + "：**" + f["telop"] + "**\n"
            msg += "```" + resp["description"]["bodyText"] + "```"

            await interaction.response.send_message(msg)
        except Exception as e:
            print(f"Weather API Error: {e}")
            await interaction.response.send_message("天気情報の取得に失敗しました（APIへの接続に問題が発生しました）。", ephemeral=True)
    else:
        await interaction.response.send_message("そこの天気はわかりません...", ephemeral=True)

TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)
