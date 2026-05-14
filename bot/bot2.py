import discord
from discord import app_commands
from discord.ext import commands, tasks
import os
import json
import random

TOKEN = os.environ.get('BOT2_TOKEN')
GUILD_ID = 1173688498822332568
STARTUP_CHANNEL_ID = 1503359521370931252
MA_COLOR = 0xE74C3C
ADMIN_ROLE_ID = 1503070615106748546
CONFIG_FILE = "bot/config2.json"

NOTIFICATION_ROLES = [
    (1482528755950813374, "Live Notice"),
    (1482528749592252477, "Football Notice"),
    (1482528745066594345, "Games Notice"),
    (1482528752499167252, "Ajr Notice"),
    (1482528747616731208, "Event Notice"),
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
intents.members = False
intents.message_content = False

bot = commands.Bot(command_prefix="!!", intents=intents)

def is_admin():
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
#        STARTUP ROOM — CONTENT
# ─────────────────────────────────────────

RULES_TEXT = (
    "**I. Mutual Respect**\n"
    "All members must treat each other with respect. "
    "Insults, personal attacks, and provocations of any kind are strictly prohibited.\n\n"

    "**II. No Harassment**\n"
    "Harassment, bullying, racism, or any behavior that causes harm to others "
    "will result in an immediate ban.\n\n"

    "**III. Appropriate Content Only**\n"
    "Sharing offensive, adult, or ToS-violating content is not allowed "
    "in any channel under any circumstances.\n\n"

    "**IV. No Spam or Flooding**\n"
    "Repeated messages, excessive reactions, or irrelevant media outside "
    "designated channels is prohibited.\n\n"

    "**V. No Advertising**\n"
    "Promoting other servers, websites, or products without prior approval "
    "from the administration is not permitted.\n\n"

    "**VI. Channel Discipline**\n"
    "Each channel has a specific purpose — use it accordingly. "
    "Follow staff instructions at all times.\n\n"

    "**VII. Privacy & Security**\n"
    "Sharing private information about others or posting suspicious links is strictly forbidden.\n\n"

    "**VIII. Discord Guidelines**\n"
    "All members must comply with [Discord Terms of Service](https://discord.com/terms) "
    "and [Community Guidelines](https://discord.com/guidelines)."
)

INFO_PAGES = [
    {
        "title": "Welcome to Our Server",
        "description": (
            "We're glad to have you here.\n\n"
            "This is a community built on respect, fun, and genuine connection. "
            "Whether you're here to socialize, watch live events, or be part of something bigger — "
            "you're in the right place.\n\n"
            "Use the pages below to learn everything before getting started."
        )
    },
    {
        "title": "Server Sections",
        "description": (
            "**Announcements** — Official server news and updates\n\n"
            "**General Chat** — Open conversations with the community\n\n"
            "**Live & Sports** — Football and live event discussions\n\n"
            "**Gaming** — Gaming sessions and discussions\n\n"
            "**Events** — Competitions, giveaways, and activities\n\n"
            "**Voice Channels** — Hang out and talk with members"
        )
    },
    {
        "title": "Notification Roles",
        "description": (
            "Stay updated by selecting your notification preferences:\n\n"
            "🔴 **Live Notice** — Live stream alerts\n"
            "⚽ **Football Notice** — Football match notifications\n"
            "🎮 **Games Notice** — Gaming session alerts\n"
            "✨ **Ajr Notice** — Daily religious messages\n"
            "🎉 **Event Notice** — Event and giveaway alerts\n\n"
            "Use the **Notifications** button on the main panel to manage your roles."
        )
    },
    {
        "title": "Getting Started",
        "description": (
            "Here's how to get the most out of this server:\n\n"
            "1. Read the **Server Rules** carefully\n"
            "2. Select your **Notification** preferences\n"
            "3. Introduce yourself in the community\n"
            "4. Engage with members and enjoy the content\n"
            "5. Interested in staff? Use the **Apply** button\n\n"
            "If you have questions, reach out to any staff member."
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

class ModApplyModal2(discord.ui.Modal, title="Staff Application — Moderator"):
    q1 = discord.ui.TextInput(label="Your name and age", placeholder="Name, Age", max_length=100)
    q2 = discord.ui.TextInput(label="Why do you want to be a Moderator?", style=discord.TextStyle.paragraph, max_length=500)
    q3 = discord.ui.TextInput(label="How do you handle rule violations?", style=discord.TextStyle.paragraph, max_length=500)
    q4 = discord.ui.TextInput(label="How many hours per day are you available?", max_length=100)

    async def on_submit(self, interaction: discord.Interaction):
        await send_application2(interaction, "Staff Application — Moderator", [
            ("Name & Age", self.q1.value),
            ("Reason for Applying", self.q2.value),
            ("Handling Violations", self.q3.value),
            ("Daily Availability", self.q4.value),
        ])

class EventApplyModal2(discord.ui.Modal, title="Staff Application — Event Team"):
    q1 = discord.ui.TextInput(label="Your name and age", placeholder="Name, Age", max_length=100)
    q2 = discord.ui.TextInput(label="What types of events can you organize?", style=discord.TextStyle.paragraph, max_length=500)
    q3 = discord.ui.TextInput(label="Do you have prior experience in events?", style=discord.TextStyle.paragraph, max_length=500)
    q4 = discord.ui.TextInput(label="What makes you stand out?", style=discord.TextStyle.paragraph, max_length=400)

    async def on_submit(self, interaction: discord.Interaction):
        await send_application2(interaction, "Staff Application — Event Team", [
            ("Name & Age", self.q1.value),
            ("Event Types", self.q2.value),
            ("Prior Experience", self.q3.value),
            ("What Sets You Apart", self.q4.value),
        ])

async def send_application2(interaction: discord.Interaction, title: str, fields: list):
    config = load_config()
    apps_channel_id = config.get("apps_channel2")
    if not apps_channel_id:
        await interaction.response.send_message(
            "ما تم تعيين روم التقديمات. استخدم `/setapps2` أولاً.", ephemeral=True
        )
        return
    apps_channel = bot.get_channel(apps_channel_id)
    if apps_channel is None:
        await interaction.response.send_message("❌ ما أقدر أوصل لروم التقديمات.", ephemeral=True)
        return
    embed = discord.Embed(title=title, color=MA_COLOR)
    embed.set_author(name=str(interaction.user), icon_url=interaction.user.display_avatar.url)
    embed.add_field(name="User ID", value=str(interaction.user.id), inline=True)
    for name, value in fields:
        embed.add_field(name=name, value=value or "—", inline=False)
    await apps_channel.send(embed=embed)
    await interaction.response.send_message(
        "✅ تم إرسال تقديمك بنجاح! سيتم مراجعته من قِبل الإدارة.", ephemeral=True
    )

# ─────────────────────────────────────────
#        STARTUP ROOM — VIEWS
# ─────────────────────────────────────────

def get_main_embed2():
    embed = discord.Embed(
        title="Welcome — Start-Up",
        description=(
            "This is your starting point.\n\n"
            "Use the buttons below to explore everything about the server:"
        ),
        color=MA_COLOR
    )
    embed.add_field(name="Server Rules", value="Read the rules to stay in good standing.", inline=False)
    embed.add_field(name="Server Info", value="Learn about the server sections and community.", inline=False)
    embed.add_field(name="Notifications", value="Choose what updates you want to receive.", inline=False)
    embed.add_field(name="Apply", value="Interested in joining the staff team?", inline=False)
    embed.set_footer(text="Server Panel  •  Start Here")
    return embed

def get_roles_embed2(status: str = ""):
    desc = "Select a role to add or remove it from your profile:\n\n"
    for _, name in NOTIFICATION_ROLES:
        desc += f"— {name}\n"
    if status:
        desc += f"\n{status}"
    embed = discord.Embed(title="Notification Roles", description=desc, color=MA_COLOR)
    embed.set_footer(text="Server Panel  •  Notifications")
    return embed

class NotificationView2(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
        for role_id, role_name in NOTIFICATION_ROLES:
            self.add_item(NotifButton2(role_id, role_name))
        self.add_item(AddAllButton2())
        self.add_item(RemoveAllButton2())

class NotifButton2(discord.ui.Button):
    def __init__(self, role_id: int, role_name: str):
        super().__init__(label=role_name, style=discord.ButtonStyle.secondary)
        self.role_id = role_id

    async def callback(self, interaction: discord.Interaction):
        role = interaction.guild.get_role(self.role_id)
        if role is None:
            await interaction.response.edit_message(
                embed=get_roles_embed2("❌ ما أقدر أوصل لهذه الرتبة."), view=self.view
            )
            return
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.edit_message(
                embed=get_roles_embed2(f"— Removed: **{role.name}**"), view=self.view
            )
        else:
            await interaction.user.add_roles(role)
            await interaction.response.edit_message(
                embed=get_roles_embed2(f"+ Added: **{role.name}**"), view=self.view
            )

class AddAllButton2(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Add All", style=discord.ButtonStyle.success)

    async def callback(self, interaction: discord.Interaction):
        roles = [interaction.guild.get_role(rid) for rid, _ in NOTIFICATION_ROLES]
        roles = [r for r in roles if r]
        await interaction.user.add_roles(*roles)
        await interaction.response.edit_message(
            embed=get_roles_embed2("+ All notification roles added."), view=self.view
        )

class RemoveAllButton2(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Remove All", style=discord.ButtonStyle.danger)

    async def callback(self, interaction: discord.Interaction):
        roles = [interaction.guild.get_role(rid) for rid, _ in NOTIFICATION_ROLES]
        roles = [r for r in roles if r]
        await interaction.user.remove_roles(*roles)
        await interaction.response.edit_message(
            embed=get_roles_embed2("— All notification roles removed."), view=self.view
        )

class ApplyTypeView2(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(label="Moderation", style=discord.ButtonStyle.secondary)
    async def mod_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="Application Terms — Moderation", description=APPLY_TERMS, color=MA_COLOR)
        embed.set_footer(text="Server Panel  •  Read carefully before proceeding")
        await interaction.response.edit_message(embed=embed, view=ApplyTermsView2("mod"))

    @discord.ui.button(label="Event Team", style=discord.ButtonStyle.secondary)
    async def event_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="Application Terms — Event Team", description=APPLY_TERMS, color=MA_COLOR)
        embed.set_footer(text="Server Panel  •  Read carefully before proceeding")
        await interaction.response.edit_message(embed=embed, view=ApplyTermsView2("event"))

class ApplyTermsView2(discord.ui.View):
    def __init__(self, apply_type: str):
        super().__init__(timeout=300)
        self.apply_type = apply_type

    @discord.ui.button(label="I Agree", style=discord.ButtonStyle.secondary)
    async def agree_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.apply_type == "mod":
            await interaction.response.send_modal(ModApplyModal2())
        elif self.apply_type == "event":
            await interaction.response.send_modal(EventApplyModal2())

    @discord.ui.button(label="Back", style=discord.ButtonStyle.secondary)
    async def back_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="Staff Applications",
            description=(
                "Select the position you'd like to apply for:\n\n"
                "**Moderation** — Moderating the server and enforcing rules\n"
                "**Event Team** — Planning and running server events"
            ),
            color=MA_COLOR
        )
        await interaction.response.edit_message(embed=embed, view=ApplyTypeView2())

class InfoView2(discord.ui.View):
    def __init__(self, page: int = 0):
        super().__init__(timeout=300)
        self.page = page

    @discord.ui.button(label="Back", style=discord.ButtonStyle.secondary)
    async def back_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page = max(0, self.page - 1)
        await interaction.response.edit_message(embed=self._build_embed(), view=InfoView2(self.page))

    @discord.ui.button(label="1 / 4", style=discord.ButtonStyle.secondary, disabled=True)
    async def counter_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass

    @discord.ui.button(label="Next", style=discord.ButtonStyle.secondary)
    async def next_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page = min(len(INFO_PAGES) - 1, self.page + 1)
        await interaction.response.edit_message(embed=self._build_embed(), view=InfoView2(self.page))

    def _build_embed(self):
        page_data = INFO_PAGES[self.page]
        embed = discord.Embed(title=page_data["title"], description=page_data["description"], color=MA_COLOR)
        embed.set_footer(text=f"Server Panel  •  Page {self.page + 1} of {len(INFO_PAGES)}")
        for item in self.children:
            if "/ 4" in item.label or "/ " in item.label:
                item.label = f"{self.page + 1} / {len(INFO_PAGES)}"
        return embed

class StartupMainView2(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Server Rules", style=discord.ButtonStyle.danger, custom_id="s2_rules")
    async def rules_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="Server Rules", description=RULES_TEXT, color=MA_COLOR)
        embed.set_footer(text="Server Panel  •  Please read carefully")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Server Info", style=discord.ButtonStyle.secondary, custom_id="s2_info")
    async def info_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = InfoView2(0)
        embed = view._build_embed()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @discord.ui.button(label="Notifications", style=discord.ButtonStyle.secondary, custom_id="s2_notifs")
    async def notif_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            embed=get_roles_embed2(), view=NotificationView2(), ephemeral=True
        )

    @discord.ui.button(label="Apply", style=discord.ButtonStyle.secondary, custom_id="s2_apply")
    async def apply_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="Staff Applications",
            description=(
                "Select the position you'd like to apply for:\n\n"
                "**Moderation** — Moderating the server and enforcing rules\n"
                "**Event Team** — Planning and running server events"
            ),
            color=MA_COLOR
        )
        await interaction.response.send_message(embed=embed, view=ApplyTypeView2(), ephemeral=True)

# ─────────────────────────────────────────
#        BOT EVENTS & COMMANDS
# ─────────────────────────────────────────

@bot.event
async def on_ready():
    bot.add_view(StartupMainView2())
    guild = discord.Object(id=GUILD_ID)
    bot.tree.copy_global_to(guild=guild)
    await bot.tree.sync(guild=guild)
    print(f"✅ Bot 2 شغال: {bot.user}")

@bot.tree.command(name="setup_startup2", description="إرسال لوحة ستارت اب للسيرفر")
@is_admin()
async def setup_startup2(interaction: discord.Interaction):
    channel = bot.get_channel(STARTUP_CHANNEL_ID)
    if channel is None:
        await interaction.response.send_message("❌ ما أقدر أوصل للروم!", ephemeral=True)
        return
    await channel.send(embed=get_main_embed2(), view=StartupMainView2())
    await interaction.response.send_message("✅ تم إرسال لوحة ستارت اب!", ephemeral=True)

@bot.tree.command(name="setapps2", description="تعيين روم استقبال التقديمات")
@app_commands.describe(channel="الروم الذي تريد إرسال التقديمات إليه")
@is_admin()
async def setapps2(interaction: discord.Interaction, channel: discord.TextChannel):
    config = load_config()
    config["apps_channel2"] = channel.id
    save_config(config)
    await interaction.response.send_message(
        f"✅ تم تعيين روم التقديمات إلى {channel.mention}!", ephemeral=True
    )

bot.run(TOKEN)
