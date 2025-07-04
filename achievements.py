
import discord
from discord.ext import commands
import json
from datetime import datetime
from data import load_data, save_data

ACHIEVEMENTS = {
    "first_blood": {
        "name": "First Blood",
        "description": "Score the first goal in a match",
        "emoji": "🩸",
        "rarity": "Common",
        "mmr_bonus": 5
    },
    "hat_trick_hero": {
        "name": "Hat Trick Hero",
        "description": "Score 3+ goals in a single match",
        "emoji": "🎩",
        "rarity": "Rare",
        "mmr_bonus": 15
    },
    "wall_warrior": {
        "name": "Wall Warrior",
        "description": "Score an aerial goal",
        "emoji": "🧗",
        "rarity": "Epic",
        "mmr_bonus": 10
    },
    "clutch_king": {
        "name": "Clutch King",
        "description": "Win a match in overtime",
        "emoji": "👑",
        "rarity": "Legendary",
        "mmr_bonus": 25
    },
    "save_master": {
        "name": "Save Master",
        "description": "Make 5+ saves in a match",
        "emoji": "🛡️",
        "rarity": "Rare",
        "mmr_bonus": 12
    },
    "assist_king": {
        "name": "Assist King",
        "description": "Get 3+ assists in a match",
        "emoji": "🤝",
        "rarity": "Uncommon",
        "mmr_bonus": 8
    },
    "perfect_game": {
        "name": "Perfect Game",
        "description": "Win without conceding a goal",
        "emoji": "💎",
        "rarity": "Epic",
        "mmr_bonus": 20
    },
    "comeback_kid": {
        "name": "Comeback Kid",
        "description": "Win after being 2+ goals down",
        "emoji": "🔥",
        "rarity": "Legendary",
        "mmr_bonus": 30
    },
    "mvp_streak": {
        "name": "MVP Streak",
        "description": "Win MVP in 3 consecutive matches",
        "emoji": "⭐",
        "rarity": "Mythic",
        "mmr_bonus": 50
    },
    "tournament_winner": {
        "name": "Tournament Champion",
        "description": "Win a tournament",
        "emoji": "🏆",
        "rarity": "Legendary",
        "mmr_bonus": 100
    }
}

def load_achievements():
    return load_data("achievements.json")

def save_achievements(achievements):
    save_data("achievements.json", achievements)

def check_achievements(player_id, match_data):
    achievements = load_achievements()
    if str(player_id) not in achievements:
        achievements[str(player_id)] = {"unlocked": [], "progress": {}}
    
    player_achievements = achievements[str(player_id)]
    new_achievements = []
    
    # Check First Blood
    if "first_blood" not in player_achievements["unlocked"]:
        if match_data.get("first_goal_scorer") == player_id:
            player_achievements["unlocked"].append("first_blood")
            new_achievements.append("first_blood")
    
    # Check Hat Trick Hero
    if "hat_trick_hero" not in player_achievements["unlocked"]:
        if match_data.get("player_goals", 0) >= 3:
            player_achievements["unlocked"].append("hat_trick_hero")
            new_achievements.append("hat_trick_hero")
    
    # Check Wall Warrior (aerial goals)
    if "wall_warrior" not in player_achievements["unlocked"]:
        if match_data.get("aerial_goals", 0) > 0:
            player_achievements["unlocked"].append("wall_warrior")
            new_achievements.append("wall_warrior")
    
    # Check Clutch King (overtime wins)
    if "clutch_king" not in player_achievements["unlocked"]:
        if match_data.get("overtime_win", False) and match_data.get("won", False):
            player_achievements["unlocked"].append("clutch_king")
            new_achievements.append("clutch_king")
    
    # Check Save Master
    if "save_master" not in player_achievements["unlocked"]:
        if match_data.get("saves", 0) >= 5:
            player_achievements["unlocked"].append("save_master")
            new_achievements.append("save_master")
    
    # Check Assist King
    if "assist_king" not in player_achievements["unlocked"]:
        if match_data.get("assists", 0) >= 3:
            player_achievements["unlocked"].append("assist_king")
            new_achievements.append("assist_king")
    
    # Check Perfect Game
    if "perfect_game" not in player_achievements["unlocked"]:
        if match_data.get("won", False) and match_data.get("goals_conceded", 0) == 0:
            player_achievements["unlocked"].append("perfect_game")
            new_achievements.append("perfect_game")
    
    # Check Comeback Kid
    if "comeback_kid" not in player_achievements["unlocked"]:
        if match_data.get("won", False) and match_data.get("max_deficit", 0) >= 2:
            player_achievements["unlocked"].append("comeback_kid")
            new_achievements.append("comeback_kid")
    
    save_achievements(achievements)
    return new_achievements

def create_achievement_embed(achievement_id, player_name):
    achievement = ACHIEVEMENTS[achievement_id]
    
    rarity_colors = {
        "Common": 0x95a5a6,
        "Uncommon": 0x27ae60,
        "Rare": 0x3498db,
        "Epic": 0x9b59b6,
        "Legendary": 0xf39c12,
        "Mythic": 0xe74c3c
    }
    
    embed = discord.Embed(
        title=f"{achievement['emoji']} Achievement Unlocked!",
        description=f"**{player_name}** earned **{achievement['name']}**",
        color=rarity_colors.get(achievement['rarity'], 0x95a5a6)
    )
    embed.add_field(name="Description", value=achievement['description'], inline=False)
    embed.add_field(name="Rarity", value=achievement['rarity'], inline=True)
    embed.add_field(name="MMR Bonus", value=f"+{achievement['mmr_bonus']}", inline=True)
    
    return embed

class AchievementView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=300)
        self.user_id = user_id
    
    @discord.ui.button(label="🏆 View All Achievements", style=discord.ButtonStyle.primary)
    async def view_all_achievements(self, interaction: discord.Interaction, button: discord.ui.Button):
        achievements = load_achievements()
        player_achievements = achievements.get(str(self.user_id), {"unlocked": []})
        
        embed = discord.Embed(title="🏆 All Achievements", color=0xFFD700)
        
        unlocked_count = len(player_achievements["unlocked"])
        total_count = len(ACHIEVEMENTS)
        
        embed.description = f"**{unlocked_count}/{total_count}** achievements unlocked"
        
        for achievement_id, achievement in ACHIEVEMENTS.items():
            status = "✅" if achievement_id in player_achievements["unlocked"] else "❌"
            embed.add_field(
                name=f"{status} {achievement['emoji']} {achievement['name']}",
                value=f"{achievement['description']}\n**{achievement['rarity']}** • +{achievement['mmr_bonus']} MMR",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="📊 Progress", style=discord.ButtonStyle.secondary)
    async def view_progress(self, interaction: discord.Interaction, button: discord.ui.Button):
        achievements = load_achievements()
        player_achievements = achievements.get(str(self.user_id), {"unlocked": [], "progress": {}})
        
        embed = discord.Embed(title="📊 Achievement Progress", color=0x00ffcc)
        
        # Show recent achievements
        recent = player_achievements["unlocked"][-5:] if player_achievements["unlocked"] else []
        if recent:
            recent_text = "\n".join([f"• {ACHIEVEMENTS[ach]['emoji']} {ACHIEVEMENTS[ach]['name']}" for ach in recent])
            embed.add_field(name="🎯 Recent Unlocks", value=recent_text, inline=False)
        
        # Show rarity breakdown
        rarity_counts = {}
        for ach_id in player_achievements["unlocked"]:
            rarity = ACHIEVEMENTS[ach_id]["rarity"]
            rarity_counts[rarity] = rarity_counts.get(rarity, 0) + 1
        
        if rarity_counts:
            rarity_text = "\n".join([f"• {rarity}: {count}" for rarity, count in rarity_counts.items()])
            embed.add_field(name="🎖️ By Rarity", value=rarity_text, inline=False)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
