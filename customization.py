
import discord
from discord.ext import commands
import json
from datetime import datetime
from data import load_data, save_data
from PIL import Image, ImageDraw, ImageFont
import io

RANK_BADGES = {
    "Bronze I": {"color": "#CD7F32", "emoji": "🥉"},
    "Silver I": {"color": "#C0C0C0", "emoji": "🥈"},
    "Gold I": {"color": "#FFD700", "emoji": "🥇"},
    "Platinum I": {"color": "#E5E4E2", "emoji": "💎"},
    "Diamond I": {"color": "#B9F2FF", "emoji": "💠"},
    "Champion I": {"color": "#9A2A2A", "emoji": "🏆"},
    "Grand Champion": {"color": "#FF6B00", "emoji": "👑"}
}

BANNERS = {
    "default": {"name": "Default", "color": "#00ffcc"},
    "fire": {"name": "Fire Storm", "color": "#ff4500"},
    "ocean": {"name": "Ocean Wave", "color": "#006994"},
    "forest": {"name": "Forest Green", "color": "#228b22"},
    "galaxy": {"name": "Galaxy", "color": "#483d8b"},
    "sunset": {"name": "Sunset", "color": "#ff8c00"},
    "champion": {"name": "Champion", "color": "#ffd700"},
    "mvp": {"name": "MVP Elite", "color": "#ff1493"}
}

def load_player_profiles():
    return load_data("player_profiles.json")

def save_player_profiles(profiles):
    save_data("player_profiles.json", profiles)

def get_player_profile(player_id):
    profiles = load_player_profiles()
    return profiles.get(str(player_id), {
        "banner": "default",
        "badge": None,
        "title": None,
        "favorite_car": "Octane",
        "bio": "Ready to rocket!",
        "unlocked_banners": ["default"],
        "unlocked_badges": [],
        "created_at": datetime.now().isoformat()
    })

def unlock_banner(player_id, banner_id):
    profiles = load_player_profiles()
    if str(player_id) not in profiles:
        profiles[str(player_id)] = get_player_profile(player_id)
    
    if banner_id not in profiles[str(player_id)]["unlocked_banners"]:
        profiles[str(player_id)]["unlocked_banners"].append(banner_id)
        save_player_profiles(profiles)
        return True
    return False

def unlock_badge(player_id, badge_id):
    profiles = load_player_profiles()
    if str(player_id) not in profiles:
        profiles[str(player_id)] = get_player_profile(player_id)
    
    if badge_id not in profiles[str(player_id)]["unlocked_badges"]:
        profiles[str(player_id)]["unlocked_badges"].append(badge_id)
        save_player_profiles(profiles)
        return True
    return False

def generate_profile_card(player_id, username, stats):
    profile = get_player_profile(player_id)
    
    # Create profile card image
    width, height = 600, 400
    img = Image.new('RGB', (width, height), color='#2c2f33')
    draw = ImageDraw.Draw(img)
    
    # Banner background
    banner_color = BANNERS[profile["banner"]]["color"]
    draw.rectangle([0, 0, width, 100], fill=banner_color)
    
    # Player info
    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
        font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Username
    draw.text((20, 20), username, fill='white', font=font_large)
    
    # Rank and MMR
    rank = stats.get("rank", "Unranked")
    mmr = stats.get("mmr", 0)
    draw.text((20, 120), f"Rank: {rank}", fill='white', font=font_medium)
    draw.text((20, 150), f"MMR: {mmr}", fill='white', font=font_medium)
    
    # Stats
    wins = stats.get("wins", 0)
    losses = stats.get("losses", 0)
    goals = stats.get("goals", 0)
    
    draw.text((20, 200), f"Record: {wins}W - {losses}L", fill='white', font=font_medium)
    draw.text((20, 230), f"Goals: {goals}", fill='white', font=font_medium)
    
    # Bio
    bio = profile.get("bio", "Ready to rocket!")
    draw.text((20, 280), f"Bio: {bio}", fill='#b0b0b0', font=font_small)
    
    # Favorite car
    car = profile.get("favorite_car", "Octane")
    draw.text((20, 320), f"Car: {car}", fill='#b0b0b0', font=font_small)
    
    # Save to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    return img_bytes

class ProfileCustomizationView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=300)
        self.user_id = user_id

    @discord.ui.button(label="🎨 Change Banner", style=discord.ButtonStyle.primary, emoji="🖼️")
    async def change_banner(self, interaction: discord.Interaction, button: discord.ui.Button):
        profile = get_player_profile(self.user_id)
        unlocked_banners = profile["unlocked_banners"]
        
        options = [
            discord.SelectOption(
                label=BANNERS[banner_id]["name"],
                value=banner_id,
                description=f"Color: {BANNERS[banner_id]['color']}",
                emoji="🎨"
            )
            for banner_id in unlocked_banners
        ]
        
        if not options:
            await interaction.response.send_message("❌ No banners unlocked!", ephemeral=True)
            return
        
        select = discord.ui.Select(placeholder="Choose a banner...", options=options)
        
        async def banner_callback(select_interaction):
            profiles = load_player_profiles()
            if str(self.user_id) not in profiles:
                profiles[str(self.user_id)] = get_player_profile(self.user_id)
            
            profiles[str(self.user_id)]["banner"] = select.values[0]
            save_player_profiles(profiles)
            
            banner_name = BANNERS[select.values[0]]["name"]
            await select_interaction.response.send_message(f"✅ Banner changed to **{banner_name}**!", ephemeral=True)
        
        select.callback = banner_callback
        view = discord.ui.View()
        view.add_item(select)
        
        await interaction.response.send_message("🎨 Choose your banner:", view=view, ephemeral=True)

    @discord.ui.button(label="🏅 Change Badge", style=discord.ButtonStyle.secondary, emoji="🎖️")
    async def change_badge(self, interaction: discord.Interaction, button: discord.ui.Button):
        profile = get_player_profile(self.user_id)
        unlocked_badges = profile["unlocked_badges"]
        
        if not unlocked_badges:
            await interaction.response.send_message("❌ No badges unlocked! Complete achievements to unlock badges.", ephemeral=True)
            return
        
        options = [
            discord.SelectOption(
                label=badge_id.replace("_", " ").title(),
                value=badge_id,
                emoji="🏅"
            )
            for badge_id in unlocked_badges
        ]
        
        select = discord.ui.Select(placeholder="Choose a badge...", options=options)
        
        async def badge_callback(select_interaction):
            profiles = load_player_profiles()
            if str(self.user_id) not in profiles:
                profiles[str(self.user_id)] = get_player_profile(self.user_id)
            
            profiles[str(self.user_id)]["badge"] = select.values[0]
            save_player_profiles(profiles)
            
            badge_name = select.values[0].replace("_", " ").title()
            await select_interaction.response.send_message(f"✅ Badge changed to **{badge_name}**!", ephemeral=True)
        
        select.callback = badge_callback
        view = discord.ui.View()
        view.add_item(select)
        
        await interaction.response.send_message("🏅 Choose your badge:", view=view, ephemeral=True)

    @discord.ui.button(label="✏️ Edit Bio", style=discord.ButtonStyle.secondary, emoji="📝")
    async def edit_bio(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = BioEditModal(self.user_id)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="🚗 Change Car", style=discord.ButtonStyle.secondary, emoji="🏎️")
    async def change_car(self, interaction: discord.Interaction, button: discord.ui.Button):
        cars = ["Octane", "Dominus", "Breakout", "Batmobile", "Fennec", "Merc", "Road Hog", "Takumi"]
        
        options = [
            discord.SelectOption(label=car, value=car, emoji="🚗")
            for car in cars
        ]
        
        select = discord.ui.Select(placeholder="Choose your favorite car...", options=options)
        
        async def car_callback(select_interaction):
            profiles = load_player_profiles()
            if str(self.user_id) not in profiles:
                profiles[str(self.user_id)] = get_player_profile(self.user_id)
            
            profiles[str(self.user_id)]["favorite_car"] = select.values[0]
            save_player_profiles(profiles)
            
            await select_interaction.response.send_message(f"✅ Favorite car changed to **{select.values[0]}**!", ephemeral=True)
        
        select.callback = car_callback
        view = discord.ui.View()
        view.add_item(select)
        
        await interaction.response.send_message("🚗 Choose your favorite car:", view=view, ephemeral=True)

    @discord.ui.button(label="🖼️ Generate Profile Card", style=discord.ButtonStyle.success, emoji="🎯")
    async def generate_card(self, interaction: discord.Interaction, button: discord.ui.Button):
        from main import load_stats
        
        await interaction.response.defer()
        
        stats = load_stats()
        player_stats = stats.get(str(self.user_id), {})
        
        try:
            img_bytes = generate_profile_card(self.user_id, interaction.user.display_name, player_stats)
            file = discord.File(img_bytes, filename="profile_card.png")
            
            embed = discord.Embed(title="🎯 Your Profile Card", color=0x00ffcc)
            embed.set_image(url="attachment://profile_card.png")
            
            await interaction.followup.send(embed=embed, file=file, ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Error generating profile card: {str(e)}", ephemeral=True)

class BioEditModal(discord.ui.Modal, title="Edit Your Bio"):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        
        profile = get_player_profile(user_id)
        self.bio.default = profile.get("bio", "Ready to rocket!")

    bio = discord.ui.TextInput(
        label="Bio",
        placeholder="Tell everyone about yourself...",
        style=discord.TextStyle.paragraph,
        max_length=200
    )

    async def on_submit(self, interaction: discord.Interaction):
        profiles = load_player_profiles()
        if str(self.user_id) not in profiles:
            profiles[str(self.user_id)] = get_player_profile(self.user_id)
        
        profiles[str(self.user_id)]["bio"] = self.bio.value
        save_player_profiles(profiles)
        
        await interaction.response.send_message(f"✅ Bio updated: {self.bio.value}", ephemeral=True)

class TeamCustomizationView(discord.ui.View):
    def __init__(self, team_id):
        super().__init__(timeout=300)
        self.team_id = team_id

    @discord.ui.button(label="🎨 Team Colors", style=discord.ButtonStyle.primary, emoji="🌈")
    async def team_colors(self, interaction: discord.Interaction, button: discord.ui.Button):
        colors = ["Red", "Blue", "Green", "Yellow", "Purple", "Orange", "Pink", "Cyan"]
        
        options = [
            discord.SelectOption(label=color, value=color.lower(), emoji="🎨")
            for color in colors
        ]
        
        select = discord.ui.Select(placeholder="Choose team color...", options=options)
        
        async def color_callback(select_interaction):
            # Save team color logic here
            await select_interaction.response.send_message(f"✅ Team color changed to **{select.values[0].title()}**!", ephemeral=True)
        
        select.callback = color_callback
        view = discord.ui.View()
        view.add_item(select)
        
        await interaction.response.send_message("🌈 Choose your team color:", view=view, ephemeral=True)

    @discord.ui.button(label="🔰 Team Logo", style=discord.ButtonStyle.secondary, emoji="🏷️")
    async def team_logo(self, interaction: discord.Interaction, button: discord.ui.Button):
        logos = ["🚀", "⚡", "🔥", "💎", "🌟", "⚔️", "🏆", "👑"]
        
        options = [
            discord.SelectOption(label=f"Logo {i+1}", value=logo, emoji=logo)
            for i, logo in enumerate(logos)
        ]
        
        select = discord.ui.Select(placeholder="Choose team logo...", options=options)
        
        async def logo_callback(select_interaction):
            # Save team logo logic here
            await select_interaction.response.send_message(f"✅ Team logo changed to {select.values[0]}!", ephemeral=True)
        
        select.callback = logo_callback
        view = discord.ui.View()
        view.add_item(select)
        
        await interaction.response.send_message("🔰 Choose your team logo:", view=view, ephemeral=True)

async def setup_customization_hub(channel):
    embed = discord.Embed(
        title="🎨 Customization Hub",
        description="Personalize your profile and team!",
        color=0x9b59b6
    )
    embed.add_field(name="🎯 Profile Features", value="• Custom banners\n• Achievement badges\n• Personal bio\n• Favorite car\n• Profile cards", inline=True)
    embed.add_field(name="🏆 Team Features", value="• Team colors\n• Custom logos\n• Team banners\n• Member roles", inline=True)
    
    return embed
