
import discord
from discord.ext import commands
import json
import asyncio
from datetime import datetime
from main import load_data, save_data, bot

class LiveMatchView(discord.ui.View):
    def __init__(self, match_id):
        super().__init__(timeout=None)
        self.match_id = match_id
        self.spectators = []
        self.chat_messages = []
        self.live_score = {"orange": 0, "blue": 0}
        self.match_time = 0
        self.overtime = False

    @discord.ui.button(label="👁️ Spectate Match", style=discord.ButtonStyle.primary, emoji="🎮")
    async def spectate_match(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id not in self.spectators:
            self.spectators.append(interaction.user.id)
            await interaction.response.send_message(f"👁️ You're now spectating match {self.match_id}!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ You're already spectating this match!", ephemeral=True)

    @discord.ui.button(label="💬 Join Live Chat", style=discord.ButtonStyle.secondary, emoji="💭")
    async def join_live_chat(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = LiveChatModal(self.match_id)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="📊 Live Stats", style=discord.ButtonStyle.secondary, emoji="📈")
    async def live_stats(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title=f"📊 Live Match Stats - {self.match_id}", color=0x00ffcc)
        
        # Current score
        embed.add_field(name="🏆 Current Score", value=f"🟠 **{self.live_score['orange']}** - **{self.live_score['blue']}** 🔵", inline=False)
        
        # Match time
        time_status = "⏰ Overtime" if self.overtime else f"⏱️ {self.match_time}:00"
        embed.add_field(name="Time", value=time_status, inline=True)
        
        # Spectators
        embed.add_field(name="👁️ Spectators", value=str(len(self.spectators)), inline=True)
        
        # Recent chat
        if self.chat_messages:
            recent_chat = "\n".join(self.chat_messages[-3:])
            embed.add_field(name="💬 Recent Chat", value=recent_chat, inline=False)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="🔄 Refresh", style=discord.ButtonStyle.success, emoji="🔄")
    async def refresh_match(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.update_live_display(interaction.message)
        await interaction.response.send_message("✅ Match display refreshed!", ephemeral=True)

    async def update_live_display(self, message):
        embed = discord.Embed(title=f"🔴 LIVE: {self.match_id}", color=0xff0000)
        
        # Live score with emphasis
        score_text = f"🟠 **{self.live_score['orange']}** - **{self.live_score['blue']}** 🔵"
        if self.overtime:
            score_text += " ⏰ **OVERTIME**"
        
        embed.add_field(name="🏆 Live Score", value=score_text, inline=False)
        embed.add_field(name="👁️ Spectators", value=str(len(self.spectators)), inline=True)
        embed.add_field(name="⏱️ Match Time", value=f"{self.match_time}:00", inline=True)
        
        # Recent events
        if self.chat_messages:
            recent_events = "\n".join(self.chat_messages[-5:])
            embed.add_field(name="📢 Recent Events", value=recent_events, inline=False)
        
        embed.set_footer(text=f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
        
        await message.edit(embed=embed, view=self)

    async def update_score(self, orange_score, blue_score, scorer=None):
        self.live_score["orange"] = orange_score
        self.live_score["blue"] = blue_score
        
        if scorer:
            goal_msg = f"⚽ GOAL! {scorer} scored! ({orange_score}-{blue_score})"
            self.chat_messages.append(goal_msg)
        
        # Notify spectators
        for spectator_id in self.spectators:
            try:
                user = await bot.fetch_user(spectator_id)
                embed = discord.Embed(title="⚽ GOAL SCORED!", color=0x00ff00)
                embed.add_field(name="Match", value=self.match_id, inline=True)
                embed.add_field(name="Score", value=f"🟠 {orange_score} - {blue_score} 🔵", inline=True)
                if scorer:
                    embed.add_field(name="Scorer", value=scorer, inline=True)
                
                await user.send(embed=embed)
            except:
                pass  # User may have DMs disabled

class LiveChatModal(discord.ui.Modal, title="Live Match Chat"):
    def __init__(self, match_id):
        super().__init__()
        self.match_id = match_id

    message = discord.ui.TextInput(
        label="Chat Message",
        placeholder="Type your message here...",
        style=discord.TextStyle.paragraph,
        max_length=200
    )

    async def on_submit(self, interaction: discord.Interaction):
        # Add message to live chat
        timestamp = datetime.now().strftime("%H:%M")
        chat_message = f"[{timestamp}] {interaction.user.display_name}: {self.message.value}"
        
        # This would typically be stored and broadcast to all spectators
        await interaction.response.send_message(f"💬 Message sent: {self.message.value}", ephemeral=True)

class MatchReporterView(discord.ui.View):
    def __init__(self, match_id):
        super().__init__(timeout=None)
        self.match_id = match_id
        self.live_match = None

    @discord.ui.button(label="📊 Start Live Tracking", style=discord.ButtonStyle.success, emoji="🔴")
    async def start_live_tracking(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.live_match = LiveMatchView(self.match_id)
        
        embed = discord.Embed(title=f"🔴 LIVE: {self.match_id}", color=0xff0000)
        embed.add_field(name="Status", value="🎮 Match is now live!", inline=False)
        embed.add_field(name="Features", value="• Real-time score updates\n• Spectator mode\n• Live chat\n• Match statistics", inline=False)
        
        await interaction.response.send_message(embed=embed, view=self.live_match)

    @discord.ui.button(label="⚽ Update Score", style=discord.ButtonStyle.primary, emoji="🏆")
    async def update_score(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.live_match:
            await interaction.response.send_message("❌ Live tracking not started!", ephemeral=True)
            return
        
        modal = ScoreUpdateModal(self.live_match)
        await interaction.response.send_modal(modal)

class ScoreUpdateModal(discord.ui.Modal, title="Update Live Score"):
    def __init__(self, live_match):
        super().__init__()
        self.live_match = live_match

    orange_score = discord.ui.TextInput(
        label="Orange Team Score",
        placeholder="Enter current orange score...",
        max_length=2
    )
    
    blue_score = discord.ui.TextInput(
        label="Blue Team Score",
        placeholder="Enter current blue score...",
        max_length=2
    )
    
    scorer = discord.ui.TextInput(
        label="Goal Scorer (Optional)",
        placeholder="Who scored the goal?",
        required=False,
        max_length=50
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            orange = int(self.orange_score.value)
            blue = int(self.blue_score.value)
            
            await self.live_match.update_score(orange, blue, self.scorer.value or None)
            await interaction.response.send_message(f"✅ Score updated: {orange} - {blue}", ephemeral=True)
        except ValueError:
            await interaction.response.send_message("❌ Please enter valid numbers!", ephemeral=True)

async def setup_live_match_reporter(channel, match_id):
    embed = discord.Embed(
        title="📺 Live Match Reporter",
        description=f"Set up live tracking for match: **{match_id}**",
        color=0xff6600
    )
    
    view = MatchReporterView(match_id)
    message = await channel.send(embed=embed, view=view)
    return message
