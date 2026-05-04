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
STARTUP_CHANNEL_ID = 1453095781790646393
MA_COLOR = 0xE74C3C

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

# ─────────────────────────────────────────
#          WELCOME SYSTEM
# ─────────────────────────────────────────

def create_welcome_image(member):
    try:
        response = requests.get(BANNER_URL, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        banner = Image.open(BytesIO(response.content)).convert("RGBA")
        banner = banner.resize((1280, 640))
        CIRCLE_CENTER_X = 644
        CIRCLE_CENTER_Y = 216
        AVATAR_SIZE = 195
        avatar_url = str(member.display_avatar.with_size(512).url)
        avatar_response = requests.get(avatar_url, timeout=10)
        avatar = Image.open(BytesIO(avatar_response.content)).convert("RGBA")
        avatar = avatar.resize((AVATAR_SIZE, AVATAR_SIZE))
        mask = Image.new("L", (AVATAR_SIZE, AVATAR_SIZE), 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.ellipse((0, 0, AVATAR_SIZE, AVATAR_SIZE), fill=255)
        avatar.putalpha(mask)
        paste_x = CIRCLE_CENTER_X - AVATAR_SIZE // 2
        paste_y = CIRCLE_CENTER_Y - AVATAR_SIZE // 2
        banner.paste(avatar, (paste_x, paste_y), avatar)
        output = BytesIO()
        banner.save(output, format="PNG")
        output.seek(0)
        return output
    except Exception as e:
        print(f"Error creating image: {e}")
        return None

async def send_welcome(channel, member):
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

# ─────────────────────────────────────────
#        STARTUP ROOM — CONTENT
# ─────────────────────────────────────────

NOTIFICATION_ROLES = [
    "Server Notifications",
    "Ajr Notifications",
    "Events Notifications",
    "Games Notifications",
]

INFO_PAGES = [
    {
        "title": "📌 ما هو روم ستارت اب؟",
        "description": (
            "روم **ستارت اب** هو المكان الذي يجمع أصحاب الأفكار والمشاريع في مجتمع **MA**.\n\n"
            "سواء كانت فكرتك في بدايتها أو مشروع يبحث عن شريك أو دعم — هذا هو مكانك الصح!\n\n"
            "نؤمن في **MA** أن كل فكرة تستحق أن تُسمع وتُبنى. 💡\n\n"
            "انضم إلينا وكن جزءاً من جيل الرواد القادم. 🚀"
        )
    },
    {
        "title": "🚀 كيف تنشر فكرتك؟",
        "description": (
            "**الخطوات بكل بساطة:**\n\n"
            "**1️⃣** اضغط على زر **🚀 تقديم فكرة** في الرسالة الرئيسية\n"
            "**2️⃣** أكمل النموذج بمعلومات مشروعك بدقة\n"
            "**3️⃣** سيتم نشر فكرتك في الروم للجميع بشكل أنيق\n"
            "**4️⃣** تفاعل مع الأعضاء وانتظر الردود والاقتراحات\n\n"
            "💡 **نصيحة:** كلما كان وصفك أوضح وأكثر تفصيلاً، كلما كانت الاستجابة أفضل!"
        )
    },
    {
        "title": "📋 شروط النشر",
        "description": (
            "لضمان بيئة منظمة وإيجابية للجميع:\n\n"
            "✅ الفكرة لازم تكون **قابلة للتطبيق** وحقيقية\n"
            "✅ لا أفكار تخالف **قوانين السيرفر أو المجتمع**\n"
            "✅ كل عضو له حق نشر فكرة **مرة كل 48 ساعة**\n"
            "✅ الإدارة تحتفظ بحق **حذف أي محتوى مخالف**\n\n"
            "❌ ممنوع نسخ أفكار الآخرين أو ادعاءها\n"
            "❌ ممنوع الإعلانات التجارية المباشرة\n"
            "❌ ممنوع نشر الفكرة خارج النموذج المخصص"
        )
    }
]

RULES_TEXT = (
    "**1️⃣ الاحترام المتبادل**\n"
    "احترم أفكار الآخرين حتى لو ما تعجبك — كل فكرة وراءها شخص بذل جهداً وحلماً.\n\n"
    "**2️⃣ الأصالة**\n"
    "الفكرة اللي تنشرها لازم تكون **فكرتك أنت**. السرقة الفكرية ممنوعة بالكامل.\n\n"
    "**3️⃣ النقد البنّاء فقط**\n"
    "عندك ملاحظة؟ قولها باحترام وبطريقة مفيدة. الهجوم الشخصي والانتقاد السلبي ممنوع.\n\n"
    "**4️⃣ التنظيم في النشر**\n"
    "استخدم زر **🚀 تقديم فكرة** فقط لنشر مشروعك. التعليقات العشوائية خارج السياق ممنوعة.\n\n"
    "**5️⃣ الخصوصية**\n"
    "لا تشارك معلومات خاصة بأشخاص آخرين بدون إذنهم الصريح.\n\n"
    "**6️⃣ ممنوع التسويق المباشر**\n"
    "لا إعلانات أو ترويج تجاري بدون إذن مسبق من الإدارة.\n\n"
    "**7️⃣ الملكية الفكرية**\n"
    "كل فكرة تُنشر هنا تبقى **ملك صاحبها** ولا يحق لأحد استخدامها تجارياً بدون إذن."
)

# ─────────────────────────────────────────
#        STARTUP ROOM — HELPERS
# ─────────────────────────────────────────

def get_info_embed(page: int) -> discord.Embed:
    info = INFO_PAGES[page]
    embed = discord.Embed(
        title=info["title"],
        description=info["description"],
        color=MA_COLOR
    )
    embed.set_footer(text=f"MA Server • الصفحة {page + 1} من {len(INFO_PAGES)}")
    return embed

def get_main_embed() -> discord.Embed:
    embed = discord.Embed(
        title="🚀 أهلاً بك في روم المشاريع | MA",
        description=(
            "هذا الروم مخصص لأصحاب الأفكار والمشاريع الطموحة في مجتمع **MA**.\n\n"
            "هنا تجد بيئة داعمة لبناء مشاريعك والتواصل مع من يشاركك طموحاتك.\n\n"
            "**استخدم الأزرار أدناه:**\n\n"
            "📋 **القوانين** — اعرف قواعد الروم\n"
            "ℹ️ **المعلومات** — كل ما تحتاج معرفته\n"
            "🔔 **الإشعارات** — اختر إشعاراتك\n"
            "🚀 **تقديم فكرة** — شارك مشروعك مع الجميع"
        ),
        color=MA_COLOR
    )
    embed.set_footer(text="MA Server • كن الإلهام للآخرين ✨")
    return embed

def get_roles_embed(note: str = "") -> discord.Embed:
    desc = (
        "اختر الإشعارات التي تريد استقبالها من سيرفر **MA**.\n\n"
        "🔄 اضغط على الزر مرة ثانية لإلغاء الرتبة."
    )
    if note:
        desc += f"\n\n{note}"
    embed = discord.Embed(
        title="🔔 رتب الإشعارات | MA",
        description=desc,
        color=MA_COLOR
    )
    embed.set_footer(text="MA Server • يمكنك تغيير اختياراتك في أي وقت")
    return embed

# ─────────────────────────────────────────
#        STARTUP ROOM — MODAL
# ─────────────────────────────────────────

class IdeaModal(discord.ui.Modal, title="🚀 تقديم فكرة مشروع"):
    project_name = discord.ui.TextInput(
        label="اسم المشروع",
        placeholder="مثال: تطبيق توصيل، متجر إلكتروني...",
        max_length=100,
        required=True
    )
    description = discord.ui.TextInput(
        label="وصف الفكرة",
        placeholder="اشرح فكرتك بشكل مختصر وواضح...",
        style=discord.TextStyle.paragraph,
        max_length=500,
        required=True
    )
    needed = discord.ui.TextInput(
        label="ماذا تحتاج؟",
        placeholder="مثال: شريك، مطور، مصمم، تمويل...",
        max_length=200,
        required=True
    )
    contact = discord.ui.TextInput(
        label="طريقة التواصل",
        placeholder="مثال: راسلني على الخاص، ديسكورد: username...",
        max_length=100,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        channel = bot.get_channel(STARTUP_CHANNEL_ID)
        embed = discord.Embed(
            title=f"💡 فكرة جديدة: {self.project_name.value}",
            color=MA_COLOR
        )
        embed.add_field(name="📝 الوصف", value=self.description.value, inline=False)
        embed.add_field(name="🤝 يحتاج", value=self.needed.value, inline=True)
        embed.add_field(name="📬 التواصل", value=self.contact.value, inline=True)
        embed.set_footer(
            text=f"مقدم من {interaction.user.display_name} • MA Server",
            icon_url=interaction.user.display_avatar.url
        )
        embed.timestamp = discord.utils.utcnow()
        await channel.send(embed=embed)
        await interaction.response.send_message("✅ تم نشر فكرتك بنجاح في الروم! 🚀", ephemeral=True)

# ─────────────────────────────────────────
#        STARTUP ROOM — VIEWS
# ─────────────────────────────────────────

class InfoNavView(discord.ui.View):
    def __init__(self, page: int):
        super().__init__(timeout=300)
        self.page = page
        self.prev_btn.disabled = (page == 0)
        self.next_btn.disabled = (page == len(INFO_PAGES) - 1)
        self.page_indicator.label = f"{page + 1} / {len(INFO_PAGES)}"

    @discord.ui.button(label="◀️", style=discord.ButtonStyle.secondary)
    async def prev_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        new_page = self.page - 1
        await interaction.response.edit_message(embed=get_info_embed(new_page), view=InfoNavView(new_page))

    @discord.ui.button(label="1 / 3", style=discord.ButtonStyle.gray, disabled=True)
    async def page_indicator(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass

    @discord.ui.button(label="▶️", style=discord.ButtonStyle.primary)
    async def next_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        new_page = self.page + 1
        await interaction.response.edit_message(embed=get_info_embed(new_page), view=InfoNavView(new_page))


class RolesView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

    async def _toggle(self, interaction: discord.Interaction, role_name: str):
        role = discord.utils.get(interaction.guild.roles, name=role_name)
        if role is None:
            await interaction.response.edit_message(
                embed=get_roles_embed(f"❌ الرتبة **{role_name}** غير موجودة! تواصل مع الإدارة."),
                view=self
            )
            return
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            note = f"🔕 تم إزالة رتبة **{role_name}**"
        else:
            await interaction.user.add_roles(role)
            note = f"🔔 تم إضافة رتبة **{role_name}**"
        await interaction.response.edit_message(embed=get_roles_embed(note), view=self)

    @discord.ui.button(label="🔔 Server Notifications", style=discord.ButtonStyle.secondary, row=0)
    async def server_notif(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._toggle(interaction, "Server Notifications")

    @discord.ui.button(label="💼 Ajr Notifications", style=discord.ButtonStyle.secondary, row=0)
    async def ajr_notif(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._toggle(interaction, "Ajr Notifications")

    @discord.ui.button(label="🎉 Events Notifications", style=discord.ButtonStyle.secondary, row=1)
    async def events_notif(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._toggle(interaction, "Events Notifications")

    @discord.ui.button(label="🎮 Games Notifications", style=discord.ButtonStyle.secondary, row=1)
    async def games_notif(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._toggle(interaction, "Games Notifications")

    @discord.ui.button(label="✅ أضف كل الرتب", style=discord.ButtonStyle.success, row=2)
    async def add_all(self, interaction: discord.Interaction, button: discord.ui.Button):
        roles = [discord.utils.get(interaction.guild.roles, name=r) for r in NOTIFICATION_ROLES]
        roles = [r for r in roles if r]
        if roles:
            await interaction.user.add_roles(*roles)
        await interaction.response.edit_message(
            embed=get_roles_embed("✅ تم إضافة جميع رتب الإشعارات!"), view=self
        )

    @discord.ui.button(label="❌ احذف كل الرتب", style=discord.ButtonStyle.danger, row=2)
    async def remove_all(self, interaction: discord.Interaction, button: discord.ui.Button):
        roles = [discord.utils.get(interaction.guild.roles, name=r) for r in NOTIFICATION_ROLES]
        roles = [r for r in roles if r]
        if roles:
            await interaction.user.remove_roles(*roles)
        await interaction.response.edit_message(
            embed=get_roles_embed("✅ تم إزالة جميع رتب الإشعارات!"), view=self
        )


class StartupMainView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📋 القوانين", style=discord.ButtonStyle.danger, custom_id="ma_startup_rules_v1")
    async def rules_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="📋 قوانين روم ستارت اب | MA",
            description=RULES_TEXT,
            color=MA_COLOR
        )
        embed.set_footer(text="MA Server • يرجى الالتزام بالقوانين لبيئة أفضل للجميع")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="ℹ️ المعلومات", style=discord.ButtonStyle.primary, custom_id="ma_startup_info_v1")
    async def info_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(embed=get_info_embed(0), view=InfoNavView(0), ephemeral=True)

    @discord.ui.button(label="🔔 الإشعارات", style=discord.ButtonStyle.secondary, custom_id="ma_startup_roles_v1")
    async def roles_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(embed=get_roles_embed(), view=RolesView(), ephemeral=True)

    @discord.ui.button(label="🚀 تقديم فكرة", style=discord.ButtonStyle.success, custom_id="ma_startup_idea_v1")
    async def idea_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(IdeaModal())

# ─────────────────────────────────────────
#        BOT EVENTS & COMMANDS
# ─────────────────────────────────────────

@bot.event
async def on_ready():
    bot.add_view(StartupMainView())
    guild = discord.Object(id=GUILD_ID)
    bot.tree.copy_global_to(guild=guild)
    await bot.tree.sync(guild=guild)
    print(f"Bot ready: {bot.user}")
    print("Commands synced!")

@bot.tree.command(name="setwelcome", description="اختر قناة الترحيب للأعضاء الجدد")
@app_commands.describe(channel="اختر القناة التي تريد إرسال رسائل الترحيب فيها")
@app_commands.checks.has_permissions(administrator=True)
async def setwelcome(interaction: discord.Interaction, channel: discord.TextChannel):
    config = load_config()
    guild_id = str(interaction.guild_id)
    config[guild_id] = {"welcome_channel": channel.id}
    save_config(config)
    await interaction.response.send_message(
        f"✅ تم تعيين قناة الترحيب إلى {channel.mention}!", ephemeral=True
    )

@bot.tree.command(name="testwelcome", description="اختبر رسالة الترحيب على نفسك")
@app_commands.checks.has_permissions(administrator=True)
async def testwelcome(interaction: discord.Interaction):
    config = load_config()
    guild_id = str(interaction.guild_id)
    if guild_id not in config or "welcome_channel" not in config[guild_id]:
        await interaction.response.send_message(
            "❌ ما تم تعيين قناة ترحيب بعد! استخدم `/setwelcome` أولاً.", ephemeral=True
        )
        return
    await interaction.response.send_message("⏳ جاري إرسال رسالة الاختبار...", ephemeral=True)
    channel_id = config[guild_id]["welcome_channel"]
    channel = bot.get_channel(channel_id)
    if channel is None:
        await interaction.followup.send("❌ ما أقدر أوصل للقناة!", ephemeral=True)
        return
    try:
        await send_welcome(channel, interaction.user)
    except Exception as e:
        await interaction.followup.send(f"❌ حصل خطأ: {e}", ephemeral=True)

@bot.tree.command(name="setup_startup", description="إرسال لوحة روم ستارت اب")
@app_commands.checks.has_permissions(administrator=True)
async def setup_startup(interaction: discord.Interaction):
    channel = bot.get_channel(STARTUP_CHANNEL_ID)
    if channel is None:
        await interaction.response.send_message("❌ ما أقدر أوصل لروم ستارت اب!", ephemeral=True)
        return
    await channel.send(embed=get_main_embed(), view=StartupMainView())
    await interaction.response.send_message("✅ تم إرسال لوحة ستارت اب!", ephemeral=True)

@bot.event
async def on_member_join(member):
    print(f"New member: {member.name}")
    try:
        config = load_config()
        guild_id = str(member.guild.id)
        if guild_id not in config or "welcome_channel" not in config[guild_id]:
            return
        channel_id = config[guild_id]["welcome_channel"]
        channel = bot.get_channel(channel_id)
        if channel is None:
            return
        await send_welcome(channel, member)
    except Exception as e:
        print(f"Error in on_member_join: {e}")

bot.run(TOKEN)
