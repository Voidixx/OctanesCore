
import discord
from discord.ext import commands
import json
import random
from datetime import datetime, timedelta
from data import load_data, save_data
from utils import *

SHOP_ITEMS = {
    "banner_fire": {"name": "🔥 Fire Banner", "price": 500, "type": "banner", "value": "fire"},
    "banner_galaxy": {"name": "🌌 Galaxy Banner", "price": 750, "type": "banner", "value": "galaxy"},
    "banner_champion": {"name": "🏆 Champion Banner", "price": 1000, "type": "banner", "value": "champion"},
    "mmr_boost": {"name": "📈 MMR Boost (+50)", "price": 300, "type": "boost", "value": 50},
    "lucky_box": {"name": "🎁 Lucky Box", "price": 200, "type": "box", "value": "random_reward"},
    "name_change": {"name": "✨ Custom Display Name", "price": 800, "type": "name", "value": "custom_name"},
    "vip_status": {"name": "👑 VIP Status (7 days)", "price": 1500, "type": "vip", "value": 7},
    "tournament_entry": {"name": "🎟️ Premium Tournament Entry", "price": 400, "type": "tournament", "value": "premium"},
    "profile_badge": {"name": "🏅 Custom Profile Badge", "price": 600, "type": "badge", "value": "custom"},
    "queue_priority": {"name": "⚡ Queue Priority (24h)", "price": 250, "type": "priority", "value": 24}
}

def load_economy():
    return load_data("economy.json")

def save_economy(economy):
    save_data("economy.json", economy)

def get_player_economy(user_id):
    economy = load_economy()
    if str(user_id) not in economy:
        economy[str(user_id)] = {
            "credits": 100,  # Starting credits
            "daily_streak": 0,
            "last_daily": None,
            "total_earned": 100,
            "total_spent": 0,
            "purchases": [],
            "vip_until": None,
            "inventory": []
        }
        save_economy(economy)
    return economy[str(user_id)]

def add_credits(user_id, amount, reason="Unknown"):
    economy = load_economy()
    player = get_player_economy(user_id)
    player["credits"] += amount
    player["total_earned"] += amount
    
    # Log transaction
    transaction = {
        "type": "earned",
        "amount": amount,
        "reason": reason,
        "timestamp": datetime.now().isoformat()
    }
    
    if "transactions" not in player:
        player["transactions"] = []
    player["transactions"].append(transaction)
    
    economy[str(user_id)] = player
    save_economy(economy)
    return player["credits"]

def spend_credits(user_id, amount, reason="Purchase"):
    economy = load_economy()
    player = get_player_economy(user_id)
    
    if player["credits"] < amount:
        return False
    
    player["credits"] -= amount
    player["total_spent"] += amount
    
    # Log transaction
    transaction = {
        "type": "spent",
        "amount": amount,
        "reason": reason,
        "timestamp": datetime.now().isoformat()
    }
    
    if "transactions" not in player:
        player["transactions"] = []
    player["transactions"].append(transaction)
    
    economy[str(user_id)] = player
    save_economy(economy)
    return True

def claim_daily_reward(user_id):
    economy = load_economy()
    player = get_player_economy(user_id)
    
    now = datetime.now()
    last_daily = player.get("last_daily")
    
    if last_daily:
        last_date = datetime.fromisoformat(last_daily)
        if (now - last_date).days < 1:
            return None, player["daily_streak"]
    
    # Calculate reward based on streak
    base_reward = 50
    streak_bonus = min(player["daily_streak"] * 10, 200)  # Max 200 bonus
    total_reward = base_reward + streak_bonus
    
    # Random bonus chance
    if random.random() < 0.1:  # 10% chance
        bonus = random.randint(50, 200)
        total_reward += bonus
    
    # Update streak
    if last_daily and (now - datetime.fromisoformat(last_daily)).days == 1:
        player["daily_streak"] += 1
    else:
        player["daily_streak"] = 1
    
    player["last_daily"] = now.isoformat()
    add_credits(user_id, total_reward, "Daily reward")
    
    economy[str(user_id)] = player
    save_economy(economy)
    
    return total_reward, player["daily_streak"]

class EconomyView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=300)
        self.user_id = user_id
    
    @discord.ui.button(label="💰 Balance", style=discord.ButtonStyle.primary)
    async def view_balance(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ This is not your economy panel!", ephemeral=True)
            return
        
        player = get_player_economy(self.user_id)
        
        embed = discord.Embed(title="💰 Your Economy Stats", color=0x00ff00)
        embed.add_field(name="💳 Current Balance", value=f"**{player['credits']:,}** credits", inline=True)
        embed.add_field(name="📈 Total Earned", value=f"{player['total_earned']:,} credits", inline=True)
        embed.add_field(name="💸 Total Spent", value=f"{player['total_spent']:,} credits", inline=True)
        embed.add_field(name="🔥 Daily Streak", value=f"**{player['daily_streak']}** days", inline=True)
        
        # VIP Status
        vip_status = "None"
        if player.get("vip_until"):
            vip_date = datetime.fromisoformat(player["vip_until"])
            if datetime.now() < vip_date:
                days_left = (vip_date - datetime.now()).days
                vip_status = f"VIP ({days_left} days left)"
        
        embed.add_field(name="👑 VIP Status", value=vip_status, inline=True)
        embed.add_field(name="🛍️ Items Purchased", value=str(len(player.get("purchases", []))), inline=True)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🎁 Daily Reward", style=discord.ButtonStyle.success)
    async def daily_reward(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ This is not your economy panel!", ephemeral=True)
            return
        
        reward, streak = claim_daily_reward(self.user_id)
        
        if reward is None:
            embed = discord.Embed(title="⏰ Daily Reward", description="You've already claimed your daily reward today!", color=0xff0000)
            embed.add_field(name="⏱️ Next Reward", value="Available in less than 24 hours", inline=False)
        else:
            embed = discord.Embed(title="🎁 Daily Reward Claimed!", color=0x00ff00)
            embed.add_field(name="💰 Reward", value=f"**+{reward}** credits", inline=True)
            embed.add_field(name="🔥 Streak", value=f"**{streak}** days", inline=True)
            embed.add_field(name="💡 Tip", value="Come back tomorrow for an even bigger reward!", inline=False)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🛍️ Shop", style=discord.ButtonStyle.secondary)
    async def open_shop(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ This is not your economy panel!", ephemeral=True)
            return
        
        embed = discord.Embed(title="🛍️ OctaneCore Shop", description="Purchase items with your credits!", color=0x9b59b6)
        
        for item_id, item in list(SHOP_ITEMS.items())[:8]:  # Show first 8 items
            embed.add_field(
                name=f"{item['name']} - {item['price']} credits",
                value=f"Type: {item['type'].title()}",
                inline=True
            )
        
        view = ShopView(self.user_id)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class ShopView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=300)
        self.user_id = user_id
        
        # Add shop item buttons
        for item_id, item in list(SHOP_ITEMS.items())[:5]:  # First 5 items as buttons
            button = discord.ui.Button(
                label=f"{item['name']} ({item['price']})",
                style=discord.ButtonStyle.secondary,
                custom_id=f"buy_{item_id}"
            )
            button.callback = self.create_purchase_callback(item_id)
            self.add_item(button)
    
    def create_purchase_callback(self, item_id):
        async def purchase_callback(interaction):
            if interaction.user.id != self.user_id:
                await interaction.response.send_message("❌ This is not your shop!", ephemeral=True)
                return
            
            item = SHOP_ITEMS[item_id]
            player = get_player_economy(self.user_id)
            
            if player["credits"] < item["price"]:
                await interaction.response.send_message(f"❌ Insufficient credits! You need {item['price']} credits but only have {player['credits']}.", ephemeral=True)
                return
            
            # Process purchase
            if spend_credits(self.user_id, item["price"], f"Purchased {item['name']}"):
                # Add item to inventory
                economy = load_economy()
                player = economy[str(self.user_id)]
                player["purchases"].append({
                    "item_id": item_id,
                    "item_name": item["name"],
                    "price": item["price"],
                    "purchased_at": datetime.now().isoformat()
                })
                
                if "inventory" not in player:
                    player["inventory"] = []
                player["inventory"].append(item_id)
                
                # Apply item effects
                if item["type"] == "banner":
                    from customization import unlock_banner
                    unlock_banner(self.user_id, item["value"])
                elif item["type"] == "boost":
                    # Apply MMR boost
                    stats = load_stats()
                    if str(self.user_id) in stats:
                        stats[str(self.user_id)]["mmr"] += item["value"]
                        save_stats(stats)
                elif item["type"] == "vip":
                    vip_until = datetime.now() + timedelta(days=item["value"])
                    player["vip_until"] = vip_until.isoformat()
                
                economy[str(self.user_id)] = player
                save_economy(economy)
                
                embed = discord.Embed(title="✅ Purchase Successful!", color=0x00ff00)
                embed.add_field(name="Item", value=item["name"], inline=True)
                embed.add_field(name="Price", value=f"{item['price']} credits", inline=True)
                embed.add_field(name="New Balance", value=f"{player['credits']} credits", inline=True)
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message("❌ Purchase failed!", ephemeral=True)
        
        return purchase_callback

# Economy reward functions for integration with other systems
def reward_match_completion(user_id, won=False):
    base_reward = 25
    win_bonus = 15 if won else 0
    total = base_reward + win_bonus
    add_credits(user_id, total, "Match completion")
    return total

def reward_tournament_participation(user_id, placement=None):
    base_reward = 50
    if placement == 1:
        bonus = 200
    elif placement == 2:
        bonus = 100
    elif placement == 3:
        bonus = 50
    else:
        bonus = 0
    
    total = base_reward + bonus
    add_credits(user_id, total, f"Tournament participation (#{placement})" if placement else "Tournament participation")
    return total

def reward_achievement_unlock(user_id, achievement_id):
    rewards = {
        "first_blood": 25,
        "hat_trick_hero": 50,
        "wall_warrior": 40,
        "clutch_king": 75,
        "save_master": 45,
        "assist_king": 35,
        "perfect_game": 60,
        "comeback_kid": 80,
        "mvp_streak": 150,
        "tournament_winner": 300
    }
    
    reward = rewards.get(achievement_id, 20)
    add_credits(user_id, reward, f"Achievement: {achievement_id}")
    return reward
