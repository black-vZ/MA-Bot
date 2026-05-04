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
APPS_CHANNEL_ID = 0  # سيتم تحديثه لاحقاً بـ ايدي روم التقديمات
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
#          WELCOME IMAGE SYSTEM
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
#       START-UP ROOM — CONTENT
# ─────────────────────────────────────────

NOTIFICATION_ROLES = [
    "Server Notifications",
    "Ajr Notifications",
    "Events Notifications",
    "Games Notifications",
]

RULES_TEXT = (
    "**1️⃣ الاحترام المتبادل**\n"
    "يُلزم جميع الأعضاء باحترام بعضهم البعض بغض النظر عن الاختلافات. أي شكل من أشكال الإهانة أو الاستفزاز ممنوع.\n\n"
    "**2️⃣ ممنوع التعدي على الآخرين**\n"
    "يُمنع التحرش، والتنمر، والعنصرية، وأي سلوك يُسبب الأذى لأعضاء السيرفر.\n\n"
    "**3️⃣ المحتوى المناسب فقط**\n"
    "يُمنع نشر أي محتوى مسيء أو للبالغين أو مخالف لشروط خدمة Discord.\n\n"
    "**4️⃣ ممنوع السبام والفلود**\n"
    "يُمنع إرسال رسائل متكررة أو رموز تعبيرية مفرطة أو صور عشوائية خارج السياق.\n\n"
    "**5️⃣ ممنوع الإعلانات**\n"
    "يُمنع الترويج لأي سيرفر أو موقع أو منتج بدون إذن مسبق من الإدارة.\n\n"
    "**6️⃣ احترام الأدوار والمهام**\n"
    "يُرجى استخدام كل قناة للغرض المخصصة له، والتقيد بتوجيهات الطاقم الإداري.\n\n"
    "**7️⃣ الخصوصية والأمان**\n"
    "يُمنع مشاركة معلومات خاصة بالآخرين أو نشر روابط مشبوهة داخل السيرفر.\n\n"
    "**8️⃣ الامتثال لشروط Discord**\n"
    "يجب على جميع الأعضاء الالتزام بـ [شروط خدمة Discord](https://discord.com/terms) و[إرشادات المجتمع](https://discord.com/guidelines)."
)

INFO_PAGES = [
    {
        "title": "🌟 مرحباً بك في سيرفر MA!",
        "description": (
            "يسعدنا انضمامك إلى مجتمع **MA** — المكان الذي نجمع فيه أشخاصاً طموحين من كل مكان.\n\n"
            "سيرفرنا بُني على أساس الاحترام والمتعة والنمو المشترك، ونسعى دائماً لتقديم تجربة مميزة لكل عضو.\n\n"
            "هذه الصفحات ستعرّفك على كل ما تحتاج معرفته للبدء. 👇"
        )
    },
    {
        "title": "📂 أقسام السيرفر",
        "description": (
            "**📣 الإعلانات** — أخبار ومستجدات السيرفر الرسمية\n\n"
            "**💬 الدردشة العامة** — تحدث مع الأعضاء بحرية\n\n"
            "**🚀 ستارت اب** — تعرّف على السيرفر وابدأ رحلتك\n\n"
            "**💼 روم الأجر** — فرص العمل والمشاريع المدفوعة\n\n"
            "**🎉 الفعاليات** — مسابقات وأنشطة ترفيهية\n\n"
            "**🎮 الألعاب** — غرف للعب والمتعة مع الأعضاء"
        )
    },
    {
        "title": "🎭 نظام الرتب",
        "description": (
            "يعتمد سيرفر **MA** نظام رتب متدرجاً بناءً على نشاطك ومشاركتك:\n\n"
            "**👋 عضو جديد** — عند الانضمام\n"
            "**✅ عضو** — بعد قراءة القوانين والتفاعل\n"
            "**⭐ عضو نشيط** — بالتفاعل المستمر\n"
            "**💎 عضو مميز** — للأعضاء الأوفياء\n\n"
            "**🛡️ رتب الطاقم:**\n"
            "مشرف • مدير • مؤسس\n\n"
            "للحصول على رتبة الطاقم، استخدم زر **التقديم** في هذا الروم."
        )
    },
    {
        "title": "🎉 الفعاليات والمزايا",
        "description": (
            "في سيرفر **MA** تجد الكثير من الأنشطة:\n\n"
            "🏆 **مسابقات دورية** مع جوائز حقيقية\n\n"
            "🎁 **قيف أواي** منتظمة للأعضاء النشيطين\n\n"
            "🤝 **فرص عمل وتعاون** في روم الأجر\n\n"
            "🎮 **جلسات ألعاب جماعية** مع الأعضاء\n\n"
            "📢 **أحداث خاصة** يُعلن عنها في قناة الإعلانات\n\n"
            "تابع **🔔 الإشعارات** لتكون أول من يعلم بكل جديد!"
        )
    },
    {
        "title": "📌 نصائح للبداية الصحيحة",
        "description": (
            "إليك أهم الخطوات للاندماج في مجتمع **MA**:\n\n"
            "**1️⃣** اقرأ **القوانين** بعناية للالتزام بها\n"
            "**2️⃣** اختر **رتب الإشعارات** المناسبة لك\n"
            "**3️⃣** عرّف بنفسك في قناة المقدمات\n"
            "**4️⃣** تفاعل مع الأعضاء وكن جزءاً من المجتمع\n"
            "**5️⃣** إذا أردت الانضمام للطاقم، استخدم زر **التقديم**\n\n"
            "لو عندك أي سؤال، تواصل مع أي عضو من الطاقم بكل ترحيب! 🤍"
        )
    }
]

APPLY_TERMS = (
    "قبل أن تتقدم، يرجى قراءة الشروط بعناية:\n\n"
    "✅ يجب أن تكون عضواً نشطاً في السيرفر\n"
    "✅ يجب أن يكون عمرك **+15 سنة** على الأقل\n"
    "✅ يجب أن تكون متاحاً بشكل منتظم\n"
    "✅ الصدق التام في الإجابة على جميع الأسئلة\n\n"
    "❌ في حال رفض طلبك لن نُخبرك بالسبب\n"
    "❌ عدم قبولك لا يعني عدم تقديرنا لك\n"
    "❌ لا تتقدم إذا لم تكن جاداً\n\n"
    "**بالضغط على 'أوافق على الشروط' فأنت تؤكد قراءتك وموافقتك على جميع ما سبق.**"
)

# ─────────────────────────────────────────
#       START-UP ROOM — MODALS
# ─────────────────────────────────────────

class StaffApplyModal(discord.ui.Modal, title="📝 تقديم للطاقم الإداري"):
    q1 = discord.ui.TextInput(label="ما اسمك وكم عمرك؟", placeholder="الاسم والعمر...", max_length=100)
    q2 = discord.ui.TextInput(label="لماذا تريد الانضمام للطاقم؟", style=discord.TextStyle.paragraph, max_length=400)
    q3 = discord.ui.TextInput(label="ما خبرتك في الإدارة؟", style=discord.TextStyle.paragraph, max_length=400)
    q4 = discord.ui.TextInput(label="كم ساعة يومياً تستطيع التواجد؟", max_length=100)

    async def on_submit(self, interaction: discord.Interaction):
        await send_application(interaction, "🛡️ تقديم للطاقم الإداري", [
            ("الاسم والعمر", self.q1.value),
            ("سبب الانضمام", self.q2.value),
            ("الخبرة في الإدارة", self.q3.value),
            ("ساعات التواجد", self.q4.value),
        ])

class EventApplyModal(discord.ui.Modal, title="📝 تقديم لفريق الفعاليات"):
    q1 = discord.ui.TextInput(label="ما اسمك وكم عمرك؟", placeholder="الاسم والعمر...", max_length=100)
    q2 = discord.ui.TextInput(label="ما نوع الفعاليات التي تستطيع تنظيمها؟", style=discord.TextStyle.paragraph, max_length=400)
    q3 = discord.ui.TextInput(label="هل لديك خبرة سابقة في تنظيم الفعاليات؟", style=discord.TextStyle.paragraph, max_length=400)
    q4 = discord.ui.TextInput(label="ما الذي يميزك عن غيرك؟", style=discord.TextStyle.paragraph, max_length=300)

    async def on_submit(self, interaction: discord.Interaction):
        await send_application(interaction, "🎉 تقديم لفريق الفعاليات", [
            ("الاسم والعمر", self.q1.value),
            ("أنواع الفعاليات", self.q2.value),
            ("الخبرة السابقة", self.q3.value),
            ("ما يميزه", self.q4.value),
        ])

class ModApplyModal(discord.ui.Modal, title="📝 تقديم للإشراف"):
    q1 = discord.ui.TextInput(label="ما اسمك وكم عمرك؟", placeholder="الاسم والعمر...", max_length=100)
    q2 = discord.ui.TextInput(label="لماذا تريد أن تكون مشرفاً؟", style=discord.TextStyle.paragraph, max_length=400)
    q3 = discord.ui.TextInput(label="كيف تتعامل مع الأعضاء المخالفين؟", style=discord.TextStyle.paragraph, max_length=400)
    q4 = discord.ui.TextInput(label="كم ساعة يومياً أنت متاح؟", max_length=100)

    async def on_submit(self, interaction: discord.Interaction):
        await send_application(interaction, "🔨 تقديم للإشراف", [
            ("الاسم والعمر", self.q1.value),
            ("سبب الرغبة في الإشراف", self.q2.value),
            ("التعامل مع المخالفين", self.q3.value),
            ("ساعات التواجد", self.q4.value),
        ])

async def send_application(interaction: discord.Interaction, title: str, fields: list):
    config = load_config()
    apps_channel_id = config.get("apps_channel", APPS_CHANNEL_ID)
    channel = bot.get_channel(int(apps_channel_id)) if apps_channel_id else None

    embed = discord.Embed(title=title, color=MA_COLOR)
    for name, value in fields:
        embed.add_field(name=name, value=value or "—", inline=False)
    embed.set_footer(
        text=f"مقدم من {interaction.user.display_name} ({interaction.user.id}) • MA Server",
        icon_url=interaction.user.display_avatar.url
    )
    embed.timestamp = discord.utils.utcnow()

    if channel:
        await channel.send(embed=embed)
        await interaction.response.send_message(
            "✅ تم إرسال تقديمك بنجاح! سنتواصل معك قريباً. 🤍", ephemeral=True
        )
    else:
        await interaction.response.send_message(
            "✅ تم استلام تقديمك! سنتواصل معك قريباً. 🤍\n"
            "*(ملاحظة للإدارة: لم يتم تعيين روم التقديمات بعد — استخدم `/setapps`)*",
            ephemeral=True
        )

# ─────────────────────────────────────────
#       START-UP ROOM — VIEWS
# ─────────────────────────────────────────

def get_info_embed(page: int) -> discord.Embed:
    info = INFO_PAGES[page]
    embed = discord.Embed(title=info["title"], description=info["description"], color=MA_COLOR)
    embed.set_footer(text=f"MA Server • الصفحة {page + 1} من {len(INFO_PAGES)}")
    return embed

def get_main_embed() -> discord.Embed:
    embed = discord.Embed(
        title="🌟 أهلاً وسهلاً في سيرفر MA!",
        description=(
            "يسعدنا انضمامك! هذا الروم سيعرّفك على كل شيء تحتاج معرفته.\n\n"
            "استخدم الأزرار أدناه للتنقل:\n\n"
            "📋 **قوانين السيرفر** — اقرأها قبل أي شيء\n"
            "ℹ️ **معلومات السيرفر** — تعرّف على أقسامنا ونظامنا\n"
            "🔔 **الإشعارات** — اختر ما تريد استقباله\n"
            "📝 **التقديم** — انضم لطاقم MA"
        ),
        color=MA_COLOR
    )
    embed.set_footer(text="MA Server • رحلة سعيدة معنا 🤍")
    return embed

def get_roles_embed(note: str = "") -> discord.Embed:
    desc = (
        "اختر الإشعارات التي تريد استقبالها من سيرفر **MA**.\n\n"
        "🔄 اضغط على الزر مرة ثانية لإلغاء الرتبة."
    )
    if note:
        desc += f"\n\n{note}"
    embed = discord.Embed(title="🔔 رتب الإشعارات | MA", description=desc, color=MA_COLOR)
    embed.set_footer(text="MA Server • يمكنك تغيير اختياراتك في أي وقت")
    return embed


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

    @discord.ui.button(label="1 / 5", style=discord.ButtonStyle.gray, disabled=True)
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
                embed=get_roles_embed(f"❌ الرتبة **{role_name}** غير موجودة! تواصل مع الإدارة."), view=self
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
        await interaction.response.edit_message(embed=get_roles_embed("✅ تم إضافة جميع رتب الإشعارات!"), view=self)

    @discord.ui.button(label="❌ احذف كل الرتب", style=discord.ButtonStyle.danger, row=2)
    async def remove_all(self, interaction: discord.Interaction, button: discord.ui.Button):
        roles = [discord.utils.get(interaction.guild.roles, name=r) for r in NOTIFICATION_ROLES]
        roles = [r for r in roles if r]
        if roles:
            await interaction.user.remove_roles(*roles)
        await interaction.response.edit_message(embed=get_roles_embed("✅ تم إزالة جميع رتب الإشعارات!"), view=self)


class ApplyTypeView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(label="🛡️ طاقم إداري", style=discord.ButtonStyle.primary, row=0)
    async def staff_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="📋 شروط التقديم للطاقم الإداري", description=APPLY_TERMS, color=MA_COLOR)
        embed.set_footer(text="MA Server • اقرأ الشروط بعناية قبل التقديم")
        await interaction.response.edit_message(embed=embed, view=ApplyTermsView("staff"))

    @discord.ui.button(label="🎉 فريق الفعاليات", style=discord.ButtonStyle.success, row=0)
    async def event_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="📋 شروط التقديم لفريق الفعاليات", description=APPLY_TERMS, color=MA_COLOR)
        embed.set_footer(text="MA Server • اقرأ الشروط بعناية قبل التقديم")
        await interaction.response.edit_message(embed=embed, view=ApplyTermsView("event"))

    @discord.ui.button(label="🔨 إشراف", style=discord.ButtonStyle.secondary, row=0)
    async def mod_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="📋 شروط التقديم للإشراف", description=APPLY_TERMS, color=MA_COLOR)
        embed.set_footer(text="MA Server • اقرأ الشروط بعناية قبل التقديم")
        await interaction.response.edit_message(embed=embed, view=ApplyTermsView("mod"))


class ApplyTermsView(discord.ui.View):
    def __init__(self, apply_type: str):
        super().__init__(timeout=300)
        self.apply_type = apply_type

    @discord.ui.button(label="✅ أوافق على الشروط", style=discord.ButtonStyle.success)
    async def agree_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.apply_type == "staff":
            await interaction.response.send_modal(StaffApplyModal())
        elif self.apply_type == "event":
            await interaction.response.send_modal(EventApplyModal())
        elif self.apply_type == "mod":
            await interaction.response.send_modal(ModApplyModal())

    @discord.ui.button(label="◀️ رجوع", style=discord.ButtonStyle.secondary)
    async def back_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="📝 التقديم في سيرفر MA",
            description=(
                "أهلاً بك في قسم التقديمات!\n\n"
                "اختر الوظيفة التي تريد التقديم عليها:\n\n"
                "🛡️ **طاقم إداري** — إدارة السيرفر والإشراف العام\n"
                "🎉 **فريق الفعاليات** — تنظيم وإدارة فعاليات السيرفر\n"
                "🔨 **إشراف** — الإشراف على المحادثات وتطبيق القوانين"
            ),
            color=MA_COLOR
        )
        await interaction.response.edit_message(embed=embed, view=ApplyTypeView())


class StartupMainView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📋 قوانين السيرفر", style=discord.ButtonStyle.danger, custom_id="ma_main_rules_v2")
    async def rules_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="📋 قوانين سيرفر MA",
            description=RULES_TEXT,
            color=MA_COLOR
        )
        embed.set_footer(text="MA Server • الالتزام بالقوانين واجب على الجميع")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="ℹ️ معلومات السيرفر", style=discord.ButtonStyle.primary, custom_id="ma_main_info_v2")
    async def info_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(embed=get_info_embed(0), view=InfoNavView(0), ephemeral=True)

    @discord.ui.button(label="🔔 الإشعارات", style=discord.ButtonStyle.secondary, custom_id="ma_main_roles_v2")
    async def roles_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(embed=get_roles_embed(), view=RolesView(), ephemeral=True)

    @discord.ui.button(label="📝 التقديم", style=discord.ButtonStyle.success, custom_id="ma_main_apply_v2")
    async def apply_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="📝 التقديم في سيرفر MA",
            description=(
                "أهلاً بك في قسم التقديمات!\n\n"
                "اختر الوظيفة التي تريد التقديم عليها:\n\n"
                "🛡️ **طاقم إداري** — إدارة السيرفر والإشراف العام\n"
                "🎉 **فريق الفعاليات** — تنظيم وإدارة فعاليات السيرفر\n"
                "🔨 **إشراف** — الإشراف على المحادثات وتطبيق القوانين"
            ),
            color=MA_COLOR
        )
        await interaction.response.send_message(embed=embed, view=ApplyTypeView(), ephemeral=True)

# ─────────────────────────────────────────
#       BOT EVENTS & COMMANDS
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
    config[str(interaction.guild_id)] = {"welcome_channel": channel.id}
    save_config(config)
    await interaction.response.send_message(f"✅ تم تعيين قناة الترحيب إلى {channel.mention}!", ephemeral=True)

@bot.tree.command(name="testwelcome", description="اختبر رسالة الترحيب على نفسك")
@app_commands.checks.has_permissions(administrator=True)
async def testwelcome(interaction: discord.Interaction):
    config = load_config()
    guild_id = str(interaction.guild_id)
    if guild_id not in config or "welcome_channel" not in config[guild_id]:
        await interaction.response.send_message("❌ استخدم `/setwelcome` أولاً.", ephemeral=True)
        return
    await interaction.response.send_message("⏳ جاري الإرسال...", ephemeral=True)
    channel = bot.get_channel(config[guild_id]["welcome_channel"])
    if channel:
        await send_welcome(channel, interaction.user)

@bot.tree.command(name="setup_startup", description="إرسال لوحة روم ستارت اب")
@app_commands.checks.has_permissions(administrator=True)
async def setup_startup(interaction: discord.Interaction):
    channel = bot.get_channel(STARTUP_CHANNEL_ID)
    if channel is None:
        await interaction.response.send_message("❌ ما أقدر أوصل للروم!", ephemeral=True)
        return
    await channel.send(embed=get_main_embed(), view=StartupMainView())
    await interaction.response.send_message("✅ تم إرسال لوحة ستارت اب!", ephemeral=True)

@bot.tree.command(name="setapps", description="تعيين روم استقبال التقديمات")
@app_commands.describe(channel="الروم الذي تريد إرسال التقديمات إليه")
@app_commands.checks.has_permissions(administrator=True)
async def setapps(interaction: discord.Interaction, channel: discord.TextChannel):
    config = load_config()
    config["apps_channel"] = channel.id
    save_config(config)
    await interaction.response.send_message(f"✅ تم تعيين روم التقديمات إلى {channel.mention}!", ephemeral=True)

@bot.event
async def on_member_join(member):
    print(f"New member: {member.name}")
    try:
        config = load_config()
        guild_id = str(member.guild.id)
        if guild_id not in config or "welcome_channel" not in config[guild_id]:
            return
        channel = bot.get_channel(config[guild_id]["welcome_channel"])
        if channel:
            await send_welcome(channel, member)
    except Exception as e:
        print(f"Error in on_member_join: {e}")

bot.run(TOKEN)
