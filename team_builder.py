
import discord
from discord.ext import commands
import json
import random
from datetime import datetime
from data import load_data, save_data

class TeamBuilderView(discord.ui.View):
    def __init__(self, channel_id):
        super().__init__(timeout=None)
        self.channel_id = channel_id
        self.players = []
        self.teams = {"Orange": [], "Blue": []}
        self.captains = {"Orange": None, "Blue": None}
        self.mode = None
        self.captain_mode = False
        self.pick_turn = "Orange"

    @discord.ui.button(label="🎯 Join Team Builder", style=discord.ButtonStyle.primary, emoji="🎮")
    async def join_builder(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id in [p["id"] for p in self.players]:
            await interaction.response.send_message("❌ You're already in the team builder!", ephemeral=True)
            return
        
        stats = load_data("stats.json")
        player_mmr = stats.get(str(interaction.user.id), {}).get("mmr", 1000)
        
        self.players.append({
            "id": interaction.user.id,
            "name": interaction.user.display_name,
            "mmr": player_mmr
        })
        
        await self.update_display(interaction)

    @discord.ui.button(label="⚖️ Auto-Balance Teams", style=discord.ButtonStyle.success, emoji="🔄")
    async def auto_balance(self, interaction: discord.Interaction, button: discord.ui.Button):
        if len(self.players) < 2:
            await interaction.response.send_message("❌ Need at least 2 players!", ephemeral=True)
            return
        
        # Sort players by MMR for balanced teams
        sorted_players = sorted(self.players, key=lambda x: x["mmr"], reverse=True)
        
        self.teams = {"Orange": [], "Blue": []}
        
        # Distribute players alternately for balance
        for i, player in enumerate(sorted_players):
            if i % 2 == 0:
                self.teams["Orange"].append(player)
            else:
                self.teams["Blue"].append(player)
        
        await self.update_display(interaction, "✅ Teams auto-balanced by MMR!")

    @discord.ui.button(label="👑 Captain Mode", style=discord.ButtonStyle.secondary, emoji="🎖️")
    async def captain_mode_toggle(self, interaction: discord.Interaction, button: discord.ui.Button):
        if len(self.players) < 2:
            await interaction.response.send_message("❌ Need at least 2 players!", ephemeral=True)
            return
        
        self.captain_mode = True
        
        # Select captains (highest MMR players)
        sorted_players = sorted(self.players, key=lambda x: x["mmr"], reverse=True)
        self.captains["Orange"] = sorted_players[0]
        self.captains["Blue"] = sorted_players[1]
        
        # Remove captains from player pool
        self.players = [p for p in self.players if p["id"] not in [self.captains["Orange"]["id"], self.captains["Blue"]["id"]]]
        
        # Reset teams
        self.teams = {"Orange": [self.captains["Orange"]], "Blue": [self.captains["Blue"]]}
        
        await self.update_display(interaction, f"👑 Captain Mode! {self.captains['Orange']['name']} vs {self.captains['Blue']['name']}")

    @discord.ui.button(label="🎲 Random Teams", style=discord.ButtonStyle.secondary, emoji="🎯")
    async def random_teams(self, interaction: discord.Interaction, button: discord.ui.Button):
        if len(self.players) < 2:
            await interaction.response.send_message("❌ Need at least 2 players!", ephemeral=True)
            return
        
        shuffled = self.players.copy()
        random.shuffle(shuffled)
        
        mid = len(shuffled) // 2
        self.teams = {
            "Orange": shuffled[:mid],
            "Blue": shuffled[mid:]
        }
        
        await self.update_display(interaction, "🎲 Teams randomly generated!")

    @discord.ui.select(placeholder="Pick a player for your team...", options=[
        discord.SelectOption(label="No players available", value="none")
    ])
    async def pick_player(self, interaction: discord.Interaction, select: discord.ui.Select):
        if not self.captain_mode:
            await interaction.response.send_message("❌ Captain mode not active!", ephemeral=True)
            return
        
        if interaction.user.id != self.captains[self.pick_turn]["id"]:
            await interaction.response.send_message(f"❌ It's {self.captains[self.pick_turn]['name']}'s turn to pick!", ephemeral=True)
            return
        
        player_id = int(select.values[0])
        picked_player = next((p for p in self.players if p["id"] == player_id), None)
        
        if picked_player:
            self.teams[self.pick_turn].append(picked_player)
            self.players.remove(picked_player)
            self.pick_turn = "Blue" if self.pick_turn == "Orange" else "Orange"
            
            await self.update_display(interaction, f"✅ {picked_player['name']} picked by {self.pick_turn} team!")

    async def update_display(self, interaction, message=None):
        embed = discord.Embed(title="🏗️ Team Builder", color=0x00ffcc)
        
        if message:
            embed.description = message
        
        # Show current teams
        if self.teams["Orange"] or self.teams["Blue"]:
            orange_mmr = sum(p["mmr"] for p in self.teams["Orange"])
            blue_mmr = sum(p["mmr"] for p in self.teams["Blue"])
            
            orange_text = "\n".join([f"• {p['name']} ({p['mmr']} MMR)" for p in self.teams["Orange"]])
            blue_text = "\n".join([f"• {p['name']} ({p['mmr']} MMR)" for p in self.teams["Blue"]])
            
            embed.add_field(name=f"🟠 Orange Team (Avg: {orange_mmr//len(self.teams['Orange']) if self.teams['Orange'] else 0})", value=orange_text or "No players", inline=True)
            embed.add_field(name=f"🔵 Blue Team (Avg: {blue_mmr//len(self.teams['Blue']) if self.teams['Blue'] else 0})", value=blue_text or "No players", inline=True)
        
        # Show available players
        if self.players:
            players_text = "\n".join([f"• {p['name']} ({p['mmr']} MMR)" for p in self.players])
            embed.add_field(name="👥 Available Players", value=players_text, inline=False)
        
        # Update pick dropdown for captain mode
        if self.captain_mode and self.players:
            self.pick_player.options = [
                discord.SelectOption(label=f"{p['name']} ({p['mmr']} MMR)", value=str(p['id']))
                for p in self.players
            ]
            if len(self.players) > 0:
                embed.add_field(name="🎯 Captain Turn", value=f"{self.captains[self.pick_turn]['name']}'s turn to pick!", inline=False)
        
        await interaction.response.edit_message(embed=embed, view=self)

async def setup_team_builder(channel):
    embed = discord.Embed(
        title="🏗️ Team Builder Hub",
        description="Create balanced teams with multiple options!",
        color=0x00ffcc
    )
    embed.add_field(name="🎯 Features", value="• Auto-balance by MMR\n• Captain draft mode\n• Random team generation", inline=False)
    
    view = TeamBuilderView(channel.id)
    message = await channel.send(embed=embed, view=view)
    return message
