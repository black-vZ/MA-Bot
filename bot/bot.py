import discord
from discord import app_commands
from discord.ext import commands, tasks
from PIL import Image, ImageDraw
import requests
from io import BytesIO
import os
import json
import random

TOKEN = os.environ.get('DISCORD_BOT_TOKEN')
GUILD_ID = 1451263550948376608
BANNER_URL = "https://i.imgur.com/d7pvLfI.png"
CONFIG_FILE = "bot/config.json"
STARTUP_CHANNEL_ID = 1453095781790646393
AJR_CHANNEL_ID = 1452763016495108297
MA_COLOR = 0xE74C3C
ADMIN_ROLE_ID = 1474442320207417525

AJR_MESSAGES = [
    "قال رسول الله ﷺ: «مَن قال سبحان الله وبحمده في يوم مئة مرة، حُطَّت خطاياه وإن كانت مثل زبد البحر»\n— متفق عليه",
    "قال رسول الله ﷺ: «كلمتان خفيفتان على اللسان، ثقيلتان في الميزان، حبيبتان إلى الرحمن: سبحان الله وبحمده، سبحان الله العظيم»\n— متفق عليه",
    "قال رسول الله ﷺ: «مَن قرأ آية الكرسي دبر كل صلاة مكتوبة لم يمنعه من دخول الجنة إلا أن يموت»\n— صحيح النسائي",
    "قال الله تعالى: ﴿فَاذْكُرُونِي أَذْكُرْكُمْ وَاشْكُرُوا لِي وَلَا تَكْفُرُونِ﴾\n— سورة البقرة: 152",
    "قال رسول الله ﷺ: «مَن صلى على واحدة صلى الله عليه بها عشراً»\n— صحيح مسلم",
    "قال رسول الله ﷺ: «أحب الأعمال إلى الله أدومها وإن قَلَّ»\n— متفق عليه",
    "قال الله تعالى: ﴿إِنَّ اللَّهَ مَعَ الصَّابِرِينَ﴾\n— سورة البقرة: 153",
    "قال رسول الله ﷺ: «مَن قال لا إله إلا الله وحده لا شريك له، له الملك وله الحمد وهو على كل شيء قدير، في يوم مئة مرة، كانت له عدل عشر رقاب»\n— متفق عليه",
    "قال رسول الله ﷺ: «الطهور شطر الإيمان، والحمد لله تملأ الميزان، وسبحان الله والحمد لله تملآن ما بين السماوات والأرض»\n— صحيح مسلم",
    "قال الله تعالى: ﴿وَمَن يَتَّقِ اللَّهَ يَجْعَل لَّهُ مَخْرَجًا ۝ وَيَرْزُقْهُ مِنْ حَيْثُ لَا يَحْتَسِبُ﴾\n— سورة الطلاق: 2-3",
    "قال رسول الله ﷺ: «مَن سلك طريقاً يلتمس فيه علماً سهَّل الله له به طريقاً إلى الجنة»\n— صحيح مسلم",
    "قال رسول الله ﷺ: «إن من أحبكم إليّ وأقربكم مني مجلساً يوم القيامة أحاسنَكم أخلاقاً»\n— صحيح الترمذي",
    "قال الله تعالى: ﴿وَقُل رَّبِّ زِدْنِي عِلْمًا﴾\n— سورة طه: 114",
    "قال رسول الله ﷺ: «أفضل الذكر لا إله إلا الله، وأفضل الدعاء الحمد لله»\n— صحيح الترمذي",
    "قال رسول الله ﷺ: «البر حسن الخلق، والإثم ما حاك في صدرك وكرهت أن يطلع عليه الناس»\n— صحيح مسلم",
    "قال الله تعالى: ﴿وَاللَّهُ يُحِبُّ الصَّابِرِينَ﴾\n— سورة آل عمران: 146",
    "قال رسول الله ﷺ: «ما من مسلم يغرس غرساً أو يزرع زرعاً فيأكل منه طير أو إنسان أو بهيمة إلا كان له به صدقة»\n— متفق عليه",
    "قال رسول الله ﷺ: «لا يؤمن أحدكم حتى يحب لأخيه ما يحب لنفسه»\n— متفق عليه",
    "قال الله تعالى: ﴿إِنَّ مَعَ الْعُسْرِ يُسْرًا﴾\n— سورة الشرح: 6",
    "قال رسول الله ﷺ: «رحم الله رجلاً سمحاً إذا باع وإذا اشترى وإذا اقتضى»\n— صحيح البخاري",
]

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
#        ADMIN STREITER CHECK
# ─────────────────────────────────────────

def is_admin_streiter():
    async def predicate(interaction: discord.Interaction) -> bool:
        role_ids = [r.id for r in interaction.user.roles]
        if ADMIN_ROLE_ID not in role_ids:
            await interaction.response.send_message(
                "ما عندك صلاحية لاستخدام هذا الأمر.", ephemeral=True
            )
            return False
        return True
    return app_commands.check(predicate)

# ─────────────────────────────────────────
#        WELCOME IMAGE SYSTEM
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

RULES_TEXT = (
    "**I. Mutual Respect**\n"
    "All members are required to treat each other with respect. "
    "Insults, provocations, and personal attacks of any kind are strictly prohibited.\n\n"

    "**II. No Harassment**\n"
    "Harassment, bullying, racism, or any behavior that causes harm to other members "
    "will result in an immediate ban.\n\n"

    "**III. Appropriate Content Only**\n"
    "Sharing offensive, adult, or Discord-ToS-violating content is not allowed "
    "in any channel under any circumstances.\n\n"

    "**IV. No Spam or Flooding**\n"
    "Repeated messages, excessive reactions, or sending irrelevant media outside "
    "of designated channels is prohibited.\n\n"

    "**V. No Advertising**\n"
    "Promoting other servers, websites, or products without prior approval from "
    "the administration is not permitted.\n\n"

    "**VI. Channel Discipline**\n"
    "Each channel has a purpose — use it accordingly. "
    "Follow staff instructions at all times.\n\n"

    "**VII. Privacy & Security**\n"
    "Sharing private information about others or posting suspicious links is strictly forbidden.\n\n"

    "**VIII. Discord Guidelines**\n"
    "All members must comply with [Discord Terms of Service](https://discord.com/terms) "
    "and [Community Guidelines](https://discord.com/guidelines)."
)

INFO_PAGES = [
    {
        "title": "Welcome to MA Server",
        "description": (
            "We're glad to have you here.\n\n"
            "**MA** is a community built on respect, ambition, and genuine connection. "
            "Whether you're here to socialize, find opportunities, or be part of something bigger — "
            "you're in the right place.\n\n"
            "Use the pages below to learn everything you need before getting started."
        )
    },
    {
        "title": "Server Sections",
        "description": (
            "**Announcements** — Official server news and updates\n\n"
            "**General Chat** — Open conversations with the community\n\n"
            "**Start-Up** — Server guide for new members\n\n"
            "**Ajr Room** — Job listings and paid collaboration opportunities\n\n"
            "**Events** — Competitions, giveaways, and community activities\n\n"
            "**Voice Channels** — Hang out and talk with members"
        )
    },
    {
        "title": "Staff Hierarchy",
        "description": (
            "**Senior Management**\n"
            "👑 Owner — ⚡️ Co-Owner — 💻 Developer — ⚙️ Over Powered — ⚔️ The Heir — 🔧 Administrator\n\n"
            "**Moderation**\n"
            "🔮 Manager — 🌸 Girl Staff — 💬 Chat Manager — 👁 Voice Manager\n"
            "🛡️ Senior Mod — ⚔️ Mod — 🗡️ Helper — 🔫 Assistant — 📙 Trial Staff\n\n"
            "**Event Team**\n"
            "🎉 Event Team\n\n"
            "**Division**\n"
            "Division Helper\n\n"
            "To apply for a staff position, use the **Apply** button on the main panel."
        )
    },
    {
        "title": "Activities & Benefits",
        "description": (
            "Being active in MA comes with real perks:\n\n"
            "— Regular giveaways for active members\n"
            "— Community events with prizes\n"
            "— Job and collaboration opportunities in the Ajr Room\n"
            "— Gaming sessions with other members\n"
            "— Special announcements and early access to server updates\n\n"
            "Enable **Notifications** to stay up to date."
        )
    },
    {
        "title": "Getting Started",
        "description": (
            "Here's how to get the most out of MA:\n\n"
            "1. Read the **Server Rules** carefully\n"
            "2. Select your **Notification** preferences\n"
            "3. Introduce yourself in the introductions channel\n"
            "4. Engage with the community\n"
            "5. If you're interested in joining the staff, use the **Apply** button\n\n"
            "If you have any questions, feel free to reach out to any staff member."
        )
    }
]

APPLY_TERMS = (
    "Please read the following before submitting your application:\n\n"
    "— You must be an active member of the server\n"
    "— You must be at least 15 years old\n"
    "— You must be regularly available\n"
    "— All answers must be honest and accurate\n\n"
    "— If your application is rejected, no reason will be provided\n"
    "— Rejection does not reflect your value as a member\n"
    "— Do not apply unless you are serious about the commitment\n\n"
    "By clicking **I Agree**, you confirm that you have read and accept all of the above."
)

# ─────────────────────────────────────────
#        STARTUP ROOM — MODALS
# ─────────────────────────────────────────

class ModeratorApplyModal(discord.ui.Modal, title="Staff Application — Moderator"):
    q1 = discord.ui.TextInput(label="Your name and age", placeholder="Name, Age", max_length=100)
    q2 = discord.ui.TextInput(label="Why do you want to be a Moderator?", style=discord.TextStyle.paragraph, max_length=500)
    q3 = discord.ui.TextInput(label="How do you handle rule violations?", style=discord.TextStyle.paragraph, max_length=500)
    q4 = discord.ui.TextInput(label="How many hours per day are you available?", max_length=100)

    async def on_submit(self, interaction: discord.Interaction):
        await send_application(interaction, "Staff Application — Moderator", [
            ("Name & Age", self.q1.value),
            ("Reason for Applying", self.q2.value),
            ("Handling Violations", self.q3.value),
            ("Daily Availability", self.q4.value),
        ])

class DivisionHelperApplyModal(discord.ui.Modal, title="Staff Application — Division Helper"):
    q1 = discord.ui.TextInput(label="Your name and age", placeholder="Name, Age", max_length=100)
    q2 = discord.ui.TextInput(label="Why do you want to be a Division Helper?", style=discord.TextStyle.paragraph, max_length=500)
    q3 = discord.ui.TextInput(label="What skills can you bring to the team?", style=discord.TextStyle.paragraph, max_length=500)
    q4 = discord.ui.TextInput(label="How many hours per day are you available?", max_length=100)

    async def on_submit(self, interaction: discord.Interaction):
        await send_application(interaction, "Staff Application — Division Helper", [
            ("Name & Age", self.q1.value),
            ("Reason for Applying", self.q2.value),
            ("Skills & Strengths", self.q3.value),
            ("Daily Availability", self.q4.value),
        ])

class EventTeamApplyModal(discord.ui.Modal, title="Staff Application — Event Team"):
    q1 = discord.ui.TextInput(label="Your name and age", placeholder="Name, Age", max_length=100)
    q2 = discord.ui.TextInput(label="What types of events can you organize?", style=discord.TextStyle.paragraph, max_length=500)
    q3 = discord.ui.TextInput(label="Do you have prior experience in events?", style=discord.TextStyle.paragraph, max_length=500)
    q4 = discord.ui.TextInput(label="What makes you stand out?", style=discord.TextStyle.paragraph, max_length=400)

    async def on_submit(self, interaction: discord.Interaction):
        await send_application(interaction, "Staff Application — Event Team", [
            ("Name & Age", self.q1.value),
            ("Event Types", self.q2.value),
            ("Prior Experience", self.q3.value),
            ("What Sets You Apart", self.q4.value),
        ])

async def send_application(interaction: discord.Interaction, title: str, fields: list):
    config = load_config()
    apps_channel_id = config.get("apps_channel")
    channel = bot.get_channel(int(apps_channel_id)) if apps_channel_id else None

    embed = discord.Embed(title=title, color=MA_COLOR)
    for name, value in fields:
        embed.add_field(name=name, value=value or "—", inline=False)
    embed.set_footer(
        text=f"Submitted by {interaction.user.display_name} ({interaction.user.id}) — MA Server",
        icon_url=interaction.user.display_avatar.url
    )
    embed.timestamp = discord.utils.utcnow()

    if channel:
        await channel.send(embed=embed)
        await interaction.response.send_message(
            "Your application has been submitted. We will be in touch.", ephemeral=True
        )
    else:
        await interaction.response.send_message(
            "Your application has been received. We will be in touch.\n"
            "*(Admin note: applications channel not set — use `/setapps`)*",
            ephemeral=True
        )

# ─────────────────────────────────────────
#        STARTUP ROOM — VIEWS
# ─────────────────────────────────────────

def get_info_embed(page: int) -> discord.Embed:
    info = INFO_PAGES[page]
    embed = discord.Embed(title=info["title"], description=info["description"], color=MA_COLOR)
    embed.set_footer(text=f"MA Server  •  Page {page + 1} of {len(INFO_PAGES)}")
    return embed

def get_main_embed() -> discord.Embed:
    embed = discord.Embed(
        title="Welcome to MA Server",
        description=(
            "This channel will walk you through everything you need to know.\n\n"
            "**Server Rules** — Read before anything else\n"
            "**Server Info** — Learn about our sections, ranks, and how things work\n"
            "**Notifications** — Choose what you want to receive\n"
            "**Apply** — Join the MA staff team"
        ),
        color=MA_COLOR
    )
    embed.set_footer(text="MA Server  •  Enjoy your stay")
    return embed

def get_roles_embed(note: str = "") -> discord.Embed:
    desc = (
        "Select the notifications you'd like to receive from MA Server.\n\n"
        "Press the same button again to remove a role."
    )
    if note:
        desc += f"\n\n{note}"
    embed = discord.Embed(title="Notification Roles", description=desc, color=MA_COLOR)
    embed.set_footer(text="MA Server  •  You can update your preferences at any time")
    return embed


class InfoNavView(discord.ui.View):
    def __init__(self, page: int):
        super().__init__(timeout=300)
        self.page = page
        self.prev_btn.disabled = (page == 0)
        self.next_btn.disabled = (page == len(INFO_PAGES) - 1)
        self.page_indicator.label = f"{page + 1} / {len(INFO_PAGES)}"

    @discord.ui.button(label="Back", style=discord.ButtonStyle.secondary)
    async def prev_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        new_page = self.page - 1
        await interaction.response.edit_message(embed=get_info_embed(new_page), view=InfoNavView(new_page))

    @discord.ui.button(label="1 / 5", style=discord.ButtonStyle.secondary, disabled=True)
    async def page_indicator(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass

    @discord.ui.button(label="Next", style=discord.ButtonStyle.secondary)
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
                embed=get_roles_embed(f"Role **{role_name}** not found. Contact an admin."), view=self
            )
            return
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            note = f"Removed **{role_name}**"
        else:
            await interaction.user.add_roles(role)
            note = f"Added **{role_name}**"
        await interaction.response.edit_message(embed=get_roles_embed(note), view=self)

    @discord.ui.button(label="Server Notifications", style=discord.ButtonStyle.secondary, row=0)
    async def server_notif(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._toggle(interaction, "Server Notifications")

    @discord.ui.button(label="Ajr Notifications", style=discord.ButtonStyle.secondary, row=0)
    async def ajr_notif(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._toggle(interaction, "Ajr Notifications")

    @discord.ui.button(label="Events Notifications", style=discord.ButtonStyle.secondary, row=1)
    async def events_notif(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._toggle(interaction, "Events Notifications")

    @discord.ui.button(label="Games Notifications", style=discord.ButtonStyle.secondary, row=1)
    async def games_notif(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._toggle(interaction, "Games Notifications")

    @discord.ui.button(label="Add All", style=discord.ButtonStyle.secondary, row=2)
    async def add_all(self, interaction: discord.Interaction, button: discord.ui.Button):
        roles = [discord.utils.get(interaction.guild.roles, name=r) for r in NOTIFICATION_ROLES]
        roles = [r for r in roles if r]
        if roles:
            await interaction.user.add_roles(*roles)
        await interaction.response.edit_message(embed=get_roles_embed("All notification roles added."), view=self)

    @discord.ui.button(label="Remove All", style=discord.ButtonStyle.danger, row=2)
    async def remove_all(self, interaction: discord.Interaction, button: discord.ui.Button):
        roles = [discord.utils.get(interaction.guild.roles, name=r) for r in NOTIFICATION_ROLES]
        roles = [r for r in roles if r]
        if roles:
            await interaction.user.remove_roles(*roles)
        await interaction.response.edit_message(embed=get_roles_embed("All notification roles removed."), view=self)


class ApplyTypeView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(label="Moderation", style=discord.ButtonStyle.secondary, row=0)
    async def mod_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="Application Terms — Moderation", description=APPLY_TERMS, color=MA_COLOR)
        embed.set_footer(text="MA Server  •  Read carefully before proceeding")
        await interaction.response.edit_message(embed=embed, view=ApplyTermsView("mod"))

    @discord.ui.button(label="Event Team", style=discord.ButtonStyle.secondary, row=0)
    async def event_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="Application Terms — Event Team", description=APPLY_TERMS, color=MA_COLOR)
        embed.set_footer(text="MA Server  •  Read carefully before proceeding")
        await interaction.response.edit_message(embed=embed, view=ApplyTermsView("event"))

    @discord.ui.button(label="Division Helper", style=discord.ButtonStyle.secondary, row=0)
    async def division_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="Application Terms — Division Helper", description=APPLY_TERMS, color=MA_COLOR)
        embed.set_footer(text="MA Server  •  Read carefully before proceeding")
        await interaction.response.edit_message(embed=embed, view=ApplyTermsView("division"))


class ApplyTermsView(discord.ui.View):
    def __init__(self, apply_type: str):
        super().__init__(timeout=300)
        self.apply_type = apply_type

    @discord.ui.button(label="I Agree", style=discord.ButtonStyle.secondary)
    async def agree_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.apply_type == "mod":
            await interaction.response.send_modal(ModeratorApplyModal())
        elif self.apply_type == "event":
            await interaction.response.send_modal(EventTeamApplyModal())
        elif self.apply_type == "division":
            await interaction.response.send_modal(DivisionHelperApplyModal())

    @discord.ui.button(label="Back", style=discord.ButtonStyle.secondary)
    async def back_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="Staff Applications — MA Server",
            description=(
                "Select the position you'd like to apply for:\n\n"
                "**Moderation** — Moderating the server and enforcing rules\n"
                "**Event Team** — Planning and running server events\n"
                "**Division Helper** — Supporting the division team"
            ),
            color=MA_COLOR
        )
        await interaction.response.edit_message(embed=embed, view=ApplyTypeView())


class StartupMainView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Server Rules", style=discord.ButtonStyle.danger, custom_id="ma_rules_v3")
    async def rules_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="MA Server — Rules", description=RULES_TEXT, color=MA_COLOR)
        embed.set_footer(text="MA Server  •  Compliance is mandatory for all members")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Server Info", style=discord.ButtonStyle.secondary, custom_id="ma_info_v3")
    async def info_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(embed=get_info_embed(0), view=InfoNavView(0), ephemeral=True)

    @discord.ui.button(label="Notifications", style=discord.ButtonStyle.secondary, custom_id="ma_roles_v3")
    async def roles_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(embed=get_roles_embed(), view=RolesView(), ephemeral=True)

    @discord.ui.button(label="Apply", style=discord.ButtonStyle.secondary, custom_id="ma_apply_v3")
    async def apply_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="Staff Applications — MA Server",
            description=(
                "Select the position you'd like to apply for:\n\n"
                "**Administration** — General server management\n"
                "**Events Team** — Planning and running server events\n"
                "**Moderation** — Enforcing rules and maintaining order"
            ),
            color=MA_COLOR
        )
        await interaction.response.send_message(embed=embed, view=ApplyTypeView(), ephemeral=True)

# ─────────────────────────────────────────
#        AJR ROOM — DAILY TASK
# ─────────────────────────────────────────

@tasks.loop(hours=24)
async def send_ajr_message():
    channel = bot.get_channel(AJR_CHANNEL_ID)
    if channel is None:
        return
    guild = bot.get_guild(GUILD_ID)
    if guild is None:
        return
    ajr_role = discord.utils.get(guild.roles, name="Ajr Notifications")
    mention = ajr_role.mention if ajr_role else ""
    message = random.choice(AJR_MESSAGES)
    embed = discord.Embed(
        description=f"✨  {message}",
        color=MA_COLOR
    )
    embed.set_footer(text="MA Server  •  أجر يومي")
    await channel.send(content=mention, embed=embed)

# ─────────────────────────────────────────
#        BOT EVENTS & COMMANDS
# ─────────────────────────────────────────

@bot.event
async def on_ready():
    bot.add_view(StartupMainView())
    guild = discord.Object(id=GUILD_ID)
    bot.tree.copy_global_to(guild=guild)
    await bot.tree.sync(guild=guild)
    if not send_ajr_message.is_running():
        send_ajr_message.start()
    print(f"✅ البوت شغال: {bot.user}")
    print("✅ تم مزامنة الأوامر!")

@bot.tree.command(name="setwelcome", description="اختر قناة الترحيب للأعضاء الجدد")
@app_commands.describe(channel="اختر القناة التي تريد إرسال رسائل الترحيب فيها")
@is_admin_streiter()
async def setwelcome(interaction: discord.Interaction, channel: discord.TextChannel):
    config = load_config()
    config[str(interaction.guild_id)] = {"welcome_channel": channel.id}
    save_config(config)
    await interaction.response.send_message(
        f"✅ تم تعيين قناة الترحيب إلى {channel.mention}!", ephemeral=True
    )

@bot.tree.command(name="testwelcome", description="اختبر رسالة الترحيب على نفسك")
@is_admin_streiter()
async def testwelcome(interaction: discord.Interaction):
    config = load_config()
    guild_id = str(interaction.guild_id)
    if guild_id not in config or "welcome_channel" not in config[guild_id]:
        await interaction.response.send_message(
            "❌ ما تم تعيين قناة ترحيب بعد! استخدم `/setwelcome` أولاً.", ephemeral=True
        )
        return
    await interaction.response.send_message("⏳ جاري إرسال رسالة الاختبار...", ephemeral=True)
    channel = bot.get_channel(config[guild_id]["welcome_channel"])
    if channel is None:
        await interaction.followup.send("❌ ما أقدر أوصل للقناة!", ephemeral=True)
        return
    try:
        await send_welcome(channel, interaction.user)
    except Exception as e:
        await interaction.followup.send(f"❌ حصل خطأ: {e}", ephemeral=True)

@bot.tree.command(name="setup_startup", description="إرسال لوحة روم ستارت اب")
@is_admin_streiter()
async def setup_startup(interaction: discord.Interaction):
    channel = bot.get_channel(STARTUP_CHANNEL_ID)
    if channel is None:
        await interaction.response.send_message("❌ ما أقدر أوصل للروم!", ephemeral=True)
        return
    await channel.send(embed=get_main_embed(), view=StartupMainView())
    await interaction.response.send_message("✅ تم إرسال لوحة ستارت اب!", ephemeral=True)

@bot.tree.command(name="setapps", description="تعيين روم استقبال التقديمات")
@app_commands.describe(channel="الروم الذي تريد إرسال التقديمات إليه")
@is_admin_streiter()
async def setapps(interaction: discord.Interaction, channel: discord.TextChannel):
    config = load_config()
    config["apps_channel"] = channel.id
    save_config(config)
    await interaction.response.send_message(
        f"✅ تم تعيين روم التقديمات إلى {channel.mention}!", ephemeral=True
    )

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
