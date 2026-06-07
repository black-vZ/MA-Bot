import discord
from discord import app_commands
from discord.ext import commands, tasks
import os
import json
import random
import asyncio

TOKEN = os.environ.get('BOT2_TOKEN')
GUILD_ID = 1173688498822332568
STARTUP_CHANNEL_ID = 1503359521370931252
AJR_CHANNEL_ID2 = 1503359595228430336
MA_COLOR = 0xE74C3C
ADMIN_ROLE_ID = 1503070615106748546
CONFIG_FILE = "bot/config2.json"

NOTIFICATION_ROLES = [
    (1482528743447728290, "Server Notice"),
    (1482528747616731208, "Giveaway Notice"),
    (1482528742046961846, "Event Notice"),
    (1482528752499167252, "Ajr Notice"),
    (1482528745066594345, "Games Notice"),
    (1482528749592252477, "Football Notice"),
    (1482528755950813374, "Live Notice"),
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
            "📢 **Server Notice** — Server announcements\n"
            "🎁 **Giveaway Notice** — Giveaway alerts\n"
            "🎉 **Event Notice** — Event alerts\n"
            "✨ **Ajr Notice** — Daily religious messages\n"
            "🎮 **Games Notice** — Gaming session alerts\n"
            "⚽ **Football Notice** — Football match notifications\n"
            "🔴 **Live Notice** — Live stream alerts\n\n"
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

class NotifButton2(discord.ui.Button):
    def __init__(self, role_id: int, role_name: str, row: int):
        super().__init__(
            label=role_name,
            style=discord.ButtonStyle.secondary,
            custom_id=f"s2_notif_{role_id}",
            row=row
        )
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
        super().__init__(label="Add All", style=discord.ButtonStyle.success, custom_id="s2_notif_add_all", row=2)

    async def callback(self, interaction: discord.Interaction):
        roles = [interaction.guild.get_role(rid) for rid, _ in NOTIFICATION_ROLES]
        roles = [r for r in roles if r]
        await interaction.user.add_roles(*roles)
        await interaction.response.edit_message(
            embed=get_roles_embed2("+ All notification roles added."), view=self.view
        )

class RemoveAllButton2(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Remove All", style=discord.ButtonStyle.danger, custom_id="s2_notif_remove_all", row=2)

    async def callback(self, interaction: discord.Interaction):
        roles = [interaction.guild.get_role(rid) for rid, _ in NOTIFICATION_ROLES]
        roles = [r for r in roles if r]
        await interaction.user.remove_roles(*roles)
        await interaction.response.edit_message(
            embed=get_roles_embed2("— All notification roles removed."), view=self.view
        )

class NotificationView2(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        for i, (role_id, role_name) in enumerate(NOTIFICATION_ROLES):
            row = 0 if i < 4 else 1
            self.add_item(NotifButton2(role_id, role_name, row=row))
        self.add_item(AddAllButton2())
        self.add_item(RemoveAllButton2())

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
#        TICKET SYSTEM
# ─────────────────────────────────────────

STAFF_ROLE_ID2    = 1503071852782682133
EVENT_ROLE_ID2    = 1503073635169206404
MGMT_ROLE_ID2     = 1503072777077522642

TICKET_TYPE_CONFIG2 = {
    "support":       {"label": "Support Ticket",       "role_id": STAFF_ROLE_ID2, "emoji": "🎫"},
    "event":         {"label": "Event Ticket",         "role_id": EVENT_ROLE_ID2, "emoji": "🎉"},
    "administrator": {"label": "Administrator Ticket", "role_id": MGMT_ROLE_ID2,  "emoji": "⚙️"},
    "report":        {"label": "Report Ticket",        "role_id": STAFF_ROLE_ID2, "emoji": "📋"},
}

def get_ticket_count():
    return load_config().get("ticket_count", 0)

def next_ticket_number():
    config = load_config()
    count = config.get("ticket_count", 0) + 1
    config["ticket_count"] = count
    save_config(config)
    return count

def get_ticket_panel_channel_id():
    return load_config().get("ticket_channel2")

def add_active_ticket(user_id: int, channel_id: int):
    config = load_config()
    tickets = config.get("active_tickets", {})
    tickets[str(user_id)] = channel_id
    config["active_tickets"] = tickets
    save_config(config)

def remove_active_ticket(channel_id: int):
    config = load_config()
    tickets = config.get("active_tickets", {})
    config["active_tickets"] = {k: v for k, v in tickets.items() if v != channel_id}
    save_config(config)

def get_active_ticket(user_id: int):
    tickets = load_config().get("active_tickets", {})
    return tickets.get(str(user_id))

def get_ticket_info_embed2():
    embed = discord.Embed(title="هل انت متاكد من فتح التذكرة ؟", color=MA_COLOR)
    embed.add_field(
        name="في حال الموافقة",
        value=(
            "● المحتوى الموجود داخل التذكرة غير قابل للنشر، وأيضاً لا يسمح بفتح شير وتجعل أحد يراها، "
            "وأيضاً لا يسمح بـ عمل نسخة أو لقطات شاشة، عقوبتها الباند من سيرفر بشكل نهائي.\n\n"
            "● لا يحق لك الاعتراض على اي قرار يتم اتخاذه بحقك اثناء استخدام التكت، سواء أكان معك أم كان ضدك.\n\n"
            "● التكت ستكون محفوظة لأي أجراء سيتم مراجعته أو إتخاذه في المستقبل ويحق للأدارة العليا "
            "مراجعتها او استخدامها كدليل ضدك في المستقبل في حال عدم احترامك اثناء التحدث مع الأدارة."
        ),
        inline=False
    )
    return embed

TICKET_GIF_URL = "https://raw.githubusercontent.com/black-vZ/MA-Bot/main/assets/ticket_banner.gif"

def get_ticket_panel_embed2():
    embed = discord.Embed(
        title="Ticket System",
        description=(
            "Welcome to the ticket system, here you can open a ticket and get help from the staff team.\n"
            "*Please read the rules before opening a ticket.*"
        ),
        color=MA_COLOR
    )
    embed.set_image(url=TICKET_GIF_URL)
    embed.set_footer(text="RS System  •  Ticket System")
    return embed

class TicketModal2(discord.ui.Modal, title="Open a Ticket"):
    reason = discord.ui.TextInput(
        label="Reason for opening this ticket",
        placeholder="Please describe your issue in detail...",
        required=True,
        min_length=10,
        max_length=1000,
        style=discord.TextStyle.paragraph
    )

    def __init__(self, ticket_type: str):
        super().__init__()
        self.ticket_type = ticket_type

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        existing_id = get_active_ticket(interaction.user.id)
        if existing_id:
            existing_ch = interaction.guild.get_channel(existing_id)
            if existing_ch:
                await interaction.followup.send(
                    f"❌ عندك تيكت مفتوح بالفعل! {existing_ch.mention}", ephemeral=True
                )
                return
            else:
                remove_active_ticket(existing_id)
        guild = interaction.guild
        cfg = TICKET_TYPE_CONFIG2[self.ticket_type]
        num = next_ticket_number()
        ticket_name = f"ticket-{num:04d}"

        panel_ch_id = get_ticket_panel_channel_id()
        category = None
        if panel_ch_id:
            panel_ch = guild.get_channel(panel_ch_id)
            if panel_ch and panel_ch.category:
                category = panel_ch.category

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(
                view_channel=True, send_messages=True,
                read_message_history=True, attach_files=True
            ),
        }
        role = guild.get_role(cfg["role_id"])
        if role:
            overwrites[role] = discord.PermissionOverwrite(
                view_channel=True, send_messages=True,
                read_message_history=True, manage_messages=True
            )
        if self.ticket_type == "administrator":
            admin_role = guild.get_role(ADMIN_ROLE_ID)
            if admin_role:
                overwrites[admin_role] = discord.PermissionOverwrite(
                    view_channel=True, send_messages=True,
                    read_message_history=True, manage_messages=True
                )

        ticket_channel = await guild.create_text_channel(
            name=ticket_name, category=category, overwrites=overwrites,
            topic=f"{cfg['label']} | {interaction.user.id} | #{num:04d}"
        )

        embed = discord.Embed(
            title=f"{cfg['emoji']} Ticket Created — {cfg['label']}",
            description="Please wait for the staff to assist you.\nTo save time, please describe your issue clearly.",
            color=MA_COLOR
        )
        embed.add_field(name="Opened By", value=interaction.user.mention, inline=True)
        embed.add_field(name="Type",      value=cfg["label"],             inline=True)
        embed.add_field(name="Ticket #",  value=f"{num:04d}",             inline=True)
        embed.add_field(name="Reason",    value=self.reason.value,        inline=False)
        embed.set_footer(text="RS System  •  Ticket System")

        mentions = interaction.user.mention + (f" {role.mention}" if role else "")
        await ticket_channel.send(content=mentions, embed=embed, view=TicketControlView2())
        add_active_ticket(interaction.user.id, ticket_channel.id)
        await interaction.followup.send(f"✅ تم فتح تذكرتك! {ticket_channel.mention}", ephemeral=True)

class TicketTypeSelect2(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Support Ticket",       value="support",       description="Open a ticket for support.",                    emoji="🎫"),
            discord.SelectOption(label="Event Ticket",         value="event",         description="Open a ticket for event support.",               emoji="🎉"),
            discord.SelectOption(label="Administrator Ticket", value="administrator", description="Open a ticket to speak to an administrator.",    emoji="⚙️"),
            discord.SelectOption(label="Report Ticket",        value="report",        description="Open a ticket to report someone.",               emoji="📋"),
        ]
        super().__init__(placeholder="Please select a type to open a ticket.", options=options, custom_id="s2_ticket_select")

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(TicketModal2(self.values[0]))

class TicketSelectView2(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)
        self.add_item(TicketTypeSelect2())

class ConfirmCloseView2(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)

    @discord.ui.button(label="Confirm Close", style=discord.ButtonStyle.danger, custom_id="s2_ticket_confirm_close")
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(
            embed=discord.Embed(description="🔒 سيتم إغلاق التذكرة خلال 5 ثواني...", color=MA_COLOR), view=None
        )
        remove_active_ticket(interaction.channel.id)
        await asyncio.sleep(5)
        await interaction.channel.delete(reason=f"Ticket closed by {interaction.user}")

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary, custom_id="s2_ticket_cancel_close")
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(
            embed=discord.Embed(description="❌ تم إلغاء الإغلاق.", color=MA_COLOR), view=None
        )

class TicketOptionsView2(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)

    @discord.ui.button(label="Delete Ticket", style=discord.ButtonStyle.danger, custom_id="s2_ticket_delete")
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🗑️ سيتم حذف التذكرة خلال 5 ثواني...", ephemeral=False)
        remove_active_ticket(interaction.channel.id)
        await asyncio.sleep(5)
        await interaction.channel.delete(reason=f"Ticket deleted by {interaction.user}")

class TicketControlView2(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="s2_ticket_close")
    async def close_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="🔒 Close Ticket",
            description=f"Are you sure you want to close this ticket?\nRequested by {interaction.user.mention}",
            color=MA_COLOR
        )
        await interaction.response.send_message(embed=embed, view=ConfirmCloseView2())

    @discord.ui.button(label="Claim", style=discord.ButtonStyle.primary, emoji="🤚", custom_id="s2_ticket_claim")
    async def claim_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        role_ids = [r.id for r in interaction.user.roles]
        if STAFF_ROLE_ID2 not in role_ids and MGMT_ROLE_ID2 not in role_ids and ADMIN_ROLE_ID not in role_ids and EVENT_ROLE_ID2 not in role_ids:
            await interaction.response.send_message("❌ ما عندك صلاحية!", ephemeral=True)
            return
        embed = discord.Embed(description=f"✅ تم استلام التذكرة بواسطة {interaction.user.mention}", color=MA_COLOR)
        await interaction.response.send_message(embed=embed)

    @discord.ui.button(label="Options", style=discord.ButtonStyle.secondary, emoji="⚙️", custom_id="s2_ticket_options")
    async def options_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        role_ids = [r.id for r in interaction.user.roles]
        if STAFF_ROLE_ID2 not in role_ids and MGMT_ROLE_ID2 not in role_ids and ADMIN_ROLE_ID not in role_ids:
            await interaction.response.send_message("❌ ما عندك صلاحية!", ephemeral=True)
            return
        embed = discord.Embed(title="⚙️ Ticket Options", color=MA_COLOR)
        embed.add_field(name="Delete Ticket", value="This will permanently delete the ticket channel.", inline=False)
        await interaction.response.send_message(embed=embed, view=TicketOptionsView2(), ephemeral=True)

class TicketPanelView2(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Open Ticket", style=discord.ButtonStyle.success, custom_id="s2_open_ticket")
    async def open_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = get_ticket_panel_embed2()
        await interaction.response.send_message(embed=embed, view=TicketSelectView2(), ephemeral=True)

    @discord.ui.button(label="Some Information", style=discord.ButtonStyle.secondary, custom_id="s2_ticket_info")
    async def info_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(embed=get_ticket_info_embed2(), ephemeral=True)

# ─────────────────────────────────────────
#        BOT EVENTS & COMMANDS
# ─────────────────────────────────────────

AJR_MESSAGES2 = [
    "قال رسول الله ﷺ: «مَن قال سبحان الله وبحمده في يوم مئة مرة، حُطَّت خطاياه وإن كانت مثل زبد البحر»\n— متفق عليه",
    "قال رسول الله ﷺ: «كلمتان خفيفتان على اللسان، ثقيلتان في الميزان، حبيبتان إلى الرحمن: سبحان الله وبحمده، سبحان الله العظيم»\n— متفق عليه",
    "قال رسول الله ﷺ: «مَن قرأ آية الكرسي دبر كل صلاة مكتوبة لم يمنعه من دخول الجنة إلا أن يموت»\n— صحيح النسائي",
    "قال الله تعالى: ﴿فَاذْكُرُونِي أَذْكُرْكُمْ وَاشْكُرُوا لِي وَلَا تَكْفُرُونِ﴾\n— سورة البقرة: 152",
    "قال رسول الله ﷺ: «مَن صلى على واحدة صلى الله عليه بها عشراً»\n— صحيح مسلم",
    "قال رسول الله ﷺ: «أحب الأعمال إلى الله أدومها وإن قَلَّ»\n— متفق عليه",
    "قال الله تعالى: ﴿إِنَّ اللَّهَ مَعَ الصَّابِرِينَ﴾\n— سورة البقرة: 153",
    "قال رسول الله ﷺ: «الطهور شطر الإيمان، والحمد لله تملأ الميزان، وسبحان الله والحمد لله تملآن ما بين السماوات والأرض»\n— صحيح مسلم",
    "قال الله تعالى: ﴿وَمَن يَتَّقِ اللَّهَ يَجْعَل لَّهُ مَخْرَجًا ۝ وَيَرْزُقْهُ مِنْ حَيْثُ لَا يَحْتَسِبُ﴾\n— سورة الطلاق: 2-3",
    "قال رسول الله ﷺ: «مَن سلك طريقاً يلتمس فيه علماً سهَّل الله له به طريقاً إلى الجنة»\n— صحيح مسلم",
    "قال الله تعالى: ﴿وَقُل رَّبِّ زِدْنِي عِلْمًا﴾\n— سورة طه: 114",
    "قال رسول الله ﷺ: «أفضل الذكر لا إله إلا الله، وأفضل الدعاء الحمد لله»\n— صحيح الترمذي",
    "قال الله تعالى: ﴿إِنَّ مَعَ الْعُسْرِ يُسْرًا﴾\n— سورة الشرح: 6",
    "قال رسول الله ﷺ: «لا يؤمن أحدكم حتى يحب لأخيه ما يحب لنفسه»\n— متفق عليه",
    "قال الله تعالى: ﴿وَاللَّهُ يُحِبُّ الصَّابِرِينَ﴾\n— سورة آل عمران: 146",
    "قال رسول الله ﷺ: «البر حسن الخلق، والإثم ما حاك في صدرك وكرهت أن يطلع عليه الناس»\n— صحيح مسلم",
    "قال رسول الله ﷺ: «إن من أحبكم إليّ وأقربكم مني مجلساً يوم القيامة أحاسنَكم أخلاقاً»\n— صحيح الترمذي",
    "قال رسول الله ﷺ: «رحم الله رجلاً سمحاً إذا باع وإذا اشترى وإذا اقتضى»\n— صحيح البخاري",
    "قال رسول الله ﷺ: «ما من مسلم يغرس غرساً فيأكل منه طير أو إنسان إلا كان له به صدقة»\n— متفق عليه",
    "قال الله تعالى: ﴿وَمَنْ أَحْسَنُ قَوْلًا مِّمَّن دَعَا إِلَى اللَّهِ وَعَمِلَ صَالِحًا﴾\n— سورة فصلت: 33",
]

@tasks.loop(hours=24)
async def send_ajr_message2():
    channel = bot.get_channel(AJR_CHANNEL_ID2)
    if channel is None:
        return
    guild = bot.get_guild(GUILD_ID)
    if guild is None:
        return
    ajr_role = discord.utils.get(guild.roles, id=1482528752499167252)
    mention = ajr_role.mention if ajr_role else ""
    message = random.choice(AJR_MESSAGES2)
    embed = discord.Embed(description=f"✨  {message}", color=MA_COLOR)
    embed.set_footer(text="Server  •  أجر يومي")
    await channel.send(content=mention, embed=embed)

VERIFIED_ROLE_ID   = 1503683196011941908
RS_FOREVER_ROLE_ID = 1482528735717494897

# ─────────────────────────────────────────
#        WELCOME SYSTEM
# ─────────────────────────────────────────

WELCOME_BG_PATH = "bot/assets/welcome_bg.png"

async def create_welcome_image(member: discord.Member) -> "io.BytesIO":
    import aiohttp, io
    from PIL import Image, ImageDraw

    bg = Image.open(WELCOME_BG_PATH).convert("RGBA")
    w, h = bg.size                     # 500 x 281

    # Download member avatar
    avatar_url = str(member.display_avatar.with_size(256).url)
    async with aiohttp.ClientSession() as session:
        async with session.get(avatar_url) as resp:
            av_bytes = await resp.read()

    av_size = 110
    av = Image.open(io.BytesIO(av_bytes)).convert("RGBA").resize((av_size, av_size))

    # Circular crop
    mask = Image.new("L", (av_size, av_size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, av_size, av_size), fill=255)
    av_circle = Image.new("RGBA", (av_size, av_size), (0, 0, 0, 0))
    av_circle.paste(av, mask=mask)

    # Paste avatar — centered inside blue ring circle
    av_x = 22
    av_y = 20
    bg.paste(av_circle, (av_x, av_y), av_circle)

    buf = io.BytesIO()
    bg.save(buf, format="PNG")
    buf.seek(0)
    return buf

@bot.event
async def on_member_join(member: discord.Member):
    import io
    config = load_config()
    channel_id = config.get("welcome_channel2")
    if not channel_id:
        return
    channel = bot.get_channel(channel_id)
    if not channel:
        return

    member_count = member.guild.member_count

    welcome_text = (
        f"**❖  Welcome To : RS Community\n"
        f"❖ Name : {member.mention}\n"
        f"❖ You Are Now A Whitelisted Number : {member_count}\n"
        f"❖ Have A Great Time.**"
    )

    try:
        img_buf = await create_welcome_image(member)
        await channel.send(file=discord.File(img_buf, filename="welcome.png"))
        await channel.send(content=welcome_text)
    except Exception as e:
        await channel.send(content=welcome_text)
        print(f"Welcome image error: {e}")

@bot.event
async def on_member_update(before: discord.Member, after: discord.Member):
    verified_role = discord.utils.get(after.guild.roles, id=VERIFIED_ROLE_ID)
    rs_forever_role = discord.utils.get(after.guild.roles, id=RS_FOREVER_ROLE_ID)
    if verified_role is None or rs_forever_role is None:
        return
    if verified_role not in before.roles and verified_role in after.roles:
        if rs_forever_role not in after.roles:
            await after.add_roles(rs_forever_role, reason="تلقائي عند الـ Verify")

@bot.event
async def on_ready():
    bot.add_view(StartupMainView2())
    bot.add_view(NotificationView2())
    bot.add_view(TicketPanelView2())
    bot.add_view(TicketControlView2())
    guild = discord.Object(id=GUILD_ID)
    bot.tree.copy_global_to(guild=guild)
    await bot.tree.sync(guild=guild)
    if not send_ajr_message2.is_running():
        send_ajr_message2.start()
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

@bot.tree.command(name="setup_welcome2", description="تعيين روم الترحيب بالأعضاء الجدد")
@app_commands.describe(channel="الروم الذي تريد إرسال الترحيب فيه")
@is_admin()
async def setup_welcome2(interaction: discord.Interaction, channel: discord.TextChannel):
    config = load_config()
    config["welcome_channel2"] = channel.id
    save_config(config)
    await interaction.response.send_message(
        f"✅ تم تعيين روم الترحيب إلى {channel.mention}!", ephemeral=True
    )

@bot.tree.command(name="setup_tickets2", description="إرسال بانل نظام التيكت")
@app_commands.describe(channel="الروم الذي تريد إرسال بانل التيكت إليه")
@is_admin()
async def setup_tickets2(interaction: discord.Interaction, channel: discord.TextChannel):
    config = load_config()
    config["ticket_channel2"] = channel.id
    save_config(config)
    await channel.send(embed=get_ticket_panel_embed2(), view=TicketPanelView2())
    await interaction.response.send_message(f"✅ تم إرسال بانل التيكت في {channel.mention}!", ephemeral=True)

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
