
import discord
from discord.ext import commands
import random
import asyncio
from datetime import datetime, timedelta
from utils import *
from main import log_to_channel, update_player_stats, create_auto_match

# Bot testing data
BOT_USERS = [
    {"id": "bot_user_1", "username": "ProRL_Striker", "rank": "Champion I", "mmr": 1320, "playstyle": "aggressive"},
    {"id": "bot_user_2", "username": "AerialMaster99", "rank": "Diamond III", "mmr": 1180, "playstyle": "aerial"},
    {"id": "bot_user_3", "username": "SaveGuardian", "rank": "Diamond II", "mmr": 1050, "playstyle": "defensive"},
    {"id": "bot_user_4", "username": "SpeedDemon_RL", "rank": "Champion II", "mmr": 1380, "playstyle": "fast"},
    {"id": "bot_user_5", "username": "TeamPlayer_Pro", "rank": "Diamond I", "mmr": 980, "playstyle": "support"},
    {"id": "bot_user_6", "username": "ClutchKing777", "rank": "Champion III", "mmr": 1450, "playstyle": "clutch"},
    {"id": "bot_user_7", "username": "FlipReset_God", "rank": "Grand Champion", "mmr": 1520, "playstyle": "mechanical"},
    {"id": "bot_user_8", "username": "PowerShot_Beast", "rank": "Platinum III", "mmr": 850, "playstyle": "power"},
    {"id": "bot_user_9", "username": "NutmegNinja", "rank": "Diamond I", "mmr": 990, "playstyle": "technical"},
    {"id": "bot_user_10", "username": "BoostHoarder", "rank": "Platinum II", "mmr": 780, "playstyle": "boost"},
    {"id": "bot_user_11", "username": "WallRider_Elite", "rank": "Diamond II", "mmr": 1080, "playstyle": "wall"},
    {"id": "bot_user_12", "username": "DemoExpert", "rank": "Champion I", "mmr": 1290, "playstyle": "demo"},
    {"id": "bot_user_13", "username": "CeilingShot_Pro", "rank": "Diamond III", "mmr": 1150, "playstyle": "ceiling"},
    {"id": "bot_user_14", "username": "MidFieldMaestro", "rank": "Champion II", "mmr": 1360, "playstyle": "midfield"},
    {"id": "bot_user_15", "username": "LastSecondHero", "rank": "Diamond I", "mmr": 1020, "playstyle": "pressure"},
    {"id": "bot_user_16", "username": "RotationKing", "rank": "Champion III", "mmr": 1480, "playstyle": "rotation"},
    {"id": "bot_user_17", "username": "FreestyleFanatic", "rank": "Platinum I", "mmr": 650, "playstyle": "freestyle"},
    {"id": "bot_user_18", "username": "GroundGame_God", "rank": "Diamond II", "mmr": 1070, "playstyle": "ground"},
    {"id": "bot_user_19", "username": "PassMaster_RL", "rank": "Champion I", "mmr": 1310, "playstyle": "passing"},
    {"id": "bot_user_20", "username": "OvertimeWarrior", "rank": "Diamond III", "mmr": 1200, "playstyle": "overtime"}
]

def generate_realistic_stats(user_data):
    """Generate realistic player stats based on rank and playstyle"""
    base_matches = random.randint(50, 200)
    
    # Win rate based on rank
    rank_win_rates = {
        "Bronze": 0.45, "Silver": 0.48, "Gold": 0.50,
        "Platinum": 0.52, "Diamond": 0.55, "Champion": 0.58,
        "Grand Champion": 0.65
    }
    
    rank_tier = user_data["rank"].split()[0]
    win_rate = rank_win_rates.get(rank_tier, 0.50)
    
    wins = int(base_matches * win_rate)
    losses = base_matches - wins
    
    # Stats based on playstyle
    if user_data["playstyle"] == "aggressive":
        goals = random.randint(2, 4) * base_matches
        saves = random.randint(1, 2) * base_matches
        assists = random.randint(1, 2) * base_matches
    elif user_data["playstyle"] == "defensive":
        goals = random.randint(1, 2) * base_matches
        saves = random.randint(3, 5) * base_matches
        assists = random.randint(2, 3) * base_matches
    elif user_data["playstyle"] == "support":
        goals = random.randint(1, 2) * base_matches
        saves = random.randint(2, 3) * base_matches
        assists = random.randint(3, 5) * base_matches
    else:  # balanced
        goals = random.randint(2, 3) * base_matches
        saves = random.randint(2, 3) * base_matches
        assists = random.randint(2, 3) * base_matches
    
    return {
        "wins": wins,
        "losses": losses,
        "goals": goals,
        "saves": saves,
        "assists": assists,
        "mmr": user_data["mmr"],
        "matches_played": base_matches,
        "rank": user_data["rank"]
    }

def initialize_bot_users():
    """Initialize all bot users with realistic stats"""
    stats = load_stats()
    
    for user in BOT_USERS:
        if user["id"] not in stats:
            stats[user["id"]] = generate_realistic_stats(user)
    
    save_stats(stats)

def get_random_bot_users(count):
    """Get random bot users for testing"""
    return random.sample(BOT_USERS, min(count, len(BOT_USERS)))

async def simulate_queue_activity(channel, format_type, user_count=6):
    """Simulate queue activity with bot users"""
    queue = load_queue()
    
    # Clear existing queue for this format
    queue = [p for p in queue if p["format"] != format_type]
    
    # Add bot users to queue
    bot_users = get_random_bot_users(user_count)
    
    embed = discord.Embed(title="🧪 Queue Test Started", description=f"Adding {user_count} bot users to {format_type} queue...", color=0x00ffcc)
    message = await channel.send(embed=embed)
    
    for i, user in enumerate(bot_users):
        queue.append({
            "user_id": user["id"],
            "username": user["username"],
            "format": format_type,
            "status": "searching",
            "joined_at": datetime.now().isoformat()
        })
        
        # Update message with progress
        embed.description = f"Adding bot users to {format_type} queue... ({i+1}/{user_count})"
        await message.edit(embed=embed)
        await asyncio.sleep(0.5)
    
    save_queue(queue)
    
    # Final update
    embed.description = f"✅ Added {user_count} bot users to {format_type} queue!"
    embed.add_field(name="Bot Users Added", value="\n".join([f"• {user['username']}" for user in bot_users]), inline=False)
    embed.add_field(name="Next Steps", value="Queue checker will automatically create matches in ~30 seconds", inline=False)
    await message.edit(embed=embed)
    
    await log_to_channel(f"🧪 Queue test: {user_count} bot users added to {format_type} queue", "INFO")

async def simulate_tournament_registration(channel, tournament_count=2):
    """Simulate tournament creation and registration"""
    from main import generate_tournament_matches
    
    tournaments = load_tournaments()
    
    embed = discord.Embed(title="🧪 Tournament Test Started", description="Creating test tournaments with bot users...", color=0xFFD700)
    message = await channel.send(embed=embed)
    
    for t in range(tournament_count):
        # Create tournament
        tournament_id = f"test_tournament_{random.randint(10000, 99999)}"
        tournament_data = {
            "id": tournament_id,
            "type": "Single Elimination",
            "format": random.choice(["2v2", "3v3"]),
            "map": random.choice(["DFH Stadium", "Mannfield", "Champions Field"]),
            "mode": "Soccar",
            "max_teams": 8,
            "status": "registration",
            "teams": [],
            "matches": [],
            "created_at": datetime.now().isoformat(),
            "created_by": "test_system",
            "prize_pool": random.randint(100, 1000),
            "current_round": 0,
            "registration_deadline": (datetime.now() + timedelta(hours=1)).isoformat()
        }
        
        # Register bot teams
        team_count = random.randint(4, 8)
        available_users = BOT_USERS.copy()
        
        for team_num in range(team_count):
            players_needed = 2 if tournament_data["format"] == "2v2" else 3
            team_users = random.sample(available_users, players_needed)
            
            # Remove used users
            for user in team_users:
                available_users.remove(user)
            
            team_data = {
                "name": f"Team {random.choice(['Alpha', 'Beta', 'Gamma', 'Delta', 'Epsilon', 'Zeta', 'Eta', 'Theta'])}",
                "players": [user["username"] for user in team_users],
                "captain": team_users[0]["id"],
                "registered_at": datetime.now().isoformat()
            }
            
            tournament_data["teams"].append(team_data)
        
        # Generate matches
        tournament_data["status"] = "active"
        tournament_data["current_round"] = 1
        tournament_data["matches"] = generate_tournament_matches(
            tournament_data["teams"],
            tournament_data["format"],
            tournament_data["map"],
            tournament_data["mode"]
        )
        
        tournaments.append(tournament_data)
        
        # Update progress
        embed.description = f"Created tournament {t+1}/{tournament_count}: {tournament_id}"
        await message.edit(embed=embed)
        await asyncio.sleep(1)
    
    save_tournaments(tournaments)
    
    # Final update
    embed.description = f"✅ Created {tournament_count} test tournaments with bot teams!"
    embed.add_field(name="Tournaments Created", value="\n".join([f"• {t['id']}" for t in tournaments[-tournament_count:]]), inline=False)
    embed.add_field(name="Features Tested", value="• Tournament creation\n• Team registration\n• Match generation\n• Bracket setup", inline=False)
    await message.edit(embed=embed)
    
    await log_to_channel(f"🧪 Tournament test: {tournament_count} tournaments created with bot teams", "INFO")

async def simulate_match_results(channel, match_count=5):
    """Simulate match results with bot users"""
    from main import load_matches, save_matches
    
    matches = load_matches()
    history = load_match_history()
    
    embed = discord.Embed(title="🧪 Match Simulation Started", description="Generating realistic match results...", color=0xff6600)
    message = await channel.send(embed=embed)
    
    for i in range(match_count):
        # Create a match
        bot_users = get_random_bot_users(6)
        team1 = bot_users[:3]
        team2 = bot_users[3:]
        
        match_id = f"test_match_{random.randint(10000, 99999)}"
        
        # Simulate match outcome based on team MMR
        team1_avg_mmr = sum(user["mmr"] for user in team1) / len(team1)
        team2_avg_mmr = sum(user["mmr"] for user in team2) / len(team2)
        
        # Higher MMR team is more likely to win
        if team1_avg_mmr > team2_avg_mmr:
            team1_score = random.randint(3, 7)
            team2_score = random.randint(0, team1_score - 1)
        else:
            team2_score = random.randint(3, 7)
            team1_score = random.randint(0, team2_score - 1)
        
        # Generate individual stats
        team1_goals = []
        team2_goals = []
        
        for _ in range(len(team1)):
            goals = random.randint(0, max(1, team1_score // 2))
            team1_goals.append(goals)
        
        for _ in range(len(team2)):
            goals = random.randint(0, max(1, team2_score // 2))
            team2_goals.append(goals)
        
        # Update player stats
        for j, user in enumerate(team1):
            won = team1_score > team2_score
            update_player_stats(user["id"], win=won, goals=team1_goals[j], saves=random.randint(1, 4), assists=random.randint(0, 3), match_id=match_id)
        
        for j, user in enumerate(team2):
            won = team2_score > team1_score
            update_player_stats(user["id"], win=won, goals=team2_goals[j], saves=random.randint(1, 4), assists=random.randint(0, 3), match_id=match_id)
        
        # Save to history
        history.append({
            "match_id": match_id,
            "date": datetime.now().isoformat(),
            "orange_score": team1_score,
            "blue_score": team2_score,
            "orange_players": [user["username"] for user in team1],
            "blue_players": [user["username"] for user in team2],
            "orange_goals": team1_goals,
            "blue_goals": team2_goals,
            "format": "3v3",
            "map": random.choice(["DFH Stadium", "Mannfield", "Champions Field"])
        })
        
        # Update progress
        embed.description = f"Simulating matches... ({i+1}/{match_count})"
        await message.edit(embed=embed)
        await asyncio.sleep(0.5)
    
    save_match_history(history)
    
    # Final update
    embed.description = f"✅ Simulated {match_count} matches with realistic results!"
    embed.add_field(name="Features Tested", value="• Match result generation\n• Player stat updates\n• MMR calculations\n• Match history tracking", inline=False)
    embed.add_field(name="Sample Results", value="\n".join([f"• {h['orange_players'][0]} vs {h['blue_players'][0]}: {h['orange_score']}-{h['blue_score']}" for h in history[-3:]]), inline=False)
    await message.edit(embed=embed)
    
    await log_to_channel(f"🧪 Match simulation: {match_count} matches completed", "INFO")

async def run_full_system_test(channel):
    """Run comprehensive system test"""
    embed = discord.Embed(title="🧪 Full System Test", description="Running comprehensive bot test...", color=0x9b59b6)
    message = await channel.send(embed=embed)
    
    test_steps = [
        "Initializing bot users",
        "Simulating queue activity",
        "Creating test tournaments",
        "Generating match results",
        "Testing achievements",
        "Finalizing test data"
    ]
    
    for i, step in enumerate(test_steps):
        embed.description = f"Step {i+1}/6: {step}..."
        await message.edit(embed=embed)
        
        if i == 0:
            initialize_bot_users()
        elif i == 1:
            await simulate_queue_activity(channel, "2v2", 4)
            await asyncio.sleep(2)
            await simulate_queue_activity(channel, "3v3", 6)
        elif i == 2:
            await simulate_tournament_registration(channel, 2)
        elif i == 3:
            await simulate_match_results(channel, 8)
        elif i == 4:
            # Test achievements
            from achievements import check_achievements
            test_user = BOT_USERS[0]
            match_data = {"won": True, "goals": 3, "saves": 2, "assists": 1}
            achievements = check_achievements(test_user["id"], match_data)
        elif i == 5:
            # Final cleanup and summary
            pass
        
        await asyncio.sleep(1)
    
    # Final summary
    stats = load_stats()
    history = load_match_history()
    tournaments = load_tournaments()
    queue = load_queue()
    
    embed.title = "✅ Full System Test Complete"
    embed.description = "All bot systems tested successfully!"
    embed.add_field(name="📊 Test Summary", value=f"• Players: {len(stats)}\n• Matches: {len(history)}\n• Tournaments: {len(tournaments)}\n• Queue: {len(queue)}", inline=False)
    embed.add_field(name="✅ Systems Tested", value="• Queue system\n• Tournament creation\n• Match simulation\n• Player statistics\n• Achievement system\n• Admin controls", inline=False)
    embed.color = 0x00ff00
    
    await message.edit(embed=embed)
    await log_to_channel("🧪 Full system test completed successfully", "SUCCESS")

class TestingView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.custom_id = "testing_persistent"

    @discord.ui.button(label="🎮 Test Queue System", style=discord.ButtonStyle.primary, custom_id="test_queue")
    async def test_queue(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Admin only!", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        embed = discord.Embed(title="🎮 Queue Test Options", description="Choose what to test:", color=0x00ffcc)
        
        view = discord.ui.View()
        
        # Queue format buttons
        view.add_item(discord.ui.Button(label="Test 1v1 Queue", style=discord.ButtonStyle.secondary, custom_id="test_1v1"))
        view.add_item(discord.ui.Button(label="Test 2v2 Queue", style=discord.ButtonStyle.secondary, custom_id="test_2v2"))
        view.add_item(discord.ui.Button(label="Test 3v3 Queue", style=discord.ButtonStyle.secondary, custom_id="test_3v3"))
        
        # Set up callbacks
        for item in view.children:
            if hasattr(item, 'custom_id'):
                if item.custom_id == "test_1v1":
                    item.callback = lambda i: self.test_queue_format(i, "1v1")
                elif item.custom_id == "test_2v2":
                    item.callback = lambda i: self.test_queue_format(i, "2v2")
                elif item.custom_id == "test_3v3":
                    item.callback = lambda i: self.test_queue_format(i, "3v3")
        
        await interaction.followup.send(embed=embed, view=view)

    async def test_queue_format(self, interaction, format_type):
        await interaction.response.defer()
        
        players_needed = {"1v1": 2, "2v2": 4, "3v3": 6}[format_type]
        await simulate_queue_activity(interaction.channel, format_type, players_needed)
        
        embed = discord.Embed(title="✅ Queue Test Started", description=f"Bot users added to {format_type} queue. Check the queue status to see them!", color=0x00ff00)
        await interaction.followup.send(embed=embed, ephemeral=True)

    @discord.ui.button(label="🏆 Test Tournaments", style=discord.ButtonStyle.success, custom_id="test_tournaments")
    async def test_tournaments(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Admin only!", ephemeral=True)
            return
        
        await interaction.response.defer()
        await simulate_tournament_registration(interaction.channel, 1)
        
        embed = discord.Embed(title="✅ Tournament Test Complete", description="Test tournament created with bot teams!", color=0x00ff00)
        await interaction.followup.send(embed=embed, ephemeral=True)

    @discord.ui.button(label="📊 Test Match Results", style=discord.ButtonStyle.secondary, custom_id="test_matches")
    async def test_matches(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Admin only!", ephemeral=True)
            return
        
        await interaction.response.defer()
        await simulate_match_results(interaction.channel, 3)
        
        embed = discord.Embed(title="✅ Match Test Complete", description="Test matches simulated with realistic results!", color=0x00ff00)
        await interaction.followup.send(embed=embed, ephemeral=True)

    @discord.ui.button(label="🧪 Full System Test", style=discord.ButtonStyle.danger, custom_id="full_test")
    async def full_system_test(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Admin only!", ephemeral=True)
            return
        
        await interaction.response.defer()
        await run_full_system_test(interaction.channel)
        
        embed = discord.Embed(title="✅ Full System Test Complete", description="All bot systems tested successfully!", color=0x00ff00)
        await interaction.followup.send(embed=embed, ephemeral=True)

    @discord.ui.button(label="🔄 Reset Test Data", style=discord.ButtonStyle.danger, custom_id="reset_test")
    async def reset_test_data(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Admin only!", ephemeral=True)
            return
        
        # Clear all test data
        stats = load_stats()
        queue = load_queue()
        history = load_match_history()
        tournaments = load_tournaments()
        
        # Remove bot users
        for user in BOT_USERS:
            if user["id"] in stats:
                del stats[user["id"]]
        
        # Remove bot users from queue
        queue = [p for p in queue if not p["user_id"].startswith("bot_user_")]
        
        # Remove test matches
        history = [h for h in history if not h["match_id"].startswith("test_match_")]
        
        # Remove test tournaments
        tournaments = [t for t in tournaments if not t["id"].startswith("test_tournament_")]
        
        save_stats(stats)
        save_queue(queue)
        save_match_history(history)
        save_tournaments(tournaments)
        
        await interaction.response.send_message("✅ Test data cleared!", ephemeral=True)

# Function to setup testing dashboard
async def setup_testing_dashboard(channel):
    embed = discord.Embed(
        title="🧪 OctaneCore Testing Dashboard",
        description="**Bot Testing & Simulation Hub**\n\nTest all bot features with realistic simulated users and scenarios.",
        color=0x9b59b6
    )
    
    embed.add_field(
        name="🎮 Available Tests",
        value="• **Queue System** - Test matchmaking with bot users\n• **Tournaments** - Create tournaments with bot teams\n• **Match Results** - Simulate realistic match outcomes\n• **Full System** - Comprehensive test of all features",
        inline=False
    )
    
    embed.add_field(
        name="🤖 Bot Users",
        value=f"• **{len(BOT_USERS)}** realistic bot users\n• Various ranks and playstyles\n• Authentic statistics and behaviors\n• Automatic match simulation",
        inline=False
    )
    
    embed.add_field(
        name="⚠️ Admin Only",
        value="Testing features require Administrator permissions. All test data can be reset.",
        inline=False
    )
    
    embed.set_footer(text="Testing Dashboard • Safe testing environment")
    
    view = TestingView()
    message = await channel.send(embed=embed, view=view)
    return message
