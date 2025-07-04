
import discord
from discord.ext import commands
import json
from datetime import datetime, timedelta
from data import load_data, save_data

def load_moderation_logs():
    return load_data("moderation_logs.json")

def save_moderation_logs(logs):
    save_data("moderation_logs.json", logs)

def load_server_config():
    return load_data("server_config.json")

def save_server_config(config):
    save_data("server_config.json", config)

def log_moderation_action(guild_id, moderator_id, action, target_id, reason=None):
    logs = load_moderation_logs()
    
    if str(guild_id) not in logs:
        logs[str(guild_id)] = []
    
    log_entry = {
        "id": len(logs[str(guild_id)]) + 1,
        "timestamp": datetime.now().isoformat(),
        "moderator_id": moderator_id,
        "action": action,
        "target_id": target_id,
        "reason": reason or "No reason provided"
    }
    
    logs[str(guild_id)].append(log_entry)
    save_moderation_logs(logs)
    return log_entry

class ModerationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
    
    @discord.ui.button(label="🛡️ Quick Actions", style=discord.ButtonStyle.primary)
    async def quick_actions(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.response.send_message("❌ You need moderation permissions!", ephemeral=True)
            return
        
        embed = discord.Embed(title="🛡️ Quick Moderation", description="Fast access to common moderation actions", color=0xff6600)
        embed.add_field(name="Available Actions", value="• Timeout members\n• Clear recent queue joins\n• Reset match disputes\n• Manage tournament bans\n• View moderation logs", inline=False)
        
        view = QuickModerationView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @discord.ui.button(label="⚙️ Server Config", style=discord.ButtonStyle.secondary)
    async def server_config(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Administrator only!", ephemeral=True)
            return
        
        config = load_server_config()
        guild_config = config.get(str(interaction.guild.id), {
            "auto_role": None,
            "welcome_channel": None,
            "log_channel": None,
            "queue_cooldown": 30,
            "max_daily_tournaments": 5,
            "economy_enabled": True,
            "clan_system_enabled": True
        })
        
        embed = discord.Embed(title="⚙️ Server Configuration", color=0x9b59b6)
        embed.add_field(name="🎭 Auto Role", value=f"<@&{guild_config['auto_role']}>" if guild_config['auto_role'] else "None", inline=True)
        embed.add_field(name="👋 Welcome Channel", value=f"<#{guild_config['welcome_channel']}>" if guild_config['welcome_channel'] else "None", inline=True)
        embed.add_field(name="📝 Log Channel", value=f"<#{guild_config['log_channel']}>" if guild_config['log_channel'] else "None", inline=True)
        embed.add_field(name="⏱️ Queue Cooldown", value=f"{guild_config['queue_cooldown']}s", inline=True)
        embed.add_field(name="🏆 Daily Tournaments", value=f"Max {guild_config['max_daily_tournaments']}", inline=True)
        embed.add_field(name="💰 Economy", value="✅ Enabled" if guild_config['economy_enabled'] else "❌ Disabled", inline=True)
        
        view = ServerConfigView(interaction.guild.id)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @discord.ui.button(label="📋 Mod Logs", style=discord.ButtonStyle.danger)
    async def mod_logs(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.view_audit_log:
            await interaction.response.send_message("❌ You need audit log permissions!", ephemeral=True)
            return
        
        logs = load_moderation_logs()
        guild_logs = logs.get(str(interaction.guild.id), [])
        
        if not guild_logs:
            await interaction.response.send_message("📋 No moderation logs found for this server.", ephemeral=True)
            return
        
        embed = discord.Embed(title="📋 Recent Moderation Actions", color=0xff0000)
        
        # Show last 10 actions
        for log in guild_logs[-10:]:
            timestamp = datetime.fromisoformat(log['timestamp']).strftime("%m/%d %H:%M")
            embed.add_field(
                name=f"#{log['id']} - {log['action'].title()}",
                value=f"**Moderator:** <@{log['moderator_id']}>\n**Target:** <@{log['target_id']}>\n**Time:** {timestamp}\n**Reason:** {log['reason']}",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class QuickModerationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
    
    @discord.ui.button(label="🔇 Clear Queue Abuse", style=discord.ButtonStyle.danger)
    async def clear_queue_abuse(self, interaction: discord.Interaction, button: discord.ui.Button):
        from utils import load_queue, save_queue
        
        queue = load_queue()
        original_count = len(queue)
        
        # Remove players who joined in the last minute (potential spam)
        now = datetime.now()
        filtered_queue = []
        
        for player in queue:
            join_time = datetime.fromisoformat(player['joined_at'])
            if (now - join_time).seconds > 60:  # Keep players who joined more than 1 minute ago
                filtered_queue.append(player)
        
        save_queue(filtered_queue)
        removed = original_count - len(filtered_queue)
        
        # Log action
        log_moderation_action(
            interaction.guild.id,
            interaction.user.id,
            "clear_queue_abuse",
            "system",
            f"Removed {removed} recent queue joins"
        )
        
        embed = discord.Embed(title="✅ Queue Cleaned", color=0x00ff00)
        embed.add_field(name="Action", value=f"Removed {removed} recent queue entries", inline=False)
        embed.add_field(name="Remaining", value=f"{len(filtered_queue)} players in queue", inline=False)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🏆 Reset Tournament", style=discord.ButtonStyle.secondary)
    async def reset_tournament(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = TournamentResetModal()
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="💰 Economy Action", style=discord.ButtonStyle.primary)
    async def economy_action(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="💰 Economy Moderation", color=0x00ffcc)
        embed.add_field(name="Available Actions", value="• Add/Remove credits from user\n• Reset user economy\n• View top economy users\n• Adjust shop prices", inline=False)
        
        view = EconomyModerationView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class TournamentResetModal(discord.ui.Modal, title="Reset Tournament"):
    def __init__(self):
        super().__init__()
    
    tournament_id = discord.ui.TextInput(
        label="Tournament ID",
        placeholder="Enter tournament ID to reset",
        max_length=50
    )
    
    reason = discord.ui.TextInput(
        label="Reason",
        placeholder="Why are you resetting this tournament?",
        style=discord.TextStyle.paragraph,
        max_length=200
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        from utils import load_tournaments, save_tournaments
        
        tournaments = load_tournaments()
        tournament = next((t for t in tournaments if t["id"] == self.tournament_id.value), None)
        
        if not tournament:
            await interaction.response.send_message("❌ Tournament not found!", ephemeral=True)
            return
        
        # Reset tournament to registration phase
        tournament["status"] = "registration"
        tournament["teams"] = []
        tournament["matches"] = []
        tournament["current_round"] = 0
        
        save_tournaments(tournaments)
        
        # Log action
        log_moderation_action(
            interaction.guild.id,
            interaction.user.id,
            "tournament_reset",
            self.tournament_id.value,
            self.reason.value
        )
        
        embed = discord.Embed(title="✅ Tournament Reset", color=0x00ff00)
        embed.add_field(name="Tournament", value=self.tournament_id.value, inline=False)
        embed.add_field(name="Reason", value=self.reason.value, inline=False)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class EconomyModerationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
    
    @discord.ui.button(label="💳 Adjust Credits", style=discord.ButtonStyle.primary)
    async def adjust_credits(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = CreditAdjustmentModal()
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="📊 Economy Stats", style=discord.ButtonStyle.secondary)
    async def economy_stats(self, interaction: discord.Interaction, button: discord.ui.Button):
        from economy import load_economy
        
        economy = load_economy()
        
        if not economy:
            await interaction.response.send_message("📊 No economy data found.", ephemeral=True)
            return
        
        total_credits = sum(player["credits"] for player in economy.values())
        avg_credits = total_credits / len(economy)
        top_player = max(economy.items(), key=lambda x: x[1]["credits"])
        
        embed = discord.Embed(title="📊 Server Economy Stats", color=0x00ffcc)
        embed.add_field(name="👥 Active Users", value=str(len(economy)), inline=True)
        embed.add_field(name="💰 Total Credits", value=f"{total_credits:,}", inline=True)
        embed.add_field(name="📈 Average Credits", value=f"{avg_credits:.0f}", inline=True)
        embed.add_field(name="🏆 Richest Player", value=f"<@{top_player[0]}>\n{top_player[1]['credits']:,} credits", inline=False)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class CreditAdjustmentModal(discord.ui.Modal, title="Adjust User Credits"):
    def __init__(self):
        super().__init__()
    
    user_id = discord.ui.TextInput(
        label="User ID",
        placeholder="Enter Discord user ID",
        max_length=20
    )
    
    amount = discord.ui.TextInput(
        label="Credit Amount",
        placeholder="Use + to add, - to remove (e.g., +500 or -200)",
        max_length=10
    )
    
    reason = discord.ui.TextInput(
        label="Reason",
        placeholder="Reason for credit adjustment",
        max_length=100
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        from economy import add_credits, spend_credits, get_player_economy
        
        try:
            user_id = int(self.user_id.value)
            amount_str = self.amount.value.strip()
            
            if amount_str.startswith('+'):
                amount = int(amount_str[1:])
                add_credits(user_id, amount, f"Admin adjustment: {self.reason.value}")
                action = f"Added {amount} credits"
            elif amount_str.startswith('-'):
                amount = int(amount_str[1:])
                spend_credits(user_id, amount, f"Admin adjustment: {self.reason.value}")
                action = f"Removed {amount} credits"
            else:
                await interaction.response.send_message("❌ Amount must start with + or -", ephemeral=True)
                return
            
            # Log action
            log_moderation_action(
                interaction.guild.id,
                interaction.user.id,
                "credit_adjustment",
                user_id,
                f"{action} - {self.reason.value}"
            )
            
            new_balance = get_player_economy(user_id)["credits"]
            
            embed = discord.Embed(title="✅ Credits Adjusted", color=0x00ff00)
            embed.add_field(name="User", value=f"<@{user_id}>", inline=True)
            embed.add_field(name="Action", value=action, inline=True)
            embed.add_field(name="New Balance", value=f"{new_balance:,} credits", inline=True)
            embed.add_field(name="Reason", value=self.reason.value, inline=False)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except ValueError:
            await interaction.response.send_message("❌ Invalid user ID or amount format!", ephemeral=True)

class ServerConfigView(discord.ui.View):
    def __init__(self, guild_id):
        super().__init__(timeout=300)
        self.guild_id = guild_id
    
    @discord.ui.button(label="🎭 Set Auto Role", style=discord.ButtonStyle.primary)
    async def set_auto_role(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="🎭 Auto Role Setup", description="Select a role to automatically assign to new members when they use the bot for the first time.", color=0x00ffcc)
        
        # Create role select menu
        options = []
        for role in interaction.guild.roles:
            if role != interaction.guild.default_role and not role.managed and len(options) < 25:
                options.append(discord.SelectOption(label=role.name, value=str(role.id), description=f"Members: {len(role.members)}"))
        
        if not options:
            await interaction.response.send_message("❌ No suitable roles found!", ephemeral=True)
            return
        
        select = discord.ui.Select(placeholder="Choose auto role...", options=options)
        
        async def role_callback(select_interaction):
            config = load_server_config()
            if str(self.guild_id) not in config:
                config[str(self.guild_id)] = {}
            
            config[str(self.guild_id)]["auto_role"] = int(select.values[0])
            save_server_config(config)
            
            role = interaction.guild.get_role(int(select.values[0]))
            await select_interaction.response.send_message(f"✅ Auto role set to {role.mention}", ephemeral=True)
        
        select.callback = role_callback
        view = discord.ui.View()
        view.add_item(select)
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
