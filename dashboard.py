import discord
from discord.ext import commands
import json
import asyncio
from datetime import datetime, timedelta

class DashboardView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.custom_id = "dashboard_persistent"

    @discord.ui.button(label="🎮 Quick Queue", style=discord.ButtonStyle.primary, custom_id="quick_queue", row=0)
    async def quick_queue(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="⚡ Quick Queue", description="Jump into the fastest available match!", color=0x00ffcc)

        # Auto-detect best queue based on current players
        from main import load_queue
        queue = load_queue()
        queue_counts = {"1v1": 0, "2v2": 0, "3v3": 0}

        for player in queue:
            if player["status"] == "searching":
                queue_counts[player["format"]] += 1

        # Find the queue closest to starting a match
        best_queue = None
        best_score = 0

        for format_type, count in queue_counts.items():
            needed = {"1v1": 2, "2v2": 4, "3v3": 6}[format_type]
            score = count / needed
            if score > best_score and count > 0:
                best_score = score
                best_queue = format_type

        if not best_queue:
            best_queue = "2v2"  # Default

        embed.add_field(name="🎯 Recommended Queue", value=f"**{best_queue}** ({queue_counts[best_queue]} waiting)", inline=False)
        embed.add_field(name="All Queues", value=f"1v1: {queue_counts['1v1']} | 2v2: {queue_counts['2v2']} | 3v3: {queue_counts['3v3']}", inline=False)
        embed.add_field(name="💡 Pro Tips", value="• Queue during peak hours for faster matches\n• Try different formats if one is slow\n• Check back in a few minutes if no matches", inline=False)

        view = QuickQueueView(best_queue)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @discord.ui.button(label="🏆 Tournaments", style=discord.ButtonStyle.success, custom_id="tournaments", row=0)
    async def tournaments(self, interaction: discord.Interaction, button: discord.ui.Button):
        from main import load_tournaments
        tournaments = load_tournaments()
        active_tournaments = [t for t in tournaments if t["status"] in ["registration", "active"]]

        embed = discord.Embed(title="🏆 Tournament Hub", description="Join competitive tournaments and climb the ranks!", color=0xFFD700)

        if active_tournaments:
            embed.add_field(name="🔥 Active Tournaments", value=f"Found **{len(active_tournaments)}** active tournaments", inline=False)
            for tournament in active_tournaments[-3:]:
                status_emoji = "🟢" if tournament["status"] == "registration" else "🔴"
                embed.add_field(
                    name=f"{status_emoji} {tournament['id'][:12]}...",
                    value=f"**{tournament['type']}** | {tournament['format']}\n{len(tournament['teams'])}/{tournament['max_teams']} teams",
                    inline=True
                )
        else:
            embed.add_field(name="No Active Tournaments", value="No tournaments running right now. Check back later or ask admins to create one!", inline=False)

        embed.add_field(name="ℹ️ How to Join", value="• Use `/tournament_register` with tournament ID\n• Form a team with friends\n• Compete for prizes and glory!", inline=False)

        view = TournamentHubView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @discord.ui.button(label="📊 My Stats", style=discord.ButtonStyle.secondary, custom_id="my_stats", row=0)
    async def my_stats(self, interaction: discord.Interaction, button: discord.ui.Button):
        from main import load_stats, load_match_history, load_mvp_votes

        stats = load_stats()
        player_id = str(interaction.user.id)

        if player_id not in stats:
            embed = discord.Embed(title="📊 Welcome to OctaneCore!", description="Ready to start your Rocket League journey? Play your first match to unlock detailed statistics!", color=0x00ffcc)
            embed.add_field(name="🎮 Getting Started", value="• Join a queue to find matches\n• Play tournaments for extra rewards\n• Track your progress over time", inline=False)
            embed.add_field(name="🏆 What You'll Unlock", value="• MMR and rank tracking\n• Win/loss statistics\n• Goal, save, and assist counts\n• Achievement system", inline=False)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        player_stats = stats[player_id]

        # Calculate additional stats
        total_games = player_stats["wins"] + player_stats["losses"]
        win_rate = (player_stats["wins"] / total_games * 100) if total_games > 0 else 0

        # Count MVPs
        mvp_votes = load_mvp_votes()
        mvp_count = 0
        for match_votes in mvp_votes.values():
            vote_counts = {}
            for vote in match_votes.values():
                vote_counts[vote] = vote_counts.get(vote, 0) + 1
            if vote_counts and max(vote_counts, key=vote_counts.get) == interaction.user.display_name:
                mvp_count += 1

        # Calculate goals per game
        goals_per_game = player_stats['goals'] / total_games if total_games > 0 else 0

        embed = discord.Embed(title=f"📊 {interaction.user.display_name}'s Profile", description=f"**{player_stats['rank']}** Player", color=0x00ffcc)
        embed.add_field(name="🏆 Rank & MMR", value=f"**{player_stats['rank']}**\n{player_stats['mmr']} MMR", inline=True)
        embed.add_field(name="🎮 Match Record", value=f"**{player_stats['wins']}W - {player_stats['losses']}L**\n{win_rate:.1f}% Win Rate", inline=True)
        embed.add_field(name="⭐ MVP Awards", value=f"**{mvp_count}** Total", inline=True)
        embed.add_field(name="⚽ Goals", value=f"**{player_stats['goals']}**\n{goals_per_game:.1f} per game", inline=True)
        embed.add_field(name="🛡️ Saves", value=f"**{player_stats['saves']}**", inline=True)
        embed.add_field(name="🤝 Assists", value=f"**{player_stats['assists']}**", inline=True)

        # Add rank progress
        rank_progress = self.get_rank_progress(player_stats['mmr'])
        embed.add_field(name="📈 Rank Progress", value=rank_progress, inline=False)

        view = StatsView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @discord.ui.button(label="🎯 Create Match", style=discord.ButtonStyle.primary, custom_id="create_match", row=1)
    async def create_match(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="🎯 Match Creator", description="Set up a custom private match with your friends!", color=0xff6600)
        embed.add_field(name="✨ Features", value="• Custom format selection\n• Choose your favorite maps\n• Private match credentials\n• Share with friends easily", inline=False)
        view = MatchCreatorView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @discord.ui.button(label="🌟 Leaderboards", style=discord.ButtonStyle.secondary, custom_id="leaderboards", row=1)
    async def leaderboards(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="🌟 Leaderboards", description="See who's dominating the server!", color=0xFFD700)
        embed.add_field(name="🏆 Available Rankings", value="• **MMR Leaderboard** - Top ranked players\n• **MVP Leaderboard** - Most valuable players\n• **Goals Leaderboard** - Top scorers", inline=False)
        view = LeaderboardView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @discord.ui.button(label="🏅 Achievements", style=discord.ButtonStyle.secondary, custom_id="achievements", row=1)
    async def achievements(self, interaction: discord.Interaction, button: discord.ui.Button):
        from achievements import load_achievements, ACHIEVEMENTS

        achievements = load_achievements()
        player_achievements = achievements.get(str(interaction.user.id), {"unlocked": []})

        unlocked_count = len(player_achievements["unlocked"])
        total_count = len(ACHIEVEMENTS)
        completion_percent = (unlocked_count / total_count * 100) if total_count > 0 else 0

        embed = discord.Embed(title="🏅 Achievement System", description=f"Progress: **{unlocked_count}/{total_count}** ({completion_percent:.1f}%)", color=0x9b59b6)

        # Show recent achievements
        recent = player_achievements["unlocked"][-3:] if player_achievements["unlocked"] else []
        if recent:
            recent_text = "\n".join([f"• {ACHIEVEMENTS[ach]['emoji']} {ACHIEVEMENTS[ach]['name']}" for ach in recent])
            embed.add_field(name="🎯 Recent Unlocks", value=recent_text, inline=False)

        embed.add_field(name="🎮 How to Unlock", value="• Score goals and make saves\n• Win matches and tournaments\n• Show MVP performance\n• Complete special challenges", inline=False)

        view = AchievementView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    def get_rank_progress(self, mmr):
        rank_thresholds = {
            "Bronze I": 50,
            "Silver I": 100,
            "Silver II": 200,
            "Silver III": 300,
            "Gold I": 400,
            "Gold II": 500,
            "Gold III": 600,
            "Platinum I": 700,
            "Platinum II": 800,
            "Platinum III": 900,
            "Diamond I": 1000,
            "Diamond II": 1100,
            "Diamond III": 1200,
            "Champion I": 1300,
            "Champion II": 1400,
            "Champion III": 1500,
            "Grand Champion": 1600
        }

        current_rank = None
        next_rank = None

        for rank, threshold in rank_thresholds.items():
            if mmr < threshold:
                next_rank = rank
                break
            current_rank = rank

        if next_rank:
            prev_threshold = rank_thresholds.get(current_rank, 0) if current_rank else 0
            next_threshold = rank_thresholds[next_rank]
            progress = ((mmr - prev_threshold) / (next_threshold - prev_threshold)) * 100
            return f"**{progress:.1f}%** to {next_rank} ({mmr}/{next_threshold} MMR)"
        else:
            return "**Maximum Rank Achieved!** 🏆"

class QuickQueueView(discord.ui.View):
    def __init__(self, recommended_format):
        super().__init__(timeout=300)
        self.recommended_format = recommended_format
        self.selected_format = None
        self.selected_mode = "Soccar"

    @discord.ui.button(label="Join Recommended", style=discord.ButtonStyle.success, emoji="⚡")
    async def join_recommended(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.join_queue_format(interaction, self.recommended_format, "Soccar")

    @discord.ui.select(placeholder="Choose format...", options=[
        discord.SelectOption(label="1v1 Duel", value="1v1", emoji="⚡"),
        discord.SelectOption(label="2v2 Doubles", value="2v2", emoji="🤝"),
        discord.SelectOption(label="3v3 Standard", value="3v3", emoji="👥")
    ])
    async def format_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.selected_format = select.values[0]
        await interaction.response.edit_message(content=f"✅ Format: **{self.selected_format}**\nNow choose game mode:", view=self)

    @discord.ui.select(placeholder="Choose game mode...", options=[
        discord.SelectOption(label="Soccar", description="Classic Rocket League", emoji="⚽"),
        discord.SelectOption(label="Hoops", description="Basketball mode", emoji="🏀"),
        discord.SelectOption(label="Snow Day", description="Hockey with a puck", emoji="🏒"),
        discord.SelectOption(label="Heatseeker", description="Auto-targeting ball", emoji="🎯")
    ])
    async def mode_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.selected_mode = select.values[0]
        if self.selected_format:
            await self.join_queue_format(interaction, self.selected_format, self.selected_mode)
        else:
            await interaction.response.send_message("❌ Please select format first!", ephemeral=True)

    @discord.ui.button(label="🔙 Back to Dashboard", style=discord.ButtonStyle.secondary, emoji="🔙")
    async def back_to_dashboard(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="🚀 OctaneCore Dashboard",
            description="**Welcome back!** Use the buttons below to access all features:",
            color=0x00ffcc
        )
        view = DashboardView()
        await interaction.response.edit_message(embed=embed, view=view)

    async def join_queue_format(self, interaction, format_type, game_mode="Soccar"):
        from main import load_queue, save_queue, log_to_channel, update_all_dashboards
        import datetime

        queue = load_queue()
        # Remove user from any existing queue
        old_queue_count = len(queue)
        queue = [p for p in queue if p["user_id"] != interaction.user.id]
        was_in_queue = len(queue) < old_queue_count

        queue.append({
            "user_id": interaction.user.id,
            "username": interaction.user.display_name,
            "format": format_type,
            "game_mode": game_mode,
            "status": "searching",
            "joined_at": datetime.datetime.now().isoformat(),
            "region": "Auto",
            "mmr": 1000  # Could get from stats
        })

        save_queue(queue)

        # Count players in this specific queue
        format_count = len([p for p in queue if p["format"] == format_type and p.get("game_mode", "Soccar") == game_mode])
        
        # Enhanced logging
        action = "rejoined" if was_in_queue else "joined"
        await log_to_channel(f"🎮 {interaction.user.display_name} {action} {format_type} {game_mode} queue", "INFO")
        await log_to_channel(f"📊 Queue Status: {format_count} players in {format_type} {game_mode}", "DEBUG")

        embed = discord.Embed(title=f"✅ Joined {format_type} {game_mode} Queue", color=0x00ff00)
        embed.add_field(name="Status", value="🔍 Searching for match...", inline=False)
        embed.add_field(name="Queue Info", value=f"**{format_count}** players in {format_type} {game_mode} queue", inline=False)
        embed.add_field(name="Estimated Wait", value=self.get_estimated_wait(format_type, format_count), inline=False)
        
        # Show all queue counts by game mode
        mode_counts = {}
        for mode in ["Soccar", "Hoops", "Snow Day", "Heatseeker"]:
            mode_counts[mode] = {}
            for fmt in ["1v1", "2v2", "3v3"]:
                mode_counts[mode][fmt] = len([p for p in queue if p["status"] == "searching" and p["format"] == fmt and p.get("game_mode", "Soccar") == mode])
        
        queue_text = ""
        for mode in ["Soccar", "Hoops", "Snow Day", "Heatseeker"]:
            emoji = {"Soccar": "⚽", "Hoops": "🏀", "Snow Day": "🏒", "Heatseeker": "🎯"}[mode]
            total = sum(mode_counts[mode].values())
            if total > 0:
                queue_text += f"{emoji} **{mode}**: {mode_counts[mode]['1v1']}-{mode_counts[mode]['2v2']}-{mode_counts[mode]['3v3']}\n"
        
        if queue_text:
            embed.add_field(name="🎮 All Queues (1v1-2v2-3v3)", value=queue_text, inline=False)
        
        embed.add_field(name="💡 Pro Tips", value="• Higher ranked players get priority\n• Peak hours = faster matches\n• Try different modes if waiting", inline=False)
        embed.set_footer(text="🔄 Queue updates in real-time | You'll be notified when matched!")

        # Update all dashboards immediately
        await update_all_dashboards()

        view = discord.ui.View()
        back_btn = discord.ui.Button(label="🔙 Back to Dashboard", style=discord.ButtonStyle.secondary)

        async def back_callback(button_interaction):
            embed, main_view = await self.create_main_dashboard_embed_and_view()
            await button_interaction.response.edit_message(embed=embed, view=main_view)

        back_btn.callback = back_callback
        view.add_item(back_btn)

        await interaction.response.edit_message(embed=embed, view=view)

    def get_estimated_wait(self, format_type, count):
        needed = {"1v1": 2, "2v2": 4, "3v3": 6}[format_type]
        if count >= needed:
            return "< 1 minute"
        else:
            return f"Waiting for {needed - count} more players"
    
    async def create_main_dashboard_embed_and_view(self):
        embed = discord.Embed(
            title="🚀 OctaneCore Dashboard",
            description="**Welcome back!** Use the buttons below to access all features:",
            color=0x00ffcc
        )
        view = DashboardView()
        return embed, view

class TournamentHubView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(label="📝 Register for Tournament", style=discord.ButtonStyle.primary, emoji="📝")
    async def register_tournament(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="📝 Tournament Registration", description="Ready to compete? Here's how to join:", color=0x00ffcc)
        embed.add_field(name="📋 Steps to Register", value="1. Copy a tournament ID from above\n2. Use `/tournament_register [ID] [team_name] [players]`\n3. Wait for tournament to start\n4. Compete for glory!", inline=False)
        embed.add_field(name="💡 Pro Tips", value="• Register early - spots fill up fast!\n• Coordinate with your team\n• Check tournament rules", inline=False)

        view = discord.ui.View()
        back_btn = discord.ui.Button(label="🔙 Back to Dashboard", style=discord.ButtonStyle.secondary)
        back_btn.callback = self.back_to_dashboard
        view.add_item(back_btn)

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    async def back_to_dashboard(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🚀 OctaneCore Dashboard",
            description="**Welcome back!** Use the buttons below to access all features:",
            color=0x00ffcc
        )
        view = DashboardView()
        await interaction.response.edit_message(embed=embed, view=view)

class StatsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(label="📊 Recent Matches", style=discord.ButtonStyle.secondary, emoji="📊")
    async def recent_matches(self, interaction: discord.Interaction, button: discord.ui.Button):
        from main import load_stats

        stats = load_stats()
        player_id = str(interaction.user.id)

        if player_id in stats and "match_history" in stats[player_id]:
            history = stats[player_id]["match_history"][-5:]

            embed = discord.Embed(title=f"📊 {interaction.user.display_name}'s Recent Matches", color=0x00ffcc)

            for match in history:
                result = "🟢 Win" if match["won"] else "🔴 Loss"
                date = datetime.fromisoformat(match["date"]).strftime("%m/%d")

                embed.add_field(
                    name=f"{result} - {date}",
                    value=f"⚽ {match['goals']}G 🛡️ {match['saves']}S 🤝 {match['assists']}A",
                    inline=True
                )
        else:
            embed = discord.Embed(title="📊 No Recent Matches", description="Play some matches to see your history!", color=0xff6600)

        view = discord.ui.View()
        back_btn = discord.ui.Button(label="🔙 Back to Dashboard", style=discord.ButtonStyle.secondary)
        back_btn.callback = self.back_to_dashboard
        view.add_item(back_btn)

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    async def back_to_dashboard(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🚀 OctaneCore Dashboard",
            description="**Welcome back!** Use the buttons below to access all features:",
            color=0x00ffcc
        )
        view = DashboardView()
        await interaction.response.edit_message(embed=embed, view=view)

class MatchCreatorView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
        self.format = None
        self.map_choice = None

    @discord.ui.select(placeholder="Choose format...", options=[
        discord.SelectOption(label="1v1", emoji="⚡"),
        discord.SelectOption(label="2v2", emoji="🤝"),
        discord.SelectOption(label="3v3", emoji="👥")
    ])
    async def format_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.format = select.values[0]
        embed = discord.Embed(title="🎯 Match Creator", description=f"✅ Format: **{self.format}**\nNow choose a map:", color=0xff6600)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.select(placeholder="Choose map...", options=[
        discord.SelectOption(label="DFH Stadium", emoji="🏟️"),
        discord.SelectOption(label="Mannfield", emoji="🌿"),
        discord.SelectOption(label="Champions Field", emoji="🏆"),
        discord.SelectOption(label="Neo Tokyo", emoji="🌸"),
        discord.SelectOption(label="Random", emoji="🎲")
    ])
    async def map_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.map_choice = select.values[0]
        embed = discord.Embed(title="🎯 Match Creator", description=f"✅ Format: **{self.format}**\n✅ Map: **{self.map_choice}**", color=0xff6600)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Create Match", style=discord.ButtonStyle.success, emoji="🚀")
    async def create_match(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.format or not self.map_choice:
            await interaction.response.send_message("❌ Please select format and map first!", ephemeral=True)
            return

        from main import load_matches, save_matches
        import random
        import datetime

        match_name = f"CustomRL{random.randint(1000,9999)}"
        password = f"CRL{random.randint(100,999)}"

        match_data = {
            "id": f"custom_{random.randint(10000, 99999)}",
            "team1_name": "Orange Team",
            "team2_name": "Blue Team",
            "format": self.format,
            "map": self.map_choice,
            "mode": "Soccar",
            "status": "ready",
            "match_name": match_name,
            "password": password,
            "created_at": datetime.datetime.now().isoformat(),
            "created_by": interaction.user.id,
            "type": "custom"
        }

        matches = load_matches()
        matches.append(match_data)
        save_matches(matches)

        embed = discord.Embed(title="🚀 Custom Match Created!", color=0x00ff00)
        embed.add_field(name="🎮 Match Details", value=f"**Format:** {self.format}\n**Map:** {self.map_choice}", inline=False)
        embed.add_field(name="🔑 Join Details", value=f"**Name:** `{match_name}`\n**Password:** `{password}`", inline=False)
        embed.add_field(name="📋 Instructions", value="1. Copy the credentials above\n2. Share with your friends\n3. Join the private match in Rocket League\n4. Have fun!", inline=False)

        view = discord.ui.View()
        back_btn = discord.ui.Button(label="🔙 Back to Dashboard", style=discord.ButtonStyle.secondary)
        back_btn.callback = self.back_to_dashboard
        view.add_item(back_btn)

        await interaction.response.edit_message(embed=embed, view=view)

    @discord.ui.button(label="🔙 Back to Dashboard", style=discord.ButtonStyle.secondary)
    async def back_to_dashboard(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="🚀 OctaneCore Dashboard",
            description="**Welcome back!** Use the buttons below to access all features:",
            color=0x00ffcc
        )
        view = DashboardView()
        await interaction.response.edit_message(embed=embed, view=view)

class LeaderboardView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(label="🏆 MMR Leaderboard", style=discord.ButtonStyle.primary)
    async def mmr_leaderboard(self, interaction: discord.Interaction, button: discord.ui.Button):
        from main import load_stats, bot

        stats = load_stats()
        if not stats:
            await interaction.response.send_message("❌ No player stats found!", ephemeral=True)
            return

        sorted_players = sorted(stats.items(), key=lambda x: x[1]["mmr"], reverse=True)

        embed = discord.Embed(title="🏆 MMR Leaderboard", description="Top ranked players on the server", color=0xFFD700)

        for i, (player_id, player_stats) in enumerate(sorted_players[:10]):
            try:
                user = await bot.fetch_user(int(player_id))
                name = user.display_name
            except:
                name = f"Player {player_id}"

            rank_emoji = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"{i+1}."

            embed.add_field(
                name=f"{rank_emoji} {name}",
                value=f"**{player_stats['rank']}** ({player_stats['mmr']} MMR)\n{player_stats['wins']}W-{player_stats['losses']}L",
                inline=True
            )

        view = discord.ui.View()
        back_btn = discord.ui.Button(label="🔙 Back to Dashboard", style=discord.ButtonStyle.secondary)
        back_btn.callback = self.back_to_dashboard
        view.add_item(back_btn)

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @discord.ui.button(label="⭐ MVP Leaderboard", style=discord.ButtonStyle.secondary)
    async def mvp_leaderboard(self, interaction: discord.Interaction, button: discord.ui.Button):
        from main import load_mvp_votes

        mvp_votes = load_mvp_votes()
        if not mvp_votes:
            await interaction.response.send_message("❌ No MVP votes found!", ephemeral=True)
            return

        mvp_counts = {}
        for match_votes in mvp_votes.values():
            vote_counts = {}
            for vote in match_votes.values():
                vote_counts[vote] = vote_counts.get(vote, 0) + 1

            if vote_counts:
                mvp = max(vote_counts, key=vote_counts.get)
                mvp_counts[mvp] = mvp_counts.get(mvp, 0) + 1

        sorted_mvps = sorted(mvp_counts.items(), key=lambda x: x[1], reverse=True)

        embed = discord.Embed(title="⭐ MVP Leaderboard", description="Most valuable players", color=0xFFD700)

        for i, (player, count) in enumerate(sorted_mvps[:10]):
            rank_emoji = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"{i+1}."
            embed.add_field(
                name=f"{rank_emoji} {player}",
                value=f"**{count}** MVP awards",
                inline=True
            )

        view = discord.ui.View()
        back_btn = discord.ui.Button(label="🔙 Back to Dashboard", style=discord.ButtonStyle.secondary)
        back_btn.callback = self.back_to_dashboard
        view.add_item(back_btn)

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    async def back_to_dashboard(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🚀 OctaneCore Dashboard",
            description="**Welcome back!** Use the buttons below to access all features:",
            color=0x00ffcc
        )
        view = DashboardView()
        await interaction.response.edit_message(embed=embed, view=view)

class AchievementView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(label="🏆 View All Achievements", style=discord.ButtonStyle.primary)
    async def view_all_achievements(self, interaction: discord.Interaction, button: discord.ui.Button):
        from achievements import load_achievements, ACHIEVEMENTS

        achievements = load_achievements()
        player_achievements = achievements.get(str(interaction.user.id), {"unlocked": []})

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

        view = discord.ui.View()
        back_btn = discord.ui.Button(label="🔙 Back to Dashboard", style=discord.ButtonStyle.secondary)
        back_btn.callback = self.back_to_dashboard
        view.add_item(back_btn)

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    async def back_to_dashboard(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🚀 OctaneCore Dashboard",
            description="**Welcome back!** Use the buttons below to access all features:",
            color=0x00ffcc
        )
        view = DashboardView()
        await interaction.response.edit_message(embed=embed, view=view)

# Function to create and send the main dashboard
async def setup_dashboard(channel):
    embed = discord.Embed(
        title="🚀 OctaneCore Dashboard",
        description="**Welcome to the ultimate Rocket League bot!**\n\nUse the buttons below to quickly access all features:",
        color=0x00ffcc
    )

    embed.add_field(
        name="🎮 Quick Actions",
        value="• **Quick Queue** - Smart matchmaking\n• **Create Match** - Custom private matches\n• **My Stats** - Detailed performance tracking",
        inline=True
    )

    embed.add_field(
        name="🏆 Competition",
        value="• **Tournaments** - Competitive events\n• **Leaderboards** - Server rankings\n• **Achievements** - Unlock rewards",
        inline=True
    )

    embed.add_field(
        name="📊 Features",
        value="• **Smart Queue System** - Auto-matching\n• **Advanced Stats** - Detailed tracking\n• **Achievement System** - Rewards & badges\n• **24/7 Uptime** - Always available",
        inline=True
    )

    embed.add_field(
        name="💡 Quick Tips",
        value="• All interactions are private to you\n• Use back buttons to navigate easily\n• Join tournaments for extra rewards\n• Check achievements for MMR bonuses",
        inline=False
    )

    embed.set_footer(text="Dashboard stays active 24/7 • Click any button to get started!")
    embed.set_thumbnail(url="https://images-ext-1.discordapp.net/external/q0ZMEHDP5sKCDBIXcrIGHZzYGV8LO9nrZjwOQnJ8xKE/https/cdn.cloudflare.steamstatic.com/steam/apps/252950/header.jpg")

    view = DashboardView()
    message = await channel.send(embed=embed, view=view)
    return message