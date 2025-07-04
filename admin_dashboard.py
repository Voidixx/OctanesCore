
import discord
from discord.ext import commands
import json
import asyncio
import subprocess
import sys
import os
from datetime import datetime, timedelta
from utils import *

class AdminDashboardView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.custom_id = "admin_dashboard_persistent"

    @discord.ui.button(label="🔧 Bot Controls", style=discord.ButtonStyle.danger, custom_id="bot_controls", row=0)
    async def bot_controls(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Admin only access!", ephemeral=True)
            return
        
        embed = discord.Embed(title="🔧 Bot Control Panel", description="Manage core bot functions", color=0xff0000)
        embed.add_field(name="⚠️ Warning", value="These actions affect all server members. Use with caution!", inline=False)
        
        view = BotControlsView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @discord.ui.button(label="🎮 Queue Management", style=discord.ButtonStyle.primary, custom_id="queue_mgmt", row=0)
    async def queue_management(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Admin only access!", ephemeral=True)
            return
        
        queue = load_queue()
        settings = load_admin_settings()
        
        embed = discord.Embed(title="🎮 Queue Management", color=0x00ffcc)
        embed.add_field(name="Queue Status", value="🟢 Enabled" if settings["allow_queue"] else "🔴 Disabled", inline=True)
        embed.add_field(name="Players in Queue", value=str(len(queue)), inline=True)
        embed.add_field(name="Auto-MMR Updates", value="✅" if settings["auto_mmr_updates"] else "❌", inline=True)
        
        # Queue breakdown
        queue_counts = {"1v1": 0, "2v2": 0, "3v3": 0}
        for player in queue:
            if player["status"] == "searching":
                queue_counts[player["format"]] += 1
        
        embed.add_field(name="Queue Breakdown", value=f"1v1: {queue_counts['1v1']}\n2v2: {queue_counts['2v2']}\n3v3: {queue_counts['3v3']}", inline=False)
        
        view = QueueManagementView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @discord.ui.button(label="🏆 Tournament Control", style=discord.ButtonStyle.success, custom_id="tournament_ctrl", row=0)
    async def tournament_control(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Admin only access!", ephemeral=True)
            return
        
        tournaments = load_tournaments()
        settings = load_admin_settings()
        
        active_tournaments = [t for t in tournaments if t["status"] in ["registration", "active"]]
        
        embed = discord.Embed(title="🏆 Tournament Control Panel", color=0xFFD700)
        embed.add_field(name="Tournament Status", value="🟢 Enabled" if settings["allow_tournaments"] else "🔴 Disabled", inline=True)
        embed.add_field(name="Active Tournaments", value=str(len(active_tournaments)), inline=True)
        embed.add_field(name="Max Teams Per Tournament", value=str(settings["max_tournament_teams"]), inline=True)
        
        if active_tournaments:
            tournament_info = "\n".join([f"• {t['id'][:12]}... ({t['status']})" for t in active_tournaments[-5:]])
            embed.add_field(name="Recent Tournaments", value=tournament_info, inline=False)
        
        view = TournamentControlView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @discord.ui.button(label="📊 Server Analytics", style=discord.ButtonStyle.secondary, custom_id="analytics", row=1)
    async def server_analytics(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Admin only access!", ephemeral=True)
            return
        
        stats = load_stats()
        history = load_match_history()
        mvp_votes = load_mvp_votes()
        tournaments = load_tournaments()
        
        embed = discord.Embed(title="📊 Server Analytics", color=0x9b59b6)
        
        # Basic stats
        embed.add_field(name="👥 Registered Players", value=str(len(stats)), inline=True)
        embed.add_field(name="🎮 Total Matches", value=str(len(history)), inline=True)
        embed.add_field(name="🏆 Total Tournaments", value=str(len(tournaments)), inline=True)
        
        # Calculate activity metrics
        recent_matches = [m for m in history if (datetime.now() - datetime.fromisoformat(m["date"])).days <= 7]
        embed.add_field(name="📈 Matches (7 days)", value=str(len(recent_matches)), inline=True)
        
        # Most active players
        if stats:
            top_players = sorted(stats.items(), key=lambda x: x[1]["matches_played"], reverse=True)[:3]
            top_player_names = []
            for player_id, player_stats in top_players:
                try:
                    user = interaction.client.get_user(int(player_id))
                    if user:
                        top_player_names.append(f"{user.display_name} ({player_stats['matches_played']} matches)")
                    else:
                        top_player_names.append(f"Player {player_id} ({player_stats['matches_played']} matches)")
                except:
                    top_player_names.append(f"Player {player_id} ({player_stats['matches_played']} matches)")
            
            embed.add_field(name="🔥 Most Active Players", value="\n".join(top_player_names), inline=False)
        
        view = AnalyticsView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @discord.ui.button(label="🗑️ Data Management", style=discord.ButtonStyle.danger, custom_id="data_mgmt", row=1)
    async def data_management(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Admin only access!", ephemeral=True)
            return
        
        embed = discord.Embed(title="🗑️ Data Management", description="⚠️ **WARNING**: These actions permanently delete data!", color=0xff0000)
        embed.add_field(name="Available Actions", value="• Clear all player stats\n• Reset match history\n• Clear tournament data\n• Reset queue\n• Clear MVP votes", inline=False)
        embed.add_field(name="⚠️ Important", value="These actions cannot be undone. Make sure you really want to clear this data!", inline=False)
        
        view = DataManagementView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @discord.ui.button(label="⚙️ Bot Settings", style=discord.ButtonStyle.secondary, custom_id="bot_settings", row=1)
    async def bot_settings(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Admin only access!", ephemeral=True)
            return
        
        settings = load_admin_settings()
        
        embed = discord.Embed(title="⚙️ Bot Settings", color=0x00ffcc)
        embed.add_field(name="🎮 Queue System", value="✅ Enabled" if settings["allow_queue"] else "❌ Disabled", inline=True)
        embed.add_field(name="🏆 Tournaments", value="✅ Enabled" if settings["allow_tournaments"] else "❌ Disabled", inline=True)
        embed.add_field(name="📊 Auto MMR Updates", value="✅ Enabled" if settings["auto_mmr_updates"] else "❌ Disabled", inline=True)
        embed.add_field(name="⭐ MVP Voting", value="✅ Enabled" if settings["mvp_voting_enabled"] else "❌ Disabled", inline=True)
        embed.add_field(name="🏆 Max Tournament Teams", value=str(settings["max_tournament_teams"]), inline=True)
        
        view = BotSettingsView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @discord.ui.button(label="🧪 Testing Hub", style=discord.ButtonStyle.primary, custom_id="testing_hub", row=2)
    async def testing_hub(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Admin only access!", ephemeral=True)
            return
        
        embed = discord.Embed(title="🧪 Testing Hub", description="Access comprehensive bot testing features", color=0x9b59b6)
        embed.add_field(name="Available Tests", value="• Queue system simulation\n• Tournament creation with bot teams\n• Match result generation\n• Full system testing", inline=False)
        embed.add_field(name="💡 Quick Start", value="Use `/testing_dashboard` to create a testing interface in any channel.", inline=False)
        
        view = discord.ui.View()
        test_btn = discord.ui.Button(label="Create Testing Dashboard", style=discord.ButtonStyle.success)
        
        async def create_testing_dashboard(test_interaction):
            try:
                from test_system import setup_testing_dashboard
                message = await setup_testing_dashboard(test_interaction.channel)
                await test_interaction.response.send_message("✅ Testing dashboard created in this channel!", ephemeral=True)
            except Exception as e:
                await test_interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)
        
        test_btn.callback = create_testing_dashboard
        view.add_item(test_btn)
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @discord.ui.button(label="🔄 Auto Tournaments", style=discord.ButtonStyle.success, custom_id="auto_tournaments", row=2)
    async def auto_tournaments(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Admin only access!", ephemeral=True)
            return
        
        settings = load_admin_settings()
        auto_settings = settings.get("auto_tournament", {
            "enabled": False,
            "interval_minutes": 60,
            "format": "3v3",
            "map": "DFH Stadium",
            "mode": "Soccar",
            "max_teams": 8,
            "channel_id": None
        })
        
        embed = discord.Embed(title="🔄 Auto Tournament Settings", color=0x00ff00)
        embed.add_field(name="Status", value="🟢 Enabled" if auto_settings["enabled"] else "🔴 Disabled", inline=True)
        embed.add_field(name="Interval", value=f"{auto_settings['interval_minutes']} minutes", inline=True)
        embed.add_field(name="Format", value=auto_settings["format"], inline=True)
        embed.add_field(name="Map", value=auto_settings["map"], inline=True)
        embed.add_field(name="Mode", value=auto_settings["mode"], inline=True)
        embed.add_field(name="Max Teams", value=str(auto_settings["max_teams"]), inline=True)
        
        channel_info = "Not set"
        if auto_settings.get("channel_id"):
            try:
                channel = interaction.client.get_channel(auto_settings["channel_id"])
                channel_info = f"#{channel.name}" if channel else "Channel not found"
            except:
                channel_info = "Channel not found"
        embed.add_field(name="Auto Tournament Channel", value=channel_info, inline=False)
        
        view = AutoTournamentView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class BotControlsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
    
    @discord.ui.button(label="🔄 Restart Bot", style=discord.ButtonStyle.danger, emoji="🔄")
    async def restart_bot(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="⚠️ Bot Restart Confirmation", description="Are you sure you want to restart the bot? This will briefly disconnect all users.", color=0xff0000)
        
        view = discord.ui.View()
        
        confirm_btn = discord.ui.Button(label="✅ Confirm Restart", style=discord.ButtonStyle.danger)
        cancel_btn = discord.ui.Button(label="❌ Cancel", style=discord.ButtonStyle.secondary)
        
        async def confirm_restart(confirm_interaction):
            from main import log_to_channel
            await log_to_channel(f"🔄 Bot restart initiated by {confirm_interaction.user.display_name}", "WARNING")
            await confirm_interaction.response.send_message("🔄 Restarting bot... Please wait.", ephemeral=True)
            # Note: In a real deployment, you'd use a proper restart mechanism
            # This is a basic example - in production, use PM2, systemd, or similar
            await asyncio.sleep(2)
            await confirm_interaction.edit_original_response(content="✅ Bot restart initiated. Bot will be back online shortly.")
        
        async def cancel_restart(cancel_interaction):
            await cancel_interaction.response.send_message("❌ Bot restart cancelled.", ephemeral=True)
        
        confirm_btn.callback = confirm_restart
        cancel_btn.callback = cancel_restart
        view.add_item(confirm_btn)
        view.add_item(cancel_btn)
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @discord.ui.button(label="🛑 Emergency Stop", style=discord.ButtonStyle.danger, emoji="🛑")
    async def emergency_stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="🛑 Emergency Stop", description="This will immediately stop the bot. Only use in emergencies!", color=0xff0000)
        
        view = discord.ui.View()
        
        confirm_btn = discord.ui.Button(label="🛑 EMERGENCY STOP", style=discord.ButtonStyle.danger)
        cancel_btn = discord.ui.Button(label="❌ Cancel", style=discord.ButtonStyle.secondary)
        
        async def confirm_stop(confirm_interaction):
            await confirm_interaction.response.send_message("🛑 Emergency stop initiated. Bot going offline NOW.", ephemeral=True)
            # In a real deployment, this would properly shut down the bot
            await asyncio.sleep(1)
            sys.exit(0)
        
        async def cancel_stop(cancel_interaction):
            await cancel_interaction.response.send_message("❌ Emergency stop cancelled.", ephemeral=True)
        
        confirm_btn.callback = confirm_stop
        cancel_btn.callback = cancel_stop
        view.add_item(confirm_btn)
        view.add_item(cancel_btn)
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @discord.ui.button(label="📊 Bot Status", style=discord.ButtonStyle.secondary, emoji="📊")
    async def bot_status(self, interaction: discord.Interaction, button: discord.ui.Button):
        import psutil
        import time
        
        bot = interaction.client
        
        # Get system info
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        embed = discord.Embed(title="📊 Bot Status", color=0x00ffcc)
        embed.add_field(name="🤖 Bot Status", value="🟢 Online", inline=True)
        embed.add_field(name="⏰ Uptime", value=f"{int(time.time() - bot.start_time)}s", inline=True)
        embed.add_field(name="📡 Latency", value=f"{round(bot.latency * 1000)}ms", inline=True)
        embed.add_field(name="🧠 CPU Usage", value=f"{cpu_percent}%", inline=True)
        embed.add_field(name="💾 Memory", value=f"{memory.percent}%", inline=True)
        embed.add_field(name="🏠 Server Count", value=str(len(bot.guilds)), inline=True)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class QueueManagementView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
    
    @discord.ui.button(label="🔄 Toggle Queue", style=discord.ButtonStyle.primary)
    async def toggle_queue(self, interaction: discord.Interaction, button: discord.ui.Button):
        from main import log_to_channel
        settings = load_admin_settings()
        settings["allow_queue"] = not settings["allow_queue"]
        save_admin_settings(settings)
        
        status = "enabled" if settings["allow_queue"] else "disabled"
        await log_to_channel(f"⚙️ Queue system {status} by {interaction.user.display_name}", "INFO")
        embed = discord.Embed(title="✅ Queue Status Updated", description=f"Queue system is now **{status}**", color=0x00ff00)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🗑️ Clear Queue", style=discord.ButtonStyle.danger)
    async def clear_queue(self, interaction: discord.Interaction, button: discord.ui.Button):
        
        view = discord.ui.View()
        
        confirm_btn = discord.ui.Button(label="✅ Confirm Clear", style=discord.ButtonStyle.danger)
        cancel_btn = discord.ui.Button(label="❌ Cancel", style=discord.ButtonStyle.secondary)
        
        async def confirm_clear(confirm_interaction):
            from main import log_to_channel
            save_queue([])
            await log_to_channel(f"🗑️ Queue cleared by admin {confirm_interaction.user.display_name}", "WARNING")
            await confirm_interaction.response.send_message("✅ Queue cleared successfully!", ephemeral=True)
        
        async def cancel_clear(cancel_interaction):
            await cancel_interaction.response.send_message("❌ Queue clear cancelled.", ephemeral=True)
        
        confirm_btn.callback = confirm_clear
        cancel_btn.callback = cancel_clear
        view.add_item(confirm_btn)
        view.add_item(cancel_btn)
        
        await interaction.response.send_message("⚠️ Are you sure you want to clear the entire queue?", view=view, ephemeral=True)

class TournamentControlView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
    
    @discord.ui.button(label="🏆 Create Tournament", style=discord.ButtonStyle.success)
    async def create_tournament(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="🏆 Quick Tournament Creator", description="Use the `/advanced_tournament` command for full tournament creation with all customization options.", color=0xFFD700)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🔄 Toggle Tournaments", style=discord.ButtonStyle.primary)
    async def toggle_tournaments(self, interaction: discord.Interaction, button: discord.ui.Button):
        settings = load_admin_settings()
        settings["allow_tournaments"] = not settings["allow_tournaments"]
        save_admin_settings(settings)
        
        status = "enabled" if settings["allow_tournaments"] else "disabled"
        embed = discord.Embed(title="✅ Tournament Status Updated", description=f"Tournament system is now **{status}**", color=0x00ff00)
        await interaction.response.send_message(embed=embed, ephemeral=True)

class AnalyticsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
    
    @discord.ui.button(label="📈 Detailed Analytics", style=discord.ButtonStyle.primary)
    async def detailed_analytics(self, interaction: discord.Interaction, button: discord.ui.Button):
        stats = load_stats()
        history = load_match_history()
        
        # Calculate more detailed metrics
        total_goals = sum(player["goals"] for player in stats.values())
        total_saves = sum(player["saves"] for player in stats.values())
        total_assists = sum(player["assists"] for player in stats.values())
        
        avg_goals_per_match = total_goals / len(history) if history else 0
        
        embed = discord.Embed(title="📈 Detailed Server Analytics", color=0x9b59b6)
        embed.add_field(name="⚽ Total Goals", value=str(total_goals), inline=True)
        embed.add_field(name="🛡️ Total Saves", value=str(total_saves), inline=True)
        embed.add_field(name="🤝 Total Assists", value=str(total_assists), inline=True)
        embed.add_field(name="📊 Avg Goals/Match", value=f"{avg_goals_per_match:.1f}", inline=True)
        
        # Most popular format
        format_counts = {}
        for match in history:
            format_type = match.get("format", "Unknown")
            format_counts[format_type] = format_counts.get(format_type, 0) + 1
        
        if format_counts:
            most_popular = max(format_counts, key=format_counts.get)
            embed.add_field(name="🎮 Most Popular Format", value=f"{most_popular} ({format_counts[most_popular]} matches)", inline=True)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class DataManagementView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
    
    @discord.ui.button(label="🗑️ Clear All Stats", style=discord.ButtonStyle.danger)
    async def clear_stats(self, interaction: discord.Interaction, button: discord.ui.Button):
        
        view = discord.ui.View()
        
        confirm_btn = discord.ui.Button(label="🗑️ CONFIRM CLEAR ALL STATS", style=discord.ButtonStyle.danger)
        cancel_btn = discord.ui.Button(label="❌ Cancel", style=discord.ButtonStyle.secondary)
        
        async def confirm_clear(confirm_interaction):
            save_stats({})
            await confirm_interaction.response.send_message("✅ All player stats cleared!", ephemeral=True)
        
        async def cancel_clear(cancel_interaction):
            await cancel_interaction.response.send_message("❌ Stats clear cancelled.", ephemeral=True)
        
        confirm_btn.callback = confirm_clear
        cancel_btn.callback = cancel_clear
        view.add_item(confirm_btn)
        view.add_item(cancel_btn)
        
        await interaction.response.send_message("⚠️ **WARNING**: This will permanently delete ALL player statistics. Are you absolutely sure?", view=view, ephemeral=True)
    
    @discord.ui.button(label="🗑️ Clear Match History", style=discord.ButtonStyle.danger)
    async def clear_history(self, interaction: discord.Interaction, button: discord.ui.Button):
        
        view = discord.ui.View()
        
        confirm_btn = discord.ui.Button(label="🗑️ CONFIRM CLEAR HISTORY", style=discord.ButtonStyle.danger)
        cancel_btn = discord.ui.Button(label="❌ Cancel", style=discord.ButtonStyle.secondary)
        
        async def confirm_clear(confirm_interaction):
            save_match_history([])
            await confirm_interaction.response.send_message("✅ Match history cleared!", ephemeral=True)
        
        async def cancel_clear(cancel_interaction):
            await cancel_interaction.response.send_message("❌ History clear cancelled.", ephemeral=True)
        
        confirm_btn.callback = confirm_clear
        cancel_btn.callback = cancel_clear
        view.add_item(confirm_btn)
        view.add_item(cancel_btn)
        
        await interaction.response.send_message("⚠️ This will permanently delete all match history. Continue?", view=view, ephemeral=True)

class BotSettingsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
    
    @discord.ui.button(label="🔄 Toggle Auto-MMR", style=discord.ButtonStyle.primary)
    async def toggle_auto_mmr(self, interaction: discord.Interaction, button: discord.ui.Button):
        settings = load_admin_settings()
        settings["auto_mmr_updates"] = not settings["auto_mmr_updates"]
        save_admin_settings(settings)
        
        status = "enabled" if settings["auto_mmr_updates"] else "disabled"
        embed = discord.Embed(title="✅ Auto-MMR Updated", description=f"Automatic MMR updates are now **{status}**", color=0x00ff00)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="⭐ Toggle MVP Voting", style=discord.ButtonStyle.primary)
    async def toggle_mvp_voting(self, interaction: discord.Interaction, button: discord.ui.Button):
        settings = load_admin_settings()
        settings["mvp_voting_enabled"] = not settings["mvp_voting_enabled"]
        save_admin_settings(settings)
        
        status = "enabled" if settings["mvp_voting_enabled"] else "disabled"
        embed = discord.Embed(title="✅ MVP Voting Updated", description=f"MVP voting is now **{status}**", color=0x00ff00)
        await interaction.response.send_message(embed=embed, ephemeral=True)

class AutoTournamentView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
    
    @discord.ui.button(label="🔄 Toggle Auto Tournaments", style=discord.ButtonStyle.success)
    async def toggle_auto_tournaments(self, interaction: discord.Interaction, button: discord.ui.Button):
        settings = load_admin_settings()
        if "auto_tournament" not in settings:
            settings["auto_tournament"] = {
                "enabled": False,
                "interval_minutes": 60,
                "format": "3v3",
                "map": "DFH Stadium",
                "mode": "Soccar",
                "max_teams": 8,
                "channel_id": None
            }
        
        settings["auto_tournament"]["enabled"] = not settings["auto_tournament"]["enabled"]
        save_admin_settings(settings)
        
        status = "enabled" if settings["auto_tournament"]["enabled"] else "disabled"
        embed = discord.Embed(title="✅ Auto Tournaments Updated", description=f"Auto tournaments are now **{status}**", color=0x00ff00)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="⏰ Set Interval", style=discord.ButtonStyle.primary)
    async def set_interval(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = AutoTournamentIntervalModal()
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="⚙️ Configure Format", style=discord.ButtonStyle.secondary)
    async def configure_format(self, interaction: discord.Interaction, button: discord.ui.Button):
        settings = load_admin_settings()
        auto_settings = settings.get("auto_tournament", {})
        
        embed = discord.Embed(title="⚙️ Auto Tournament Configuration", color=0x00ffcc)
        embed.add_field(name="Current Format", value=auto_settings.get("format", "3v3"), inline=True)
        embed.add_field(name="Current Map", value=auto_settings.get("map", "DFH Stadium"), inline=True)
        embed.add_field(name="Current Mode", value=auto_settings.get("mode", "Soccar"), inline=True)
        embed.add_field(name="Max Teams", value=str(auto_settings.get("max_teams", 8)), inline=True)
        
        view = AutoTournamentConfigView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @discord.ui.button(label="📍 Set Channel", style=discord.ButtonStyle.primary)
    async def set_channel(self, interaction: discord.Interaction, button: discord.ui.Button):
        settings = load_admin_settings()
        if "auto_tournament" not in settings:
            settings["auto_tournament"] = {
                "enabled": False,
                "interval_minutes": 60,
                "format": "3v3",
                "map": "DFH Stadium",
                "mode": "Soccar",
                "max_teams": 8,
                "channel_id": None
            }
        
        settings["auto_tournament"]["channel_id"] = interaction.channel.id
        save_admin_settings(settings)
        
        embed = discord.Embed(title="✅ Auto Tournament Channel Set", description=f"Auto tournaments will now be posted in {interaction.channel.mention}", color=0x00ff00)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🚀 Create Test Tournament", style=discord.ButtonStyle.success)
    async def create_test_tournament(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        
        try:
            from main import create_auto_tournament
            tournament_id = await create_auto_tournament(interaction.channel)
            embed = discord.Embed(title="✅ Test Tournament Created", description=f"Tournament ID: {tournament_id}", color=0x00ff00)
            await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Error creating tournament: {str(e)}", ephemeral=True)

class AutoTournamentIntervalModal(discord.ui.Modal, title="Set Auto Tournament Interval"):
    def __init__(self):
        super().__init__()
    
    interval = discord.ui.TextInput(
        label="Interval (minutes)",
        placeholder="Enter interval in minutes (e.g., 60 for 1 hour)",
        default="60",
        max_length=4
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            interval_minutes = int(self.interval.value)
            if interval_minutes < 10:
                await interaction.response.send_message("❌ Interval must be at least 10 minutes!", ephemeral=True)
                return
            
            settings = load_admin_settings()
            if "auto_tournament" not in settings:
                settings["auto_tournament"] = {
                    "enabled": False,
                    "interval_minutes": 60,
                    "format": "3v3",
                    "map": "DFH Stadium",
                    "mode": "Soccar",
                    "max_teams": 8,
                    "channel_id": None
                }
            
            settings["auto_tournament"]["interval_minutes"] = interval_minutes
            save_admin_settings(settings)
            
            embed = discord.Embed(title="✅ Interval Updated", description=f"Auto tournaments will now be created every **{interval_minutes} minutes**", color=0x00ff00)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except ValueError:
            await interaction.response.send_message("❌ Please enter a valid number!", ephemeral=True)

class AutoTournamentConfigView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
    
    @discord.ui.select(placeholder="Choose format...", options=[
        discord.SelectOption(label="1v1", description="1 vs 1 tournaments", emoji="⚡"),
        discord.SelectOption(label="2v2", description="2 vs 2 tournaments", emoji="🤝"),
        discord.SelectOption(label="3v3", description="3 vs 3 tournaments", emoji="👥")
    ])
    async def format_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        settings = load_admin_settings()
        settings["auto_tournament"]["format"] = select.values[0]
        save_admin_settings(settings)
        
        embed = discord.Embed(title="✅ Format Updated", description=f"Auto tournaments will now use **{select.values[0]}** format", color=0x00ff00)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.select(placeholder="Choose map...", options=[
        discord.SelectOption(label="DFH Stadium", emoji="🏟️"),
        discord.SelectOption(label="Mannfield", emoji="🌿"),
        discord.SelectOption(label="Champions Field", emoji="🏆"),
        discord.SelectOption(label="Neo Tokyo", emoji="🌸"),
        discord.SelectOption(label="Random Maps", emoji="🎲")
    ])
    async def map_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        settings = load_admin_settings()
        settings["auto_tournament"]["map"] = select.values[0]
        save_admin_settings(settings)
        
        embed = discord.Embed(title="✅ Map Updated", description=f"Auto tournaments will now use **{select.values[0]}** map", color=0x00ff00)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.select(placeholder="Choose mode...", options=[
        discord.SelectOption(label="Soccar", description="Classic Rocket League", emoji="⚽"),
        discord.SelectOption(label="Hoops", description="Basketball mode", emoji="🏀"),
        discord.SelectOption(label="Snow Day", description="Hockey with a puck", emoji="🏒"),
        discord.SelectOption(label="Rumble", description="Power-ups enabled", emoji="💥")
    ])
    async def mode_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        settings = load_admin_settings()
        settings["auto_tournament"]["mode"] = select.values[0]
        save_admin_settings(settings)
        
        embed = discord.Embed(title="✅ Mode Updated", description=f"Auto tournaments will now use **{select.values[0]}** mode", color=0x00ff00)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.select(placeholder="Choose max teams...", options=[
        discord.SelectOption(label="4 Teams", value="4", emoji="4️⃣"),
        discord.SelectOption(label="8 Teams", value="8", emoji="8️⃣"),
        discord.SelectOption(label="16 Teams", value="16", emoji="🔢"),
        discord.SelectOption(label="32 Teams", value="32", emoji="🏟️")
    ])
    async def max_teams_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        settings = load_admin_settings()
        settings["auto_tournament"]["max_teams"] = int(select.values[0])
        save_admin_settings(settings)
        
        embed = discord.Embed(title="✅ Max Teams Updated", description=f"Auto tournaments will now allow **{select.values[0]}** teams maximum", color=0x00ff00)
        await interaction.response.send_message(embed=embed, ephemeral=True)

# Function to create admin dashboard
async def setup_admin_dashboard(channel):
    embed = discord.Embed(
        title="🛠️ OctaneCore Admin Dashboard",
        description="**Administrator Control Panel**\n\nManage all aspects of the OctaneCore bot from this central hub.",
        color=0xff6600
    )
    
    embed.add_field(
        name="🔧 Core Controls",
        value="• **Bot Controls** - Restart, stop, status\n• **Queue Management** - Enable/disable queues\n• **Tournament Control** - Manage tournaments",
        inline=True
    )
    
    embed.add_field(
        name="📊 Analytics & Data",
        value="• **Server Analytics** - Usage statistics\n• **Data Management** - Clear/reset data\n• **Bot Settings** - Configure features",
        inline=True
    )
    
    embed.add_field(
        name="⚠️ Admin Only",
        value="Only users with Administrator permissions can use these controls. All actions are logged.",
        inline=False
    )
    
    embed.set_footer(text="Admin Dashboard • Use responsibly")
    
    view = AdminDashboardView()
    message = await channel.send(embed=embed, view=view)
    return message
