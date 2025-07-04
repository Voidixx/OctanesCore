
import discord
from discord.ext import commands
import json
import random
from datetime import datetime, timedelta
from data import load_data, save_data
from utils import *

def load_clans():
    return load_data("clans.json")

def save_clans(clans):
    save_data("clans.json", clans)

def load_clan_members():
    return load_data("clan_members.json")

def save_clan_members(members):
    save_data("clan_members.json", members)

def get_player_clan(user_id):
    members = load_clan_members()
    return members.get(str(user_id))

def create_clan(name, tag, owner_id, description="A new clan ready for action!"):
    clans = load_clans()
    clan_id = f"clan_{random.randint(10000, 99999)}"
    
    # Check if clan name or tag already exists
    for existing_clan in clans.values():
        if existing_clan["name"].lower() == name.lower():
            return None, "Clan name already exists!"
        if existing_clan["tag"].lower() == tag.lower():
            return None, "Clan tag already taken!"
    
    clan_data = {
        "id": clan_id,
        "name": name,
        "tag": tag,
        "description": description,
        "owner_id": owner_id,
        "created_at": datetime.now().isoformat(),
        "level": 1,
        "experience": 0,
        "member_count": 1,
        "max_members": 20,
        "total_wins": 0,
        "total_matches": 0,
        "trophies": 0,
        "perks": {
            "xp_boost": 0,
            "credit_boost": 0,
            "queue_priority": False,
            "custom_banner": False
        },
        "settings": {
            "join_type": "open",  # open, invite_only, application
            "min_mmr": 0,
            "region": "global"
        }
    }
    
    clans[clan_id] = clan_data
    save_clans(clans)
    
    # Add owner to clan members
    members = load_clan_members()
    members[str(owner_id)] = {
        "clan_id": clan_id,
        "role": "owner",
        "joined_at": datetime.now().isoformat(),
        "contribution": 0,
        "matches_played": 0
    }
    save_clan_members(members)
    
    return clan_id, None

def join_clan(user_id, clan_id):
    clans = load_clans()
    members = load_clan_members()
    
    if clan_id not in clans:
        return False, "Clan not found!"
    
    if str(user_id) in members:
        return False, "You're already in a clan!"
    
    clan = clans[clan_id]
    
    if clan["member_count"] >= clan["max_members"]:
        return False, "Clan is full!"
    
    # Add member
    members[str(user_id)] = {
        "clan_id": clan_id,
        "role": "member",
        "joined_at": datetime.now().isoformat(),
        "contribution": 0,
        "matches_played": 0
    }
    
    # Update clan member count
    clan["member_count"] += 1
    
    save_clan_members(members)
    save_clans(clans)
    
    return True, "Successfully joined clan!"

def leave_clan(user_id):
    members = load_clan_members()
    clans = load_clans()
    
    if str(user_id) not in members:
        return False, "You're not in a clan!"
    
    member_data = members[str(user_id)]
    clan_id = member_data["clan_id"]
    
    if member_data["role"] == "owner":
        return False, "Clan owners cannot leave! Transfer ownership or disband the clan."
    
    # Remove member
    del members[str(user_id)]
    
    # Update clan member count
    if clan_id in clans:
        clans[clan_id]["member_count"] -= 1
    
    save_clan_members(members)
    save_clans(clans)
    
    return True, "Successfully left clan!"

class ClanView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=300)
        self.user_id = user_id
    
    @discord.ui.button(label="🏠 My Clan", style=discord.ButtonStyle.primary)
    async def my_clan(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ This is not your clan panel!", ephemeral=True)
            return
        
        member_data = get_player_clan(self.user_id)
        if not member_data:
            embed = discord.Embed(title="🏠 No Clan", description="You're not currently in a clan!", color=0xff0000)
            embed.add_field(name="💡 Getting Started", value="• Use the **Join Clan** button to find a clan\n• Or create your own with **Create Clan**", inline=False)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        clans = load_clans()
        clan = clans.get(member_data["clan_id"])
        
        if not clan:
            await interaction.response.send_message("❌ Clan data not found!", ephemeral=True)
            return
        
        embed = discord.Embed(title=f"🏠 [{clan['tag']}] {clan['name']}", color=0x00ffcc)
        embed.add_field(name="📊 Level", value=f"Level {clan['level']}", inline=True)
        embed.add_field(name="👥 Members", value=f"{clan['member_count']}/{clan['max_members']}", inline=True)
        embed.add_field(name="🏆 Trophies", value=str(clan['trophies']), inline=True)
        embed.add_field(name="⚔️ Win Rate", value=f"{(clan['total_wins']/clan['total_matches']*100):.1f}%" if clan['total_matches'] > 0 else "0%", inline=True)
        embed.add_field(name="🎯 Your Role", value=member_data['role'].title(), inline=True)
        embed.add_field(name="📅 Joined", value=datetime.fromisoformat(member_data['joined_at']).strftime("%Y-%m-%d"), inline=True)
        embed.add_field(name="📝 Description", value=clan['description'], inline=False)
        
        # Show perks if any
        active_perks = [k for k, v in clan['perks'].items() if v]
        if active_perks:
            perk_text = "\n".join([f"• {perk.replace('_', ' ').title()}" for perk in active_perks])
            embed.add_field(name="✨ Active Perks", value=perk_text, inline=False)
        
        view = ClanManagementView(self.user_id, clan['id'])
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @discord.ui.button(label="🔍 Find Clans", style=discord.ButtonStyle.secondary)
    async def find_clans(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ This is not your clan panel!", ephemeral=True)
            return
        
        clans = load_clans()
        
        if not clans:
            await interaction.response.send_message("❌ No clans available to join!", ephemeral=True)
            return
        
        # Show top clans by trophies
        sorted_clans = sorted(clans.values(), key=lambda x: x['trophies'], reverse=True)[:10]
        
        embed = discord.Embed(title="🔍 Available Clans", color=0x9b59b6)
        
        for clan in sorted_clans:
            join_status = "🔓 Open" if clan['settings']['join_type'] == 'open' else "🔒 Invite Only"
            embed.add_field(
                name=f"[{clan['tag']}] {clan['name']}",
                value=f"**Level {clan['level']}** • {clan['member_count']}/{clan['max_members']} members\n🏆 {clan['trophies']} trophies • {join_status}",
                inline=True
            )
        
        view = ClanBrowserView(self.user_id)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @discord.ui.button(label="➕ Create Clan", style=discord.ButtonStyle.success)
    async def create_clan(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ This is not your clan panel!", ephemeral=True)
            return
        
        # Check if user is already in a clan
        if get_player_clan(self.user_id):
            await interaction.response.send_message("❌ You're already in a clan! Leave your current clan first.", ephemeral=True)
            return
        
        modal = CreateClanModal()
        await interaction.response.send_modal(modal)

class CreateClanModal(discord.ui.Modal, title="Create New Clan"):
    def __init__(self):
        super().__init__()
    
    clan_name = discord.ui.TextInput(
        label="Clan Name",
        placeholder="Enter your clan name (max 30 characters)",
        max_length=30
    )
    
    clan_tag = discord.ui.TextInput(
        label="Clan Tag",
        placeholder="Enter clan tag (max 6 characters)",
        max_length=6
    )
    
    description = discord.ui.TextInput(
        label="Description",
        placeholder="Describe your clan...",
        style=discord.TextStyle.paragraph,
        max_length=200,
        required=False
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        from economy import spend_credits, get_player_economy
        
        # Check if user has enough credits (cost: 1000 credits)
        player_economy = get_player_economy(interaction.user.id)
        if player_economy["credits"] < 1000:
            await interaction.response.send_message("❌ You need 1000 credits to create a clan!", ephemeral=True)
            return
        
        clan_id, error = create_clan(
            self.clan_name.value,
            self.clan_tag.value,
            interaction.user.id,
            self.description.value or "A new clan ready for action!"
        )
        
        if error:
            await interaction.response.send_message(f"❌ {error}", ephemeral=True)
            return
        
        # Charge the user
        spend_credits(interaction.user.id, 1000, "Clan creation")
        
        embed = discord.Embed(title="✅ Clan Created!", color=0x00ff00)
        embed.add_field(name="Clan Name", value=self.clan_name.value, inline=True)
        embed.add_field(name="Clan Tag", value=f"[{self.clan_tag.value}]", inline=True)
        embed.add_field(name="Cost", value="1000 credits", inline=True)
        embed.add_field(name="💡 Next Steps", value="• Invite members to your clan\n• Participate in clan wars\n• Level up your clan for perks!", inline=False)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class ClanManagementView(discord.ui.View):
    def __init__(self, user_id, clan_id):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.clan_id = clan_id
    
    @discord.ui.button(label="👥 Members", style=discord.ButtonStyle.primary)
    async def view_members(self, interaction: discord.Interaction, button: discord.ui.Button):
        members = load_clan_members()
        clan_members = {k: v for k, v in members.items() if v["clan_id"] == self.clan_id}
        
        embed = discord.Embed(title="👥 Clan Members", color=0x00ffcc)
        
        # Sort by role (owner first, then by join date)
        sorted_members = sorted(clan_members.items(), key=lambda x: (x[1]["role"] != "owner", x[1]["joined_at"]))
        
        for user_id, member_data in sorted_members[:20]:  # Show max 20 members
            role_emoji = "👑" if member_data["role"] == "owner" else "⭐" if member_data["role"] == "officer" else "👤"
            embed.add_field(
                name=f"{role_emoji} User {user_id}",
                value=f"**{member_data['role'].title()}**\nJoined: {datetime.fromisoformat(member_data['joined_at']).strftime('%m/%d/%Y')}",
                inline=True
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🚪 Leave Clan", style=discord.ButtonStyle.danger)
    async def leave_clan_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        success, message = leave_clan(interaction.user.id)
        
        if success:
            embed = discord.Embed(title="✅ Left Clan", description=message, color=0x00ff00)
        else:
            embed = discord.Embed(title="❌ Cannot Leave", description=message, color=0xff0000)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class ClanBrowserView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=300)
        self.user_id = user_id
    
    @discord.ui.select(placeholder="Select a clan to join...", min_values=1, max_values=1)
    async def clan_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        # This would be populated dynamically with clan options
        await interaction.response.send_message("🔄 Clan joining system will be implemented with dropdown population", ephemeral=True)
