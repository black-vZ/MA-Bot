import discord
from discord import app_commands
from discord.ext import commands
from PIL import Image, ImageDraw
import requests
from io import BytesIO
import os
import json

TOKEN = os.environ.get('DISCORD_BOT_TOKEN')
GUILD_ID = 1451263550948376608
BANNER_URL = "https://i.imgur.com/d7pvLfI.png"
CONFIG_FILE = "bot/config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f)

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

def create_welcome_image(member):
    try:
        response = requests.get(BANNER_URL, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        banner = Image.open(BytesIO(response.content)).convert("RGBA")
        banner = banner.resize((1280, 640))

        # مركز الدائرة الحمراء بعد الـ resize هو (644, 216) ونصف القطر 192
        CIRCLE_CENTER_X = 644
        CIRCLE_CENTER_Y = 216
        AVATAR_SIZE = 195  # يظهر الشريط الأحمر في الأطراف

        avatar_url = str(member.display_avatar.with_size(512).url)
        avatar_response = requests.get(avatar_url, timeout=10)
        avatar = Image.open(BytesIO(avatar_response.content)).convert("RGBA")
        avatar = avatar.resize((AVATAR_SIZE, AVATAR_SIZE))

        # قص الأفاتار بشكل دائرة
        mask = Image.new("L", (AVATAR_SIZE, AVATAR_SIZE), 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.ellipse((0, 0, AVATAR_SIZE, AVATAR_SIZE), fill=255)
        avatar.putalpha(mask)

        # لصق الأفاتار في منتصف الدائرة
        paste_x = CIRCLE_CENTER_X - AVATAR_SIZE // 2
        paste_y = CIRCLE_CENTER_Y - AVATAR_SIZE // 2
        banner.paste(avatar, (paste_x, paste_y), avatar)

        output = BytesIO()
        banner.save(output, format="PNG")
        output.seek(0)
        return output
    except Exception as e:
        print(f"❌ خطأ في إنشاء الصورة: {e}")
        return None

async def send_welcome(channel, member):
    member_count = member.guild.member_count
    welcome_text = (
        f"✨ أهلاً فيك بين أهلك!\n"
        f"نورت سيرفر MA 🤍 لا تنسى تقرأ القوانين وتعرّف بنفسك {member.mention} 😉\n"
        f"يُرجى منك إلقاء نظرة على <#1453109203672498310> <#1453095781790646393> "
        f"لكي تعرف كل شيء يخص السيرفر"
    )
    image = create_welcome_image(member)
    if image:
        file = discord.File(fp=image, filename="welcome.png")
        await channel.send(content=welcome_text, file=file)
    else:
        await channel.send(content=welcome_text)

@bot.event
async def on_ready():
    guild = discord.Object(id=GUILD_ID)
    bot.tree.copy_global_to(guild=guild)
    await bot.tree.sync(guild=guild)
    print(f"✅ البوت شغال: {bot.user}")
    print("✅ تم مزامنة الأوامر على السيرفر!")

@bot.tree.command(name="setwelcome", description="اختر قناة الترحيب للأعضاء الجدد")
@app_commands.describe(channel="اختر القناة التي تريد إرسال رسائل الترحيب فيها")
@app_commands.checks.has_permissions(administrator=True)
async def setwelcome(interaction: discord.Interaction, channel: discord.TextChannel):
    config = load_config()
    guild_id = str(interaction.guild_id)
    config[guild_id] = {"welcome_channel": channel.id}
    save_config(config)
    await interaction.response.send_message(
        f"✅ تم تعيين قناة الترحيب إلى {channel.mention}!",
        ephemeral=True
    )

@bot.tree.command(name="testwelcome", description="اختبر رسالة الترحيب على نفسك")
@app_commands.checks.has_permissions(administrator=True)
async def testwelcome(interaction: discord.Interaction):
    config = load_config()
    guild_id = str(interaction.guild_id)
    if guild_id not in config or "welcome_channel" not in config[guild_id]:
        await interaction.response.send_message(
            "❌ ما تم تعيين قناة ترحيب بعد! استخدم `/setwelcome` أولاً.",
            ephemeral=True
        )
        return
    await interaction.response.send_message("⏳ جاري إرسال رسالة الاختبار...", ephemeral=True)
    channel_id = config[guild_id]["welcome_channel"]
    channel = bot.get_channel(channel_id)
    if channel is None:
        await interaction.followup.send("❌ ما أقدر أوصل للقناة! تأكد أن للبوت صلاحية القراءة والكتابة فيها.", ephemeral=True)
        return
    try:
        await send_welcome(channel, interaction.user)
        print(f"✅ تم إرسال رسالة اختبار في #{channel.name}")
    except Exception as e:
        print(f"❌ خطأ في إرسال رسالة الاختبار: {e}")
        await interaction.followup.send(f"❌ حصل خطأ: {e}", ephemeral=True)

@bot.event
async def on_member_join(member):
    print(f"👤 عضو جديد انضم: {member.name}")
    try:
        config = load_config()
        guild_id = str(member.guild.id)
        if guild_id not in config or "welcome_channel" not in config[guild_id]:
            print("❌ ما في قناة ترحيب محددة")
            return
        channel_id = config[guild_id]["welcome_channel"]
        channel = bot.get_channel(channel_id)
        if channel is None:
            print(f"❌ ما أقدر أوصل للقناة: {channel_id}")
            return
        await send_welcome(channel, member)
        print(f"✅ تم إرسال رسالة الترحيب في #{channel.name}")
    except Exception as e:
        print(f"❌ خطأ في on_member_join: {e}")

bot.run(TOKEN)
