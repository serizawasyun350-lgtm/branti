import discord
from discord.ext import commands
from discord import app_commands
import json
import urllib.request
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- 1. UptimeRobotおよびRenderのLive維持用Webサーバー ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"Bot is active and running!")
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

# 都道府県・市区町村のコード一覧
citycodes = {
    "北海道 札幌市": "016010", "北海道 函館市": "014010", "北海道 旭川市": "012010", "北海道 北海道": "016010",
    "青森県 青森市": "020010", "青森県 弘前市": "020020",
    "岩手県 盛岡市": "030010",
    "宮城県 仙台市": "040010",
    "秋田県 秋田市": "050010",
    "山形県 山形市": "060010",
    "福島県 福島市": "070010", "福島県 いわき市": "070020",
    "茨城県 水戸市": "080010",
    "栃木県 宇都宮市": "090010",
    "群馬県 前橋市": "100010", "群馬県 高崎市": "100020",
    "埼玉県 さいたま市": "110010", "埼玉県 川越市": "110020", "埼玉県 熊谷市": "110030",
    "千葉県 千葉市": "120010", "千葉県 船橋市": "120020",
    "東京都 東京": "130010", "東京都 千代田区": "130010", "東京都 新宿区": "130010",
    "神奈川県 横浜市": "140010", "神奈川県 川崎市": "140020", "神奈川県 相模原市": "140030", "神奈川県 鎌倉市": "140040",
    "新潟県 新潟市": "150010", "新潟県 長岡市": "150020",
    "富山県 富山市": "160010",
    "石川県 金沢市": "170010",
    "福井県 福井市": "180010",
    "山梨県 甲府市": "190010",
    "長野県 長野市": "200010", "長野県 松本市": "200020",
    "岐阜県 岐阜市": "210010",
    "静岡県 静岡市": "220010", "静岡県 浜松市": "220020",
    "愛知県 名古屋市": "230010", "愛知県 豊田市": "230020",
    "三重県 津市": "240010", "三重県 四日市市": "240020",
    "滋賀県 大津市": "250010",
    "京都府 京都市": "260010",
    "大阪府 大阪市": "270000", "大阪府 堺市": "270020",
    "兵庫県 神戸市": "280010", "兵庫県 姫路市": "280020", "兵庫県 西宮市": "280030",
    "奈良県 奈良市": "290010",
    "和歌山県 和歌山市": "300010",
    "鳥取県 鳥取市": "310010",
    "島根県 松江市": "320010",
    "岡山県 岡山市": "330010", "岡山県 倉敷市": "330020",
    "広島県 広島市": "340010", "広島県 福山市": "340020",
    "山口県 山口市": "350010", "山口県 下関市": "350020",
    "徳島県 徳島市": "360010",
    "香川県 高松市": "370000",
    "愛媛県 松山市": "380010",
    "高知県 高知市": "390010",
    "福岡県 福岡市": "400010", "福岡県 北九州市": "400020", "福岡県 久留米市": "400030",
    "佐賀県 佐賀市": "410010",
    "長崎県 長崎市": "420010", "長崎県 佐世保市": "420020",
    "熊本県 熊本市": "430010",
    "大分県 大分市": "440010",
    "宮崎県 宮崎市": "450010",
    "鹿児島県 鹿児島市": "460010",
    "沖縄県 那覇市": "471010"
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

@bot.tree.command(name="set_city", description="自分のデフォルトの地域を設定します")
@app_commands.describe(prefecture="都道府県名（例: 東京都）", city="市区町村名（例: 新宿区）")
async def set_city(interaction: discord.Interaction, prefecture: str, city: str):
    key = f"{prefecture} {city}"
    if key not in citycodes:
        await interaction.response.send_message("指定された都道府県・市の組み合わせが見つかりません。", ephemeral=True)
        return

    user_id = str(interaction.user.id)
    if user_id not in user_settings:
        user_settings[user_id] = {"use_location": True, "city_key": key}
    else:
        user_settings[user_id]["city_key"] = key
        
    save_settings(user_settings)
    await interaction.response.send_message(f"あなたの地域を **{prefecture} {city}** に設定しました。（位置情報取得: ON）", ephemeral=True)

@bot.tree.command(name="location_setting", description="登録した地域の自動使用を切り替えます")
@app_commands.choices(flag=[
    app_commands.Choice(name="true", value="true"),
    app_commands.Choice(name="false", value="false")
])
async def location_setting(interaction: discord.Interaction, flag: str):
    use_loc = (flag.lower() == "true")
    user_id = str(interaction.user.id)
    
    if user_id not in user_settings:
        user_settings[user_id] = {"use_location": use_loc, "city_key": None}
    else:
        user_settings[user_id]["use_location"] = use_loc

    save_settings(user_settings)
    status_text = "有効 (true)" if use_loc else "無効 (false)"
    await interaction.response.send_message(f"位置情報（登録地域）の自動取得を **{status_text}** にしました。", ephemeral=True)

@bot.tree.command(name="tenki", description="指定した県と市の天気を確認します")
@app_commands.describe(prefecture="都道府県名（省略時は登録地域を使用）", city="市区町村名（省略時は登録地域を使用）")
async def tenki(interaction: discord.Interaction, prefecture: str = None, city: str = None):
    user_id = str(interaction.user.id)
    setting = user_settings.get(user_id, {"use_location": False, "city_key": None})

    target_key = None
    if not prefecture or not city:
        if setting.get("use_location") and setting.get("city_key"):
            target_key = setting["city_key"]
        else:
            await interaction.response.send_message(
                "都道府県と市を両方指定してください。\n例: `/tenki prefecture:東京都 city:新宿区`", 
                ephemeral=True
            )
            return
    else:
        target_key = f"{prefecture} {city}"

    if target_key in citycodes:
        citycode = citycodes[target_key]
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
        await interaction.response.send_message("指定された地域の天気は見つかりませんでした。", ephemeral=True)

TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)
