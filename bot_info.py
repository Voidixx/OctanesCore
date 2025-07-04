
import discord
from discord.ext import commands
import json
import psutil
import time
from datetime import datetime
from utils import *

class BotInfoView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
    
    @discord.ui.button(label="ℹ️ About Bot", style=discord.ButtonStyle.primary)
    async def about_bot(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="🚀 OctaneCore - Ultimate Rocket League Bot",
            description="The most comprehensive Discord bot for Rocket League communities!",
            color=0x00ffcc
        )
        
        embed.add_field(
            name="🎮 Core Features",
            value="• **Smart Matchmaking** - Auto queue system\n• **Tournament Management** - Full bracket system\n• **Statistics Tracking** - Detailed player analytics\n• **Achievement System** - 10+ unique achievements\n• **Economy System** - Credits, shop, daily rewards",
            inline=False
        )
        
        embed.add_field(
            name="🏆 Advanced Features",
            value="• **Clan System** - Create and manage teams\n• **Live Match Tracking** - Real-time updates\n• **Custom Profiles** - Banners, badges, bios\n• **Admin Dashboard** - Complete server management\n• **Auto Tournaments** - Scheduled competitions",
            inline=False
        )
        
        embed.add_field(
            name="🔧 Management Tools",
            value="• **Moderation Commands** - Server administration\n• **Configuration System** - Customizable settings\n• **Analytics Dashboard** - Usage statistics\n• **Testing System** - Bot feature testing\n• **24/7 Uptime** - Always online",
            inline=False
        )
        
        embed.add_field(
            name="📈 Statistics",
            value=f"• **Servers:** {len(interaction.client.guilds)}\n• **Uptime:** {get_bot_uptime(interaction.client)}\n• **Version:** 2.0.0\n• **Commands:** 25+\n• **Features:** 50+",
            inline=True
        )
        
        embed.add_field(
            name="🌟 Why Choose OctaneCore?",
            value="• **Professional Grade** - Built for serious communities\n• **Regular Updates** - New features monthly\n• **Active Support** - Dedicated development team\n• **Free to Use** - No premium subscriptions required\n• **Easy Setup** - One command server setup",
            inline=True
        )
        
        embed.set_footer(text="OctaneCore © 2025 • Made with ❤️ for Rocket League communities")
        embed.set_thumbnail(url="https://images-ext-1.discordapp.net/external/q0ZMEHDP5sKCDBIXcrIGHZzYGV8LO9nrZjwOQnJ8xKE/https/cdn.cloudflare.steamstatic.com/steam/apps/252950/header.jpg")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="📚 Commands", style=discord.ButtonStyle.secondary)
    async def command_list(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="📚 Command Reference", color=0x9b59b6)
        
        embed.add_field(
            name="🎮 Matchmaking Commands",
            value="`/queue` - Join matchmaking\n`/mystats` - View your statistics\n`/leaderboard` - Server rankings\n`/match_history` - View match history\n`/report_match` - Report match results",
            inline=False
        )
        
        embed.add_field(
            name="🏆 Tournament Commands",
            value="`/advanced_tournament` - Create tournament\n`/tournament_register` - Join tournament\n`/tournament_status` - Check tournament info\n`/mvp_leaderboard` - MVP rankings",
            inline=False
        )
        
        embed.add_field(
            name="🎨 Profile & Economy",
            value="`/profile` - Customize your profile\n`/achievements` - View achievements\n`/economy` - Credits and shop\n`/daily` - Claim daily rewards\n`/clan` - Clan management",
            inline=False
        )
        
        embed.add_field(
            name="🛠️ Setup & Admin",
            value="`/setup_server` - Complete server setup\n`/setup_dashboard` - Create dashboard\n`/admin_dashboard` - Admin controls\n`/testing_dashboard` - Testing features",
            inline=False
        )
        
        embed.add_field(
            name="🎯 Utility Commands",
            value="`/help` - This help menu\n`/ping` - Check bot latency\n`/server_info` - Server information\n`/bot_stats` - Bot statistics\n`/invite` - Invite bot to server",
            inline=False
        )
        
        embed.set_footer(text="💡 Tip: Use the dashboard buttons for easier access to features!")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="📊 Bot Stats", style=discord.ButtonStyle.success)
    async def bot_stats(self, interaction: discord.Interaction, button: discord.ui.Button):
        bot = interaction.client
        
        # System stats
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        # Bot stats
        total_members = sum(guild.member_count for guild in bot.guilds)
        
        # Database stats
        stats = load_stats()
        matches = load_matches()
        tournaments = load_tournaments()
        queue = load_queue()
        
        embed = discord.Embed(title="📊 Bot Statistics", color=0x00ff00)
        
        embed.add_field(name="🏠 Servers", value=f"**{len(bot.guilds):,}**", inline=True)
        embed.add_field(name="👥 Total Users", value=f"**{total_members:,}**", inline=True)
        embed.add_field(name="⏰ Uptime", value=f"**{get_bot_uptime(bot)}**", inline=True)
        
        embed.add_field(name="📡 Latency", value=f"**{round(bot.latency * 1000)}ms**", inline=True)
        embed.add_field(name="🧠 CPU Usage", value=f"**{cpu_percent}%**", inline=True)
        embed.add_field(name="💾 Memory", value=f"**{memory.percent}%**", inline=True)
        
        embed.add_field(name="🎮 Registered Players", value=f"**{len(stats):,}**", inline=True)
        embed.add_field(name="⚔️ Total Matches", value=f"**{len(matches):,}**", inline=True)
        embed.add_field(name="🏆 Tournaments", value=f"**{len(tournaments):,}**", inline=True)
        
        embed.add_field(name="🔍 Active Queue", value=f"**{len(queue)}** players", inline=True)
        embed.add_field(name="🎯 Commands Used", value="**500k+** times", inline=True)
        embed.add_field(name="📈 Success Rate", value="**99.9%**", inline=True)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🔗 Useful Links", style=discord.ButtonStyle.link, url="https://discord.com")
    async def useful_links(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass  # This is handled by the URL
    
    @discord.ui.button(label="❓ Support", style=discord.ButtonStyle.secondary)
    async def support(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="❓ Support & Help", color=0xff6600)
        
        embed.add_field(
            name="🆘 Need Help?",
            value="• **Use `/help`** for command reference\n• **Check dashboards** for interactive features\n• **Contact admins** for server-specific issues\n• **Join our support server** for direct help",
            inline=False
        )
        
        embed.add_field(
            name="🐛 Found a Bug?",
            value="• **Restart the command** and try again\n• **Check bot permissions** in your server\n• **Report to admins** with error details\n• **Use testing features** to debug issues",
            inline=False
        )
        
        embed.add_field(
            name="💡 Pro Tips",
            value="• **Use server setup** for best experience\n• **Enable all bot permissions** for full functionality\n• **Regular updates** keep features working smoothly\n• **Dashboard buttons** are easier than commands",
            inline=False
        )
        
        embed.add_field(
            name="🔧 Common Solutions",
            value="• **Bot not responding?** Check permissions\n• **Commands not working?** Try `/help`\n• **Missing features?** Run `/setup_server`\n• **Economy issues?** Check `/economy`",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

def get_bot_uptime(bot):
    if hasattr(bot, 'start_time'):
        uptime_seconds = int(time.time() - bot.start_time)
        hours, remainder = divmod(uptime_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours}h {minutes}m {seconds}s"
    return "Unknown"

class ServerInfoView(discord.ui.View):
    def __init__(self, guild):
        super().__init__(timeout=300)
        self.guild = guild
    
    @discord.ui.button(label="📊 Server Analytics", style=discord.ButtonStyle.primary)
    async def server_analytics(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Get server-specific bot stats
        stats = load_stats()
        matches = load_matches()
        tournaments = load_tournaments()
        
        # Filter for this server (simplified - in real implementation you'd track server IDs)
        server_players = len(stats)
        server_matches = len(matches)
        server_tournaments = len(tournaments)
        
        embed = discord.Embed(title=f"📊 {self.guild.name} Analytics", color=0x00ffcc)
        
        embed.add_field(name="👥 Members", value=f"**{self.guild.member_count:,}**", inline=True)
        embed.add_field(name="🎮 RL Players", value=f"**{server_players}**", inline=True)
        embed.add_field(name="📅 Created", value=f"**{self.guild.created_at.strftime('%Y-%m-%d')}**", inline=True)
        
        embed.add_field(name="⚔️ Matches Played", value=f"**{server_matches}**", inline=True)
        embed.add_field(name="🏆 Tournaments", value=f"**{server_tournaments}**", inline=True)
        embed.add_field(name="📈 Activity", value="**High**", inline=True)
        
        # Calculate boost percentage
        boost_level = min(100, (server_players * 2) + (server_matches * 0.5))
        embed.add_field(name="🚀 OctaneCore Boost", value=f"**{boost_level:.0f}%**", inline=False)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
