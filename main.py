
import discord
from discord.ext import commands, tasks
from discord import app_commands
import os, json, asyncio, random, datetime, time
from bracket import generate_bracket_image
from flask import Flask, render_template_string, jsonify
import threading
from data import load_data, save_data
from utils import *

TOKEN = os.getenv("BOT_TOKEN")
LOG_CHANNEL_ID = "1390470987971166208"  # Your specified log channel

if not TOKEN:
    print("❌ ERROR: BOT_TOKEN environment variable not found!")
    print("Please add your Discord bot token to the Secrets tab.")
    exit(1)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# Global variables for tracking
bot.dashboard_messages = []
bot.last_queue_state = {}
bot.uptime_start = None

# Flask app for 24/7 uptime monitoring
app = Flask(__name__)

@app.route('/')
def home():
    try:
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>OctaneCore Bot - Professional Gaming Community</title>
            <meta http-equiv="refresh" content="25">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body { 
                    font-family: 'Arial', sans-serif; 
                    background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%); 
                    color: #fff; 
                    min-height: 100vh;
                    padding: 20px;
                }
                .container { max-width: 1200px; margin: 0 auto; }
                .header { text-align: center; margin-bottom: 40px; }
                .header h1 { font-size: 3em; color: #00ffcc; text-shadow: 0 0 20px #00ffcc; }
                .header p { font-size: 1.2em; color: #888; margin-top: 10px; }
                .status { 
                    background: linear-gradient(45deg, #2d2d2d, #3d3d3d); 
                    padding: 30px; 
                    border-radius: 15px; 
                    margin: 30px 0; 
                    border-left: 5px solid #00ff00;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                }
                .status h2 { color: #00ff00; font-size: 2em; margin-bottom: 15px; }
                .status-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 20px; }
                .status-item { background: #1a1a1a; padding: 15px; border-radius: 10px; text-align: center; }
                .status-value { font-size: 1.5em; color: #00ffcc; font-weight: bold; }
                .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 25px; margin: 40px 0; }
                .stat-card { 
                    background: linear-gradient(45deg, #2d2d2d, #3d3d3d); 
                    padding: 25px; 
                    border-radius: 15px; 
                    text-align: center; 
                    transition: transform 0.3s ease;
                    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
                }
                .stat-card:hover { transform: translateY(-5px); }
                .stat-number { font-size: 2.5em; font-weight: bold; color: #00ffcc; margin-bottom: 10px; }
                .stat-label { color: #888; font-size: 1.1em; }
                .features { margin: 40px 0; }
                .features h3 { color: #00ffcc; font-size: 1.8em; margin-bottom: 20px; text-align: center; }
                .feature-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
                .feature { background: #2d2d2d; padding: 20px; border-radius: 10px; border-left: 3px solid #00ffcc; }
                .feature h4 { color: #fff; margin-bottom: 10px; }
                .feature p { color: #aaa; line-height: 1.6; }
                .footer { text-align: center; margin-top: 50px; padding: 30px; background: #1a1a1a; border-radius: 10px; }
                .pulse { animation: pulse 2s infinite; }
                @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.7; } 100% { opacity: 1; } }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 OctaneCore</h1>
                    <p>Professional Gaming Community • Discord Bot</p>
                </div>
                
                <div class="status">
                    <h2>✅ System Status: Online</h2>
                    <div class="status-grid">
                        <div class="status-item">
                            <div class="status-value">{{ uptime }}</div>
                            <div>Uptime</div>
                        </div>
                        <div class="status-item">
                            <div class="status-value pulse">LIVE</div>
                            <div>Status</div>
                        </div>
                        <div class="status-item">
                            <div class="status-value">{{ current_time }}</div>
                            <div>Last Update</div>
                        </div>
                        <div class="status-item">
                            <div class="status-value">24/7</div>
                            <div>Availability</div>
                        </div>
                    </div>
                </div>

                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-number">{{ total_matches }}</div>
                        <div class="stat-label">Total Matches</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{{ active_tournaments }}</div>
                        <div class="stat-label">Active Tournaments</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{{ queue_count }}</div>
                        <div class="stat-label">Players in Queue</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{{ registered_players }}</div>
                        <div class="stat-label">Registered Players</div>
                    </div>
                </div>

                <div class="features">
                    <h3>🎮 Bot Features</h3>
                    <div class="feature-grid">
                        <div class="feature">
                            <h4>⚡ Smart Matchmaking</h4>
                            <p>AI-powered queue system that creates balanced matches across all skill levels with sub-minute wait times.</p>
                        </div>
                        <div class="feature">
                            <h4>🏆 Tournament System</h4>
                            <p>Automated tournaments every 2 hours with bracket generation, prize distribution, and live tracking.</p>
                        </div>
                        <div class="feature">
                            <h4>📊 Advanced Analytics</h4>
                            <p>Comprehensive statistics tracking, MMR system, achievements, and detailed performance insights.</p>
                        </div>
                        <div class="feature">
                            <h4>🎯 Multiple Game Modes</h4>
                            <p>Support for Soccar, Hoops, Snow Day, and Heatseeker across 1v1, 2v2, and 3v3 formats.</p>
                        </div>
                        <div class="feature">
                            <h4>💰 Economy System</h4>
                            <p>Earn credits through gameplay, daily rewards, tournaments, and spend them in the shop.</p>
                        </div>
                        <div class="feature">
                            <h4>🏰 Clan System</h4>
                            <p>Create teams, compete in clan wars, and unlock exclusive perks and benefits.</p>
                        </div>
                    </div>
                </div>

                <div class="footer">
                    <h3>🤖 System Information</h3>
                    <p>Hosted on Replit • Auto-refreshes every 25 seconds for 24/7 uptime</p>
                    <p>Professional Discord bot for competitive Rocket League communities</p>
                    <p style="margin-top: 20px; color: #00ffcc;">Ready to deploy to your community server!</p>
                </div>
            </div>
        </body>
        </html>
        """, 
        current_time=datetime.datetime.now().strftime("%H:%M:%S"),
        uptime=get_uptime(),
        total_matches=len(load_matches()) if load_matches() else 0,
        active_tournaments=len([t for t in load_tournaments() if t.get('status') == 'active']) if load_tournaments() else 0,
        queue_count=len(load_queue()) if load_queue() else 0,
        registered_players=len(load_stats()) if load_stats() else 0
        )
    except Exception as e:
        return f"""
        <html>
        <head><title>OctaneCore Status</title></head>
        <body style="background:#1a1a1a;color:#fff;font-family:Arial;padding:50px;text-align:center;">
            <h1>🚀 OctaneCore Bot</h1>
            <h2 style="color:#00ff00;">✅ Online & Running</h2>
            <p>Error loading detailed stats: {str(e)}</p>
            <p style="margin-top:30px;color:#888;">This keeps the bot alive 24/7 on Replit</p>
        </body>
        </html>
        """

@app.route('/api/status')
def api_status():
    return jsonify({
        'status': 'online',
        'uptime': get_uptime(),
        'total_matches': len(load_matches()),
        'active_tournaments': len([t for t in load_tournaments() if t['status'] == 'active']),
        'queue_count': len(load_queue()),
        'registered_players': len(load_stats())
    })

def get_uptime():
    uptime_seconds = int(time.time() - bot.start_time)
    hours, remainder = divmod(uptime_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}h {minutes}m {seconds}s"

def run_flask():
    app.run(host='0.0.0.0', port=5000, debug=False)



# Functions now imported from utils module

def update_player_stats(player_id, win=False, goals=0, saves=0, assists=0, match_id=None):
    stats = load_stats()
    
    if player_id not in stats:
        stats[player_id] = {
            "wins": 0,
            "losses": 0,
            "goals": 0,
            "saves": 0,
            "assists": 0,
            "mmr": 1000,
            "matches_played": 0,
            "rank": "Bronze I"
        }
    
    stats[player_id]["matches_played"] += 1
    if win:
        stats[player_id]["wins"] += 1
        stats[player_id]["mmr"] += random.randint(15, 25)
    else:
        stats[player_id]["losses"] += 1
        stats[player_id]["mmr"] -= random.randint(10, 20)
    
    stats[player_id]["goals"] += goals
    stats[player_id]["saves"] += saves
    stats[player_id]["assists"] += assists
    
    # Add match to player's history
    if "match_history" not in stats[player_id]:
        stats[player_id]["match_history"] = []
    
    if match_id:
        stats[player_id]["match_history"].append({
            "match_id": match_id,
            "date": datetime.datetime.now().isoformat(),
            "won": win,
            "goals": goals,
            "saves": saves,
            "assists": assists
        })
    
    # Update rank based on MMR
    mmr = stats[player_id]["mmr"]
    if mmr >= 1500:
        stats[player_id]["rank"] = "Grand Champion"
    elif mmr >= 1400:
        stats[player_id]["rank"] = "Champion III"
    elif mmr >= 1300:
        stats[player_id]["rank"] = "Champion II"
    elif mmr >= 1200:
        stats[player_id]["rank"] = "Champion I"
    elif mmr >= 1100:
        stats[player_id]["rank"] = "Diamond III"
    elif mmr >= 1000:
        stats[player_id]["rank"] = "Diamond II"
    elif mmr >= 900:
        stats[player_id]["rank"] = "Diamond I"
    elif mmr >= 800:
        stats[player_id]["rank"] = "Platinum III"
    elif mmr >= 700:
        stats[player_id]["rank"] = "Platinum II"
    elif mmr >= 600:
        stats[player_id]["rank"] = "Platinum I"
    elif mmr >= 500:
        stats[player_id]["rank"] = "Gold III"
    elif mmr >= 400:
        stats[player_id]["rank"] = "Gold II"
    elif mmr >= 300:
        stats[player_id]["rank"] = "Gold I"
    elif mmr >= 200:
        stats[player_id]["rank"] = "Silver III"
    elif mmr >= 100:
        stats[player_id]["rank"] = "Silver II"
    elif mmr >= 50:
        stats[player_id]["rank"] = "Silver I"
    else:
        stats[player_id]["rank"] = "Bronze I"
    
    save_stats(stats)
    
    # Reward credits for match participation
    try:
        from economy import reward_match_completion
        numeric_id = int(player_id.replace("player_", "")) if "player_" in str(player_id) else int(player_id)
        reward_match_completion(numeric_id, win)
    except:
        pass  # Economy system not available or invalid ID

async def log_to_channel(message, level="INFO"):
    """Send logs to the designated log channel"""
    if not LOG_CHANNEL_ID:
        return
    
    try:
        log_channel = bot.get_channel(int(LOG_CHANNEL_ID))
        if log_channel:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Color coding for different log levels
            colors = {
                "INFO": 0x00ffcc,
                "WARNING": 0xffa500,
                "ERROR": 0xff0000,
                "SUCCESS": 0x00ff00
            }
            
            embed = discord.Embed(
                title=f"🤖 Bot Log - {level}",
                description=f"**{timestamp}**\n{message}",
                color=colors.get(level, 0x00ffcc)
            )
            
            await log_channel.send(embed=embed)
    except Exception as e:
        print(f"Failed to send log: {e}")

def format_uptime(seconds):
    """Convert seconds to a readable uptime format"""
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    elif seconds < 86400:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"
    else:
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        return f"{days}d {hours}h"

@tasks.loop(seconds=15)
async def update_bot_status():
    """Update bot status with uptime"""
    if bot.uptime_start:
        uptime = time.time() - bot.uptime_start
        uptime_str = format_uptime(uptime)
        
        # Count active users
        queue = load_queue()
        active_players = len([p for p in queue if p["status"] == "searching"])
        
        status_text = f"🕐 Up {uptime_str} | 🎮 {active_players} in queue"
        
        try:
            await bot.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.watching,
                    name=status_text
                )
            )
        except Exception as e:
            print(f"Failed to update status: {e}")

@tasks.loop(seconds=30)
async def update_dashboards():
    """Update all dashboard messages every 30 seconds"""
    try:
        from dashboard import DashboardView
        
        # Update main dashboards
        for message_info in bot.dashboard_messages[:]:
            try:
                channel = bot.get_channel(message_info['channel_id'])
                if channel:
                    message = await channel.fetch_message(message_info['message_id'])
                    
                    # Create updated embed
                    embed = discord.Embed(
                        title="🚀 OctaneCore Dashboard",
                        description="**Welcome to the ultimate Rocket League bot!**\n\nUse the buttons below to quickly access all features:",
                        color=0x00ffcc
                    )

                    queue = load_queue()
                    queue_counts = {"1v1": 0, "2v2": 0, "3v3": 0}
                    for player in queue:
                        if player["status"] == "searching":
                            queue_counts[player["format"]] += 1

                    embed.add_field(
                        name="🎮 Live Queue Status",
                        value=f"**1v1:** {queue_counts['1v1']} players\n**2v2:** {queue_counts['2v2']} players\n**3v3:** {queue_counts['3v3']} players",
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

                    # Show recent activity
                    history = load_match_history()
                    recent_matches = [m for m in history if (datetime.datetime.now() - datetime.datetime.fromisoformat(m["date"])).seconds < 1800]  # Last 30 minutes
                    
                    embed.add_field(
                        name="📈 Recent Activity (30min)",
                        value=f"**{len(recent_matches)}** matches completed\n**{len(queue)}** players in queue",
                        inline=False
                    )

                    uptime = format_uptime(time.time() - bot.uptime_start) if bot.uptime_start else "Unknown"
                    embed.set_footer(text=f"🤖 Bot Uptime: {uptime} | Auto-updates every 30s")
                    embed.set_thumbnail(url="https://images-ext-1.discordapp.net/external/q0ZMEHDP5sKCDBIXcrIGHZzYGV8LO9nrZjwOQnJ8xKE/https/cdn.cloudflare.steamstatic.com/steam/apps/252950/header.jpg")

                    view = DashboardView()
                    await message.edit(embed=embed, view=view)
                    
            except discord.NotFound:
                # Message was deleted, remove from tracking
                bot.dashboard_messages.remove(message_info)
            except Exception as e:
                print(f"Failed to update dashboard: {e}")
                
        # Log queue updates if there are changes
        queue = load_queue()
        current_queue_state = {}
        for player in queue:
            if player["status"] == "searching":
                format_type = player["format"]
                current_queue_state[format_type] = current_queue_state.get(format_type, 0) + 1
        
        if current_queue_state != bot.last_queue_state:
            bot.last_queue_state = current_queue_state
            queue_info = " | ".join([f"{fmt}: {count}" for fmt, count in current_queue_state.items()])
            await log_to_channel(f"Queue Updated: {queue_info if queue_info else 'Empty'}", "INFO")
            
    except Exception as e:
        print(f"Dashboard update error: {e}")

@bot.event
async def on_ready():
    bot.start_time = time.time()
    bot.uptime_start = time.time()
    await tree.sync()
    print(f"✅ {bot.user} is online.")
    
    # Start all tasks
    queue_checker.start()
    tournament_updater.start()
    auto_tournament_creator.start()
    update_bot_status.start()
    update_dashboards.start()
    
    # Log bot startup
    await log_to_channel(f"🚀 Bot started successfully! Servers: {len(bot.guilds)}", "SUCCESS")
    
    # Start Flask server in background
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

@tasks.loop(seconds=15)
async def queue_checker():
    """Check queue for matches every 15 seconds with enhanced logging"""
    try:
        await log_to_channel("🔍 Queue Check: Starting queue analysis...", "DEBUG")
        
        queue = load_queue()
        matches = load_matches()
        
        # Log current queue state
        queue_status = {}
        for mode in ["1v1", "2v2", "3v3"]:
            for game_mode in ["Soccar", "Hoops", "Snow Day", "Heatseeker"]:
                key = f"{mode}_{game_mode}"
                queue_status[key] = len([p for p in queue if p["status"] == "searching" and p.get("format") == mode and p.get("game_mode", "Soccar") == game_mode])
        
        await log_to_channel(f"📊 Queue Status: {queue_status}", "DEBUG")
        
        # Group players by format and game mode
        formats = {}
        for player in queue:
            if player["status"] == "searching":
                format_type = player["format"]
                game_mode = player.get("game_mode", "Soccar")
                key = f"{format_type}_{game_mode}"
                if key not in formats:
                    formats[key] = []
                formats[key].append(player)
        
        matches_created = 0
        failed_matches = 0
        
        # Try to create matches for all game modes
        for format_key, players in formats.items():
            format_type, game_mode = format_key.split('_', 1)
            needed_players = {"1v1": 2, "2v2": 4, "3v3": 6}[format_type]
            
            if len(players) >= needed_players:
                try:
                    selected = random.sample(players, needed_players)
                    
                    # Create teams based on format
                    if format_type == "1v1":
                        team1, team2 = [selected[0]], [selected[1]]
                    elif format_type == "2v2":
                        team1, team2 = selected[:2], selected[2:]
                    else:  # 3v3
                        team1, team2 = selected[:3], selected[3:]
                    
                    # Simulate match acceptance (10% chance of failure)
                    if random.random() < 0.1:
                        failed_matches += 1
                        await log_to_channel(f"❌ Match Failed: Players didn't accept {format_type} {game_mode} match", "WARNING")
                        # Remove one random player who "didn't accept"
                        queue = [p for p in queue if p["user_id"] != random.choice(selected)["user_id"]]
                        continue
                    
                    match_id = create_auto_match(team1, team2, format_type, game_mode)
                    matches_created += 1
                    
                    # Remove all players from queue
                    queue = [p for p in queue if p["user_id"] not in [p["user_id"] for p in selected]]
                    
                    # Enhanced logging
                    team1_names = ", ".join([p['username'] for p in team1])
                    team2_names = ", ".join([p['username'] for p in team2])
                    await log_to_channel(f"🎮 {format_type} {game_mode} Match Created!", "SUCCESS")
                    await log_to_channel(f"🟠 Orange: {team1_names}", "INFO")
                    await log_to_channel(f"🔵 Blue: {team2_names}", "INFO")
                    await log_to_channel(f"🆔 Match ID: {match_id}", "INFO")
                    
                    # Update dashboards immediately
                    await update_all_dashboards()
                    
                except Exception as e:
                    await log_to_channel(f"❌ Error creating {format_key} match: {str(e)}", "ERROR")
        
        save_queue(queue)
        
        # Comprehensive logging
        if matches_created > 0 or failed_matches > 0:
            await log_to_channel(f"🎯 Queue Results: {matches_created} matches created, {failed_matches} failed", "INFO")
        
        # Log queue timeouts (players waiting too long)
        now = datetime.datetime.now()
        timeout_players = []
        for player in queue:
            join_time = datetime.datetime.fromisoformat(player['joined_at'])
            if (now - join_time).seconds > 600:  # 10 minutes
                timeout_players.append(player)
        
        if timeout_players:
            queue = [p for p in queue if p not in timeout_players]
            save_queue(queue)
            await log_to_channel(f"⏰ Queue Timeout: Removed {len(timeout_players)} players (waiting >10min)", "WARNING")
            
    except Exception as e:
        await log_to_channel(f"❌ CRITICAL: Queue Checker Failed: {str(e)}", "ERROR")
        await log_to_channel(f"🔧 Stack Trace: {type(e).__name__}: {str(e)}", "ERROR")
        print(f"Queue checker error: {e}")

async def update_all_dashboards():
    """Immediately update all dashboard messages"""
    try:
        for message_info in bot.dashboard_messages[:]:
            try:
                channel = bot.get_channel(message_info['channel_id'])
                if channel:
                    message = await channel.fetch_message(message_info['message_id'])
                    await update_dashboard_message(message)
            except:
                pass
    except Exception as e:
        await log_to_channel(f"❌ Dashboard Update Error: {str(e)}", "ERROR")

def create_auto_match(team1, team2, format_type, game_mode="Soccar"):
    match_id = f"auto_{random.randint(10000, 99999)}"
    
    # Game mode specific maps
    maps = {
        "Soccar": ["DFH Stadium", "Mannfield", "Champions Field", "Neo Tokyo", "Urban Central", "Beckwith Park"],
        "Hoops": ["Dunk House", "The Block (Hoops)"],
        "Snow Day": ["Snowy DFH Stadium", "Wintry Mannfield"],
        "Heatseeker": ["DFH Stadium", "Mannfield", "Champions Field"]
    }
    
    match_data = {
        "id": match_id,
        "team1_name": "Orange Team",
        "team2_name": "Blue Team",
        "orange_players": [p["username"] for p in team1],
        "blue_players": [p["username"] for p in team2],
        "format": format_type,
        "map": random.choice(maps.get(game_mode, maps["Soccar"])),
        "mode": game_mode,
        "status": "ready",
        "match_name": f"AutoRL{random.randint(1000,9999)}",
        "password": f"AUTO{random.randint(100,999)}",
        "created_at": datetime.datetime.now().isoformat(),
        "type": "auto_matched",
        "game_mode": game_mode,
        "estimated_duration": "5 minutes",
        "priority": "normal"
    }
    
    matches = load_matches()
    matches.append(match_data)
    save_matches(matches)
    
    # Add to match history with status
    history = load_match_history()
    history.append({
        "match_id": match_id,
        "date": datetime.datetime.now().isoformat(),
        "status": "created",
        "format": format_type,
        "mode": game_mode,
        "orange_players": [p["username"] for p in team1],
        "blue_players": [p["username"] for p in team2],
        "map": match_data["map"],
        "type": "auto_matched"
    })
    save_match_history(history)
    
    return match_id

@tasks.loop(minutes=5)
async def tournament_updater():
    """Update tournament status every 5 minutes"""
    try:
        tournaments = load_tournaments()
        tournaments_started = 0
        
        for tournament in tournaments:
            if tournament["status"] == "registration" and tournament.get("auto_start_time"):
                start_time = datetime.datetime.fromisoformat(tournament["auto_start_time"])
                if datetime.datetime.now() >= start_time:
                    tournament["status"] = "active"
                    tournaments_started += 1
                    
                    # Generate first round matches
                    teams = tournament.get("teams", [])
                    if len(teams) >= 2:
                        tournament["current_round"] = 1
                        tournament["matches"] = generate_tournament_matches(teams, tournament["format"], tournament["map"], tournament["mode"])
                        
                        await log_to_channel(f"🏆 Tournament Started: {tournament['id']} with {len(teams)} teams", "SUCCESS")
                    else:
                        await log_to_channel(f"⚠️ Tournament {tournament['id']} started but insufficient teams ({len(teams)})", "WARNING")
        
        save_tournaments(tournaments)
        
        if tournaments_started > 0:
            await log_to_channel(f"🏆 Tournament Update: {tournaments_started} tournaments started", "INFO")
            
    except Exception as e:
        await log_to_channel(f"❌ Tournament Updater Error: {str(e)}", "ERROR")
        print(f"Tournament updater error: {e}")

@tasks.loop(minutes=1)
async def auto_tournament_creator():
    """Create auto tournaments based on admin settings"""
    try:
        settings = load_admin_settings()
        auto_settings = settings.get("auto_tournament", {})
        
        if not auto_settings.get("enabled", False):
            return
        
        if not auto_settings.get("channel_id"):
            return
        
        # Check if it's time to create a tournament
        current_time = datetime.datetime.now()
        last_tournament_time = auto_settings.get("last_created")
        
        if last_tournament_time:
            last_time = datetime.datetime.fromisoformat(last_tournament_time)
            interval_minutes = auto_settings.get("interval_minutes", 60)
            
            if (current_time - last_time).total_seconds() < interval_minutes * 60:
                return
        
        # Get the channel
        channel = bot.get_channel(auto_settings["channel_id"])
        if not channel:
            await log_to_channel("❌ Auto tournament channel not found", "ERROR")
            return
        
        # Create tournament
        tournament_id = await create_auto_tournament(channel)
        
        # Update last created time
        auto_settings["last_created"] = current_time.isoformat()
        settings["auto_tournament"] = auto_settings
        save_admin_settings(settings)
        
        await log_to_channel(f"🔄 Auto tournament created: {tournament_id}", "SUCCESS")
        
    except Exception as e:
        await log_to_channel(f"❌ Auto Tournament Creator Error: {str(e)}", "ERROR")
        print(f"Auto tournament creator error: {e}")

async def create_auto_tournament(channel):
    """Create an automatic tournament"""
    settings = load_admin_settings()
    auto_settings = settings.get("auto_tournament", {})
    
    tournament_id = f"auto_tournament_{random.randint(10000, 99999)}"
    
    tournament_data = {
        "id": tournament_id,
        "type": "Single Elimination",
        "format": auto_settings.get("format", "3v3"),
        "map": auto_settings.get("map", "DFH Stadium"),
        "mode": auto_settings.get("mode", "Soccar"),
        "max_teams": auto_settings.get("max_teams", 8),
        "status": "registration",
        "teams": [],
        "matches": [],
        "created_at": datetime.datetime.now().isoformat(),
        "created_by": "auto_system",
        "prize_pool": random.randint(100, 500),
        "current_round": 0,
        "registration_deadline": (datetime.datetime.now() + datetime.timedelta(hours=2)).isoformat(),
        "auto_start_time": (datetime.datetime.now() + datetime.timedelta(hours=2)).isoformat(),
        "auto_created": True
    }
    
    tournaments = load_tournaments()
    tournaments.append(tournament_data)
    save_tournaments(tournaments)
    
    # Create announcement embed
    embed = discord.Embed(
        title="🔥 AUTO TOURNAMENT ALERT!",
        description=f"**A new tournament has been automatically created!**\n\n🏆 **Tournament ID:** `{tournament_id}`",
        color=0xFF6B00
    )
    
    embed.add_field(name="⚙️ Format", value=tournament_data["format"], inline=True)
    embed.add_field(name="🗺️ Map", value=tournament_data["map"], inline=True)
    embed.add_field(name="🎮 Mode", value=tournament_data["mode"], inline=True)
    embed.add_field(name="👥 Max Teams", value=str(tournament_data["max_teams"]), inline=True)
    embed.add_field(name="💰 Prize Pool", value=f"{tournament_data['prize_pool']} credits", inline=True)
    embed.add_field(name="⏰ Registration Ends", value=f"<t:{int(datetime.datetime.fromisoformat(tournament_data['registration_deadline']).timestamp())}:R>", inline=True)
    
    embed.add_field(
        name="📝 How to Join",
        value=f"Use this command to register:\n```/tournament_register {tournament_id} [team_name] [players]```",
        inline=False
    )
    
    embed.add_field(
        name="🎯 Quick Register",
        value="Click the button below to start registration!",
        inline=False
    )
    
    embed.set_footer(text="Auto-generated tournament • Registration closes in 2 hours")
    embed.set_thumbnail(url="https://images-ext-1.discordapp.net/external/q0ZMEHDP5sKCDBIXcrIGHZzYGV8LO9nrZjwOQnJ8xKE/https/cdn.cloudflare.steamstatic.com/steam/apps/252950/header.jpg")
    
    # Create registration button
    view = AutoTournamentRegistrationView(tournament_id)
    
    await channel.send(embed=embed, view=view)
    
    return tournament_id

class AutoTournamentRegistrationView(discord.ui.View):
    def __init__(self, tournament_id):
        super().__init__(timeout=7200)  # 2 hours
        self.tournament_id = tournament_id
    
    @discord.ui.button(label="📝 Quick Register", style=discord.ButtonStyle.success, emoji="🏆")
    async def quick_register(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = QuickTournamentRegistrationModal(self.tournament_id)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="📊 Tournament Info", style=discord.ButtonStyle.primary, emoji="ℹ️")
    async def tournament_info(self, interaction: discord.Interaction, button: discord.ui.Button):
        tournaments = load_tournaments()
        tournament = next((t for t in tournaments if t["id"] == self.tournament_id), None)
        
        if not tournament:
            await interaction.response.send_message("❌ Tournament not found!", ephemeral=True)
            return
        
        embed = discord.Embed(title=f"🏆 Tournament: {self.tournament_id}", color=0xFFD700)
        embed.add_field(name="Status", value=tournament["status"].title(), inline=True)
        embed.add_field(name="Teams Registered", value=f"{len(tournament['teams'])}/{tournament['max_teams']}", inline=True)
        embed.add_field(name="Format", value=tournament["format"], inline=True)
        embed.add_field(name="Map", value=tournament["map"], inline=True)
        embed.add_field(name="Mode", value=tournament["mode"], inline=True)
        embed.add_field(name="Prize Pool", value=f"{tournament['prize_pool']} credits", inline=True)
        
        if tournament["teams"]:
            teams_list = "\n".join([f"• {team['name']}" for team in tournament["teams"][-5:]])
            embed.add_field(name="Recent Teams", value=teams_list, inline=False)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class QuickTournamentRegistrationModal(discord.ui.Modal, title="Quick Tournament Registration"):
    def __init__(self, tournament_id):
        super().__init__()
        self.tournament_id = tournament_id
    
    team_name = discord.ui.TextInput(
        label="Team Name",
        placeholder="Enter your team name...",
        max_length=50
    )
    
    players = discord.ui.TextInput(
        label="Players",
        placeholder="Enter player names separated by commas...",
        style=discord.TextStyle.paragraph,
        max_length=200
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        tournaments = load_tournaments()
        tournament = next((t for t in tournaments if t["id"] == self.tournament_id), None)
        
        if not tournament:
            await interaction.response.send_message("❌ Tournament not found!", ephemeral=True)
            return
        
        if tournament["status"] != "registration":
            await interaction.response.send_message("❌ Tournament registration is closed!", ephemeral=True)
            return
        
        if len(tournament["teams"]) >= tournament["max_teams"]:
            await interaction.response.send_message("❌ Tournament is full!", ephemeral=True)
            return
        
        player_list = [p.strip() for p in self.players.value.split(",")]
        team_data = {
            "name": self.team_name.value,
            "players": player_list,
            "captain": interaction.user.id,
            "registered_at": datetime.datetime.now().isoformat()
        }
        
        tournament["teams"].append(team_data)
        
        # Update tournaments
        for i, t in enumerate(tournaments):
            if t["id"] == self.tournament_id:
                tournaments[i] = tournament
                break
        
        save_tournaments(tournaments)
        
        embed = discord.Embed(title="✅ Tournament Registration Successful!", color=0x00ff00)
        embed.add_field(name="Tournament", value=self.tournament_id, inline=False)
        embed.add_field(name="Team", value=self.team_name.value, inline=True)
        embed.add_field(name="Players", value=", ".join(player_list), inline=True)
        embed.add_field(name="Teams Registered", value=f"{len(tournament['teams'])}/{tournament['max_teams']}", inline=False)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

def generate_tournament_matches(teams, format_type, map_choice, game_mode):
    matches = []
    random.shuffle(teams)
    
    for i in range(0, len(teams), 2):
        if i + 1 < len(teams):
            match_id = f"tournament_{random.randint(10000, 99999)}"
            match = {
                "id": match_id,
                "team1_name": teams[i]["name"],
                "team2_name": teams[i + 1]["name"],
                "team1_players": teams[i]["players"],
                "team2_players": teams[i + 1]["players"],
                "format": format_type,
                "map": map_choice,
                "mode": game_mode,
                "status": "scheduled",
                "match_name": f"Tournament{random.randint(1000,9999)}",
                "password": f"TOUR{random.randint(100,999)}",
                "created_at": datetime.datetime.now().isoformat(),
                "type": "tournament"
            }
            matches.append(match)
    
    return matches

class TeamRegistrationModal(discord.ui.Modal, title="Register Your Team"):
    def __init__(self):
        super().__init__()

    team_name = discord.ui.TextInput(label="Team Name", placeholder="Enter your team name...", max_length=50)
    players = discord.ui.TextInput(
        label="Players", 
        placeholder="Enter player names separated by commas...", 
        style=discord.TextStyle.paragraph,
        max_length=200
    )

    async def on_submit(self, interaction: discord.Interaction):
        teams = load_teams()
        player_list = [p.strip() for p in self.players.value.split(",")]
        teams.append({"name": self.team_name.value, "players": player_list})
        save_teams(teams)
        
        embed = discord.Embed(title="✅ Team Registered!", color=0x00ff00)
        embed.add_field(name="Team Name", value=self.team_name.value, inline=False)
        embed.add_field(name="Players", value=", ".join(player_list), inline=False)
        embed.set_footer(text="Good luck in the tournament! 🏆")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class AdvancedTournamentView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.format = None
        self.map_choice = None
        self.game_mode = None
        self.tournament_type = None
        self.max_teams = None

    @discord.ui.select(placeholder="Choose tournament type...", options=[
        discord.SelectOption(label="Single Elimination", description="Winner takes all", emoji="🏆"),
        discord.SelectOption(label="Double Elimination", description="Second chance bracket", emoji="🔄"),
        discord.SelectOption(label="Round Robin", description="Everyone plays everyone", emoji="🔁"),
        discord.SelectOption(label="Swiss System", description="Balanced matchmaking", emoji="⚖️")
    ])
    async def tournament_type_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.tournament_type = select.values[0]
        await interaction.response.edit_message(content=f"✅ Type: **{self.tournament_type}**\nChoose format:", view=self)

    @discord.ui.select(placeholder="Choose format...", options=[
        discord.SelectOption(label="1v1", description="1 vs 1 tournament", emoji="⚡"),
        discord.SelectOption(label="2v2", description="2 vs 2 tournament", emoji="🤝"),
        discord.SelectOption(label="3v3", description="3 vs 3 tournament", emoji="👥")
    ])
    async def format_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.format = select.values[0]
        await interaction.response.edit_message(content=f"✅ Type: **{self.tournament_type}**\n✅ Format: **{self.format}**\nChoose map:", view=self)

    @discord.ui.select(placeholder="Choose map...", options=[
        discord.SelectOption(label="DFH Stadium", emoji="🏟️"),
        discord.SelectOption(label="Mannfield", emoji="🌿"),
        discord.SelectOption(label="Champions Field", emoji="🏆"),
        discord.SelectOption(label="Neo Tokyo", emoji="🌸"),
        discord.SelectOption(label="Random Maps", emoji="🎲")
    ])
    async def map_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.map_choice = select.values[0]
        await interaction.response.edit_message(content=f"✅ Type: **{self.tournament_type}**\n✅ Format: **{self.format}**\n✅ Map: **{self.map_choice}**\nChoose game mode:", view=self)

    @discord.ui.select(placeholder="Choose game mode...", options=[
        discord.SelectOption(label="Soccar", description="Classic Rocket League", emoji="⚽"),
        discord.SelectOption(label="Hoops", description="Basketball mode", emoji="🏀"),
        discord.SelectOption(label="Snow Day", description="Hockey with a puck", emoji="🏒"),
        discord.SelectOption(label="Rumble", description="Power-ups enabled", emoji="💥")
    ])
    async def mode_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.game_mode = select.values[0]
        await interaction.response.edit_message(content=f"✅ Type: **{self.tournament_type}**\n✅ Format: **{self.format}**\n✅ Map: **{self.map_choice}**\n✅ Mode: **{self.game_mode}**\nChoose max teams:", view=self)

    @discord.ui.select(placeholder="Max teams...", options=[
        discord.SelectOption(label="8 Teams", value="8", emoji="8️⃣"),
        discord.SelectOption(label="16 Teams", value="16", emoji="🔢"),
        discord.SelectOption(label="32 Teams", value="32", emoji="🏟️"),
        discord.SelectOption(label="Unlimited", value="999", emoji="♾️")
    ])
    async def max_teams_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.max_teams = int(select.values[0])
        await interaction.response.edit_message(content=f"✅ All settings configured!\n**Type:** {self.tournament_type}\n**Format:** {self.format}\n**Map:** {self.map_choice}\n**Mode:** {self.game_mode}\n**Max Teams:** {self.max_teams}", view=self)

    @discord.ui.button(label="Create Tournament", style=discord.ButtonStyle.green, emoji="🚀")
    async def create_tournament(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not all([self.tournament_type, self.format, self.map_choice, self.game_mode, self.max_teams]):
            await interaction.response.send_message("❌ Please configure all settings first!", ephemeral=True)
            return

        tournament_id = f"tournament_{random.randint(10000, 99999)}"
        tournament_data = {
            "id": tournament_id,
            "type": self.tournament_type,
            "format": self.format,
            "map": self.map_choice,
            "mode": self.game_mode,
            "max_teams": self.max_teams,
            "status": "registration",
            "teams": [],
            "matches": [],
            "created_at": datetime.datetime.now().isoformat(),
            "created_by": interaction.user.id,
            "prize_pool": 0,
            "current_round": 0,
            "registration_deadline": (datetime.datetime.now() + datetime.timedelta(hours=24)).isoformat()
        }
        
        tournaments = load_tournaments()
        tournaments.append(tournament_data)
        save_tournaments(tournaments)
        
        embed = discord.Embed(title="🏆 Tournament Created!", color=0xFFD700)
        embed.add_field(name="Tournament ID", value=tournament_id, inline=False)
        embed.add_field(name="Type", value=self.tournament_type, inline=True)
        embed.add_field(name="Format", value=self.format, inline=True)
        embed.add_field(name="Map", value=self.map_choice, inline=True)
        embed.add_field(name="Mode", value=self.game_mode, inline=True)
        embed.add_field(name="Max Teams", value=self.max_teams, inline=True)
        embed.add_field(name="Status", value="🟢 Registration Open", inline=True)
        embed.add_field(name="Registration", value="Use `/tournament_register` to join!", inline=False)
        embed.set_footer(text=f"Tournament ID: {tournament_id}")
        
        await interaction.response.edit_message(content="", embed=embed, view=None)

class MVPVotingView(discord.ui.View):
    def __init__(self, match_id, players):
        super().__init__(timeout=300)  # 5 minute timeout
        self.match_id = match_id
        self.players = players
        self.votes = {}
        
        # Add buttons for each player
        for player in players[:5]:  # Discord limit of 5 buttons per row
            button = discord.ui.Button(label=player, style=discord.ButtonStyle.secondary)
            button.callback = self.create_vote_callback(player)
            self.add_item(button)
    
    def create_vote_callback(self, player):
        async def vote_callback(interaction):
            user_id = interaction.user.id
            
            # Check if user already voted
            if user_id in self.votes:
                await interaction.response.send_message(f"❌ You already voted for {self.votes[user_id]}!", ephemeral=True)
                return
            
            self.votes[user_id] = player
            
            # Save vote
            mvp_votes = load_mvp_votes()
            if self.match_id not in mvp_votes:
                mvp_votes[self.match_id] = {}
            mvp_votes[self.match_id][str(user_id)] = player
            save_mvp_votes(mvp_votes)
            
            await interaction.response.send_message(f"✅ You voted for **{player}** as MVP!", ephemeral=True)
            
            # Update embed with vote count
            embed = discord.Embed(title="🏆 MVP Voting", description=f"Vote for the MVP of match {self.match_id}!", color=0xFFD700)
            
            # Count votes
            vote_counts = {}
            for voted_player in self.votes.values():
                vote_counts[voted_player] = vote_counts.get(voted_player, 0) + 1
            
            if vote_counts:
                vote_text = "\n".join([f"**{player}**: {count} votes" for player, count in sorted(vote_counts.items(), key=lambda x: x[1], reverse=True)])
                embed.add_field(name="Current Votes", value=vote_text, inline=False)
            
            await interaction.edit_original_response(embed=embed, view=self)
        
        return vote_callback

class QueueView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Join 1v1 Queue", style=discord.ButtonStyle.primary, emoji="⚡")
    async def queue_1v1(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.join_queue(interaction, "1v1")

    @discord.ui.button(label="Join 2v2 Queue", style=discord.ButtonStyle.primary, emoji="🤝")
    async def queue_2v2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.join_queue(interaction, "2v2")

    @discord.ui.button(label="Join 3v3 Queue", style=discord.ButtonStyle.primary, emoji="👥")
    async def queue_3v3(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.join_queue(interaction, "3v3")

    @discord.ui.button(label="Leave Queue", style=discord.ButtonStyle.danger, emoji="❌")
    async def leave_queue(self, interaction: discord.Interaction, button: discord.ui.Button):
        queue = load_queue()
        queue = [p for p in queue if p["user_id"] != interaction.user.id]
        save_queue(queue)
        
        embed = discord.Embed(title="❌ Left Queue", description="You have been removed from all queues.", color=0xff0000)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def join_queue(self, interaction, format_type):
        queue = load_queue()
        
        # Remove user from any existing queue
        queue = [p for p in queue if p["user_id"] != interaction.user.id]
        
        # Add to new queue
        queue.append({
            "user_id": interaction.user.id,
            "username": interaction.user.display_name,
            "format": format_type,
            "status": "searching",
            "joined_at": datetime.datetime.now().isoformat()
        })
        
        save_queue(queue)
        
        # Count players in this format
        format_count = len([p for p in queue if p["format"] == format_type])
        
        embed = discord.Embed(title=f"🔍 Searching for {format_type} Match", color=0x00ffcc)
        embed.add_field(name="Queue Status", value=f"**{format_count}** players in {format_type} queue", inline=False)
        embed.add_field(name="Estimated Wait", value=self.get_estimated_wait(format_type, format_count), inline=False)
        embed.set_footer(text="You'll be notified when a match is found!")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    def get_estimated_wait(self, format_type, count):
        if format_type == "1v1":
            return "< 1 minute" if count >= 2 else f"Waiting for {2-count} more players"
        elif format_type == "2v2":
            return "< 1 minute" if count >= 4 else f"Waiting for {4-count} more players"
        elif format_type == "3v3":
            return "< 1 minute" if count >= 6 else f"Waiting for {6-count} more players"

class AdminControlView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Toggle Queue", style=discord.ButtonStyle.primary, emoji="🎮")
    async def toggle_queue(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Admin only!", ephemeral=True)
            return
        
        settings = load_admin_settings()
        settings["allow_queue"] = not settings["allow_queue"]
        save_admin_settings(settings)
        
        status = "enabled" if settings["allow_queue"] else "disabled"
        await interaction.response.send_message(f"✅ Queue {status}!", ephemeral=True)
    
    @discord.ui.button(label="Toggle Tournaments", style=discord.ButtonStyle.primary, emoji="🏆")
    async def toggle_tournaments(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Admin only!", ephemeral=True)
            return
        
        settings = load_admin_settings()
        settings["allow_tournaments"] = not settings["allow_tournaments"]
        save_admin_settings(settings)
        
        status = "enabled" if settings["allow_tournaments"] else "disabled"
        await interaction.response.send_message(f"✅ Tournaments {status}!", ephemeral=True)
    
    @discord.ui.button(label="Wipe Stats", style=discord.ButtonStyle.danger, emoji="🗑️")
    async def wipe_stats(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Admin only!", ephemeral=True)
            return
        
        view = discord.ui.View()
        confirm_btn = discord.ui.Button(label="CONFIRM WIPE", style=discord.ButtonStyle.danger)
        cancel_btn = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.secondary)
        
        async def confirm_wipe(confirm_interaction):
            save_stats({})
            save_match_history([])
            save_mvp_votes({})
            await confirm_interaction.response.send_message("✅ All stats wiped!", ephemeral=True)
        
        async def cancel_wipe(cancel_interaction):
            await cancel_interaction.response.send_message("❌ Wipe cancelled.", ephemeral=True)
        
        confirm_btn.callback = confirm_wipe
        cancel_btn.callback = cancel_wipe
        view.add_item(confirm_btn)
        view.add_item(cancel_btn)
        
        await interaction.response.send_message("⚠️ **WARNING**: This will permanently delete all player stats, match history, and MVP votes. Are you sure?", view=view, ephemeral=True)
    
    @discord.ui.button(label="View Settings", style=discord.ButtonStyle.secondary, emoji="⚙️")
    async def view_settings(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Admin only!", ephemeral=True)
            return
        
        settings = load_admin_settings()
        
        embed = discord.Embed(title="⚙️ Admin Settings", color=0x00ffcc)
        embed.add_field(name="Queue Enabled", value="✅" if settings["allow_queue"] else "❌", inline=True)
        embed.add_field(name="Tournaments Enabled", value="✅" if settings["allow_tournaments"] else "❌", inline=True)
        embed.add_field(name="Max Tournament Teams", value=settings["max_tournament_teams"], inline=True)
        embed.add_field(name="Auto MMR Updates", value="✅" if settings["auto_mmr_updates"] else "❌", inline=True)
        embed.add_field(name="MVP Voting", value="✅" if settings["mvp_voting_enabled"] else "❌", inline=True)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="advanced_tournament", description="Create an advanced tournament with multiple options")
async def advanced_tournament(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Only admins can create tournaments.", ephemeral=True)
        return

    view = AdvancedTournamentView()
    embed = discord.Embed(title="🏆 Advanced Tournament Creator", description="Configure your tournament settings below:", color=0xFFD700)
    await interaction.response.send_message(embed=embed, view=view)

@tree.command(name="queue", description="Join the matchmaking queue")
async def queue_command(interaction: discord.Interaction):
    queue = load_queue()
    current_queues = {}
    
    for format_type in ["1v1", "2v2", "3v3"]:
        current_queues[format_type] = len([p for p in queue if p["format"] == format_type])
    
    embed = discord.Embed(title="🎮 Matchmaking Queue", description="Join a queue to find matches automatically!", color=0x00ffcc)
    embed.add_field(name="🔥 Current Queues", value=f"**1v1:** {current_queues['1v1']} players\n**2v2:** {current_queues['2v2']} players\n**3v3:** {current_queues['3v3']} players", inline=False)
    embed.add_field(name="ℹ️ How it works", value="• Choose a format to queue for\n• Bot automatically matches you with players\n• Get notified when match is ready\n• Auto-generated match credentials", inline=False)
    
    view = QueueView()
    await interaction.response.send_message(embed=embed, view=view)

@tree.command(name="tournament_register", description="Register for a tournament")
@app_commands.describe(tournament_id="Tournament ID to join", team_name="Your team name", players="Comma-separated player names")
async def tournament_register(interaction: discord.Interaction, tournament_id: str, team_name: str, players: str):
    tournaments = load_tournaments()
    tournament = next((t for t in tournaments if t["id"] == tournament_id), None)
    
    if not tournament:
        await interaction.response.send_message("❌ Tournament not found!", ephemeral=True)
        return
    
    if tournament["status"] != "registration":
        await interaction.response.send_message("❌ Tournament registration is closed!", ephemeral=True)
        return
    
    if len(tournament["teams"]) >= tournament["max_teams"]:
        await interaction.response.send_message("❌ Tournament is full!", ephemeral=True)
        return
    
    player_list = [p.strip() for p in players.split(",")]
    team_data = {
        "name": team_name,
        "players": player_list,
        "captain": interaction.user.id,
        "registered_at": datetime.datetime.now().isoformat()
    }
    
    tournament["teams"].append(team_data)
    
    # Update tournaments
    for i, t in enumerate(tournaments):
        if t["id"] == tournament_id:
            tournaments[i] = tournament
            break
    
    save_tournaments(tournaments)
    
    embed = discord.Embed(title="✅ Tournament Registration Successful!", color=0x00ff00)
    embed.add_field(name="Tournament", value=tournament_id, inline=False)
    embed.add_field(name="Team", value=team_name, inline=True)
    embed.add_field(name="Players", value=", ".join(player_list), inline=True)
    embed.add_field(name="Teams Registered", value=f"{len(tournament['teams'])}/{tournament['max_teams']}", inline=False)
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="leaderboard", description="View the server leaderboard")
async def leaderboard(interaction: discord.Interaction):
    stats = load_stats()
    
    if not stats:
        await interaction.response.send_message("❌ No player stats found!", ephemeral=True)
        return
    
    # Sort by MMR
    sorted_players = sorted(stats.items(), key=lambda x: x[1]["mmr"], reverse=True)
    
    embed = discord.Embed(title="🏆 Server Leaderboard", color=0xFFD700)
    
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
    
    await interaction.response.send_message(embed=embed)

@tree.command(name="mystats", description="View your player statistics")
async def mystats(interaction: discord.Interaction):
    stats = load_stats()
    player_id = str(interaction.user.id)
    
    if player_id not in stats:
        # Initialize new player
        update_player_stats(player_id)
        stats = load_stats()
    
    player_stats = stats[player_id]
    
    embed = discord.Embed(title=f"📊 {interaction.user.display_name}'s Stats", color=0x00ffcc)
    embed.add_field(name="🏆 Rank", value=f"**{player_stats['rank']}**", inline=True)
    embed.add_field(name="📈 MMR", value=f"**{player_stats['mmr']}**", inline=True)
    embed.add_field(name="🎮 Matches", value=f"**{player_stats['matches_played']}**", inline=True)
    embed.add_field(name="✅ Wins", value=f"**{player_stats['wins']}**", inline=True)
    embed.add_field(name="❌ Losses", value=f"**{player_stats['losses']}**", inline=True)
    embed.add_field(name="📊 W/L Ratio", value=f"**{player_stats['wins']/(player_stats['losses'] or 1):.2f}**", inline=True)
    embed.add_field(name="⚽ Goals", value=f"**{player_stats['goals']}**", inline=True)
    embed.add_field(name="🛡️ Saves", value=f"**{player_stats['saves']}**", inline=True)
    embed.add_field(name="🤝 Assists", value=f"**{player_stats['assists']}**", inline=True)
    
    await interaction.response.send_message(embed=embed)

@tree.command(name="list_matches", description="List all matches")
async def list_matches(interaction: discord.Interaction):
    matches = load_matches()
    if not matches:
        await interaction.response.send_message("❌ No matches found!", ephemeral=True)
        return
    
    embed = discord.Embed(title="📋 All Matches", color=0x00ffcc)
    
    for match in matches[-10:]:  # Show last 10 matches
        status_emoji = "⏳" if match["status"] == "scheduled" else "✅" if match["status"] == "completed" else "🎮"
        
        if "team1_name" in match and "team2_name" in match:
            team_info = f"{match['team1_name']} vs {match['team2_name']}"
        elif "orange_players" in match and "blue_players" in match:
            team_info = f"Orange: {', '.join(match['orange_players'])} vs Blue: {', '.join(match['blue_players'])}"
        else:
            team_info = "Unknown teams"
        
        embed.add_field(
            name=f"{status_emoji} {match['id']}", 
            value=f"**{team_info}**\n**Credentials:** `{match['match_name']}` / `{match['password']}`\n**Status:** {match['status'].title()}", 
            inline=False
        )
    
    await interaction.response.send_message(embed=embed)

@tree.command(name="report_match", description="Report match results with detailed stats")
@app_commands.describe(match_id="Match ID", orange_score="Orange team score", blue_score="Blue team score", orange_goals="Orange team individual goals (comma-separated)", blue_goals="Blue team individual goals (comma-separated)")
async def report_match(interaction: discord.Interaction, match_id: str, orange_score: int, blue_score: int, orange_goals: str = None, blue_goals: str = None):
    matches = load_matches()
    match = next((m for m in matches if m["id"] == match_id), None)
    
    if not match:
        await interaction.response.send_message("❌ Match not found!", ephemeral=True)
        return
    
    # Parse individual goals
    orange_individual_goals = []
    blue_individual_goals = []
    
    if orange_goals:
        orange_individual_goals = [int(g.strip()) for g in orange_goals.split(",") if g.strip().isdigit()]
    if blue_goals:
        blue_individual_goals = [int(g.strip()) for g in blue_goals.split(",") if g.strip().isdigit()]
    
    # Update match with results
    match["status"] = "completed"
    match["orange_score"] = orange_score
    match["blue_score"] = blue_score
    match["completed_at"] = datetime.datetime.now().isoformat()
    match["reported_by"] = interaction.user.id
    match["orange_individual_goals"] = orange_individual_goals
    match["blue_individual_goals"] = blue_individual_goals
    
    # Update player stats with detailed tracking
    if "orange_players" in match and "blue_players" in match:
        orange_won = orange_score > blue_score
        blue_won = blue_score > orange_score
        
        for i, player in enumerate(match["orange_players"]):
            goals = orange_individual_goals[i] if i < len(orange_individual_goals) else 0
            update_player_stats(f"player_{player}", win=orange_won, goals=goals, saves=random.randint(0, 2), assists=random.randint(0, 2), match_id=match_id)
        
        for i, player in enumerate(match["blue_players"]):
            goals = blue_individual_goals[i] if i < len(blue_individual_goals) else 0
            update_player_stats(f"player_{player}", win=blue_won, goals=goals, saves=random.randint(0, 2), assists=random.randint(0, 2), match_id=match_id)
    
    # Save to match history
    history = load_match_history()
    history.append({
        "match_id": match_id,
        "date": datetime.datetime.now().isoformat(),
        "orange_score": orange_score,
        "blue_score": blue_score,
        "orange_players": match.get("orange_players", []),
        "blue_players": match.get("blue_players", []),
        "orange_goals": orange_individual_goals,
        "blue_goals": blue_individual_goals,
        "format": match.get("format", "Unknown"),
        "map": match.get("map", "Unknown")
    })
    save_match_history(history)
    
    # Save updated matches
    for i, m in enumerate(matches):
        if m["id"] == match_id:
            matches[i] = match
            break
    save_matches(matches)
    
    winner = "Orange" if orange_score > blue_score else "Blue" if blue_score > orange_score else "Tie"
    
    embed = discord.Embed(title="📊 Match Results", color=0x00ff00)
    embed.add_field(name="🏆 Final Score", value=f"🟠 **{orange_score}** - **{blue_score}** 🔵", inline=False)
    embed.add_field(name="🥇 Winner", value=f"**{winner} Team!**" if winner != "Tie" else "**It's a Tie!**", inline=False)
    
    # Show individual goals if provided
    if orange_individual_goals:
        embed.add_field(name="🟠 Orange Goals", value=f"{', '.join(map(str, orange_individual_goals))}", inline=True)
    if blue_individual_goals:
        embed.add_field(name="🔵 Blue Goals", value=f"{', '.join(map(str, blue_individual_goals))}", inline=True)
    
    embed.add_field(name="📋 Match Details", value=f"**ID:** {match_id}\n**Format:** {match.get('format', 'Unknown')}\n**Map:** {match.get('map', 'Unknown')}", inline=False)
    embed.set_footer(text=f"Reported by {interaction.user.display_name}")
    
    # Check achievements for all players
    new_achievements = []
    if "orange_players" in match and "blue_players" in match:
        from achievements import check_achievements, create_achievement_embed
        from customization import unlock_banner, unlock_badge
        
        all_players = match["orange_players"] + match["blue_players"]
        for i, player in enumerate(all_players):
            player_id = f"player_{player}"
            
            # Create match data for achievement checking
            match_data = {
                "won": (player in match["orange_players"] and orange_score > blue_score) or 
                       (player in match["blue_players"] and blue_score > orange_score),
                "goals": orange_individual_goals[i] if i < len(orange_individual_goals) and player in match["orange_players"] else 
                        blue_individual_goals[i-len(match["orange_players"])] if i >= len(match["orange_players"]) and i-len(match["orange_players"]) < len(blue_individual_goals) else 0,
                "saves": random.randint(0, 3),
                "assists": random.randint(0, 2),
                "first_goal_scorer": player_id if (orange_individual_goals and orange_individual_goals[0] > 0 and i == 0) or (blue_individual_goals and blue_individual_goals[0] > 0 and i == len(match["orange_players"])) else None,
                "overtime_win": abs(orange_score - blue_score) == 1 and max(orange_score, blue_score) > 3,
                "goals_conceded": blue_score if player in match["orange_players"] else orange_score,
                "max_deficit": random.randint(0, 2) if match_data.get("won") else 0,
                "aerial_goals": random.randint(0, 1) if match_data.get("goals", 0) > 0 else 0
            }
            
            achievements = check_achievements(player_id, match_data)
            for achievement in achievements:
                new_achievements.append((player, achievement))
                
                # Unlock corresponding banner/badge
                if achievement == "hat_trick_hero":
                    unlock_banner(f"player_{player}", "fire")
                elif achievement == "clutch_king":
                    unlock_banner(f"player_{player}", "champion")
                elif achievement == "mvp_streak":
                    unlock_banner(f"player_{player}", "mvp")
                
                unlock_badge(f"player_{player}", achievement)
    
    # Start MVP voting if enabled
    settings = load_admin_settings()
    if settings.get("mvp_voting_enabled", True):
        all_players = match.get("orange_players", []) + match.get("blue_players", [])
        if all_players:
            mvp_view = MVPVotingView(match_id, all_players)
            mvp_embed = discord.Embed(title="🏆 MVP Voting", description=f"Vote for the MVP of match {match_id}!", color=0xFFD700)
            mvp_embed.add_field(name="Players", value=", ".join(all_players), inline=False)
            
            await interaction.response.send_message(embed=embed)
            await interaction.followup.send(embed=mvp_embed, view=mvp_view)
        else:
            await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message(embed=embed)
    
    # Send achievement notifications
    for player, achievement in new_achievements:
        try:
            from achievements import create_achievement_embed
            achievement_embed = create_achievement_embed(achievement, player)
            await interaction.followup.send(embed=achievement_embed)
        except:
            pass

@tree.command(name="tournament_status", description="Check tournament status")
@app_commands.describe(tournament_id="Tournament ID to check")
async def tournament_status(interaction: discord.Interaction, tournament_id: str):
    tournaments = load_tournaments()
    tournament = next((t for t in tournaments if t["id"] == tournament_id), None)
    
    if not tournament:
        await interaction.response.send_message("❌ Tournament not found!", ephemeral=True)
        return
    
    embed = discord.Embed(title=f"🏆 Tournament: {tournament_id}", color=0xFFD700)
    embed.add_field(name="Status", value=f"**{tournament['status'].title()}**", inline=True)
    embed.add_field(name="Type", value=tournament['type'], inline=True)
    embed.add_field(name="Format", value=tournament['format'], inline=True)
    embed.add_field(name="Teams", value=f"{len(tournament['teams'])}/{tournament['max_teams']}", inline=True)
    embed.add_field(name="Current Round", value=tournament.get('current_round', 0), inline=True)
    embed.add_field(name="Matches", value=len(tournament.get('matches', [])), inline=True)
    
    if tournament['teams']:
        teams_list = "\n".join([f"• {team['name']}" for team in tournament['teams'][-5:]])
        embed.add_field(name="Recent Teams", value=teams_list, inline=False)
    
    await interaction.response.send_message(embed=embed)

@tree.command(name="admin_panel", description="Admin control panel")
async def admin_panel(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Only admins can access this panel.", ephemeral=True)
        return
    
    embed = discord.Embed(title="🛠️ Admin Control Panel", description="Manage your OctaneCore bot settings", color=0xff6600)
    view = AdminControlView()
    await interaction.response.send_message(embed=embed, view=view)

@tree.command(name="match_history", description="View detailed match history including pending and cancelled matches")
@app_commands.describe(player="Player name to filter by (optional)", status="Filter by match status (optional)")
async def match_history(interaction: discord.Interaction, player: str = None, status: str = None):
    history = load_match_history()
    
    if not history:
        await interaction.response.send_message("❌ No match history found!", ephemeral=True)
        return
    
    # Filter by player if specified
    if player:
        history = [h for h in history if player in h.get("orange_players", []) + h.get("blue_players", [])]
    
    # Filter by status if specified
    if status:
        history = [h for h in history if h.get("status", "").lower() == status.lower()]
    
    # Group by status
    status_groups = {
        "completed": [],
        "created": [],
        "cancelled": [],
        "in_progress": []
    }
    
    for match in history:
        match_status = match.get("status", "unknown")
        if match_status in status_groups:
            status_groups[match_status].append(match)
        else:
            status_groups["created"].append(match)  # Default
    
    embed = discord.Embed(title="📜 Match History & Status", color=0x00ffcc)
    
    # Show each status group
    for status_type, matches in status_groups.items():
        if not matches:
            continue
            
        status_emoji = {
            "completed": "✅",
            "created": "🎮", 
            "cancelled": "❌",
            "in_progress": "🔄"
        }
        
        # Show last 5 matches of each type
        match_text = ""
        for match in matches[-5:]:
            date = datetime.datetime.fromisoformat(match["date"]).strftime("%m/%d %H:%M")
            
            if status_type == "completed":
                orange_score = match.get("orange_score", 0)
                blue_score = match.get("blue_score", 0)
                match_text += f"**{match['match_id'][:8]}** - {date}\n🟠 {orange_score} - {blue_score} 🔵 | {match.get('mode', 'Soccar')}\n\n"
            elif status_type == "created":
                players = len(match.get("orange_players", [])) + len(match.get("blue_players", []))
                match_text += f"**{match['match_id'][:8]}** - {date}\n{match.get('format', 'Unknown')} {match.get('mode', 'Soccar')} | {players} players\n\n"
            elif status_type == "cancelled":
                reason = match.get("cancel_reason", "Players didn't join")
                match_text += f"**{match['match_id'][:8]}** - {date}\n{match.get('format', 'Unknown')} | Reason: {reason}\n\n"
            elif status_type == "in_progress":
                elapsed = (datetime.datetime.now() - datetime.datetime.fromisoformat(match["date"])).total_seconds() / 60
                match_text += f"**{match['match_id'][:8]}** - {date}\n{match.get('format', 'Unknown')} | Running {elapsed:.0f}min\n\n"
        
        if match_text:
            embed.add_field(
                name=f"{status_emoji[status_type]} {status_type.title()} Matches ({len(matches)})",
                value=match_text[:1024],  # Discord field limit
                inline=True if len(matches) < 3 else False
            )
    
    # Add summary stats
    total_matches = len(history)
    completed = len(status_groups["completed"])
    success_rate = (completed / total_matches * 100) if total_matches > 0 else 0
    
    embed.add_field(
        name="📊 Summary Statistics",
        value=f"**Total Matches:** {total_matches}\n**Completion Rate:** {success_rate:.1f}%\n**Active:** {len(status_groups['in_progress'])}\n**Recent Activity:** {len([m for m in history if (datetime.datetime.now() - datetime.datetime.fromisoformat(m['date'])).days < 1])} today",
        inline=False
    )
    
    if total_matches > 10:
        embed.set_footer(text=f"Showing recent matches • Use filters to narrow results • Total: {total_matches}")
    
    await interaction.response.send_message(embed=embed)

@tree.command(name="mvp_leaderboard", description="View MVP leaderboard")
async def mvp_leaderboard(interaction: discord.Interaction):
    mvp_votes = load_mvp_votes()
    
    if not mvp_votes:
        await interaction.response.send_message("❌ No MVP votes found!", ephemeral=True)
        return
    
    # Count MVP wins
    mvp_counts = {}
    for match_votes in mvp_votes.values():
        vote_counts = {}
        for vote in match_votes.values():
            vote_counts[vote] = vote_counts.get(vote, 0) + 1
        
        # Find MVP (most votes)
        if vote_counts:
            mvp = max(vote_counts, key=vote_counts.get)
            mvp_counts[mvp] = mvp_counts.get(mvp, 0) + 1
    
    # Sort by MVP count
    sorted_mvps = sorted(mvp_counts.items(), key=lambda x: x[1], reverse=True)
    
    embed = discord.Embed(title="⭐ MVP Leaderboard", color=0xFFD700)
    
    for i, (player, count) in enumerate(sorted_mvps[:10]):
        rank_emoji = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"{i+1}."
        embed.add_field(
            name=f"{rank_emoji} {player}",
            value=f"**{count}** MVP awards",
            inline=True
        )
    
    await interaction.response.send_message(embed=embed)

@tree.command(name="setup_dashboard", description="Set up the interactive dashboard in this channel")
async def setup_dashboard_command(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Only admins can set up the dashboard.", ephemeral=True)
        return
    
    from dashboard import setup_dashboard
    
    await interaction.response.defer()
    
    try:
        message = await setup_dashboard(interaction.channel)
        
        # Track this dashboard message for auto-updates
        bot.dashboard_messages.append({
            'channel_id': interaction.channel.id,
            'message_id': message.id,
            'guild_id': interaction.guild.id
        })
        
        await log_to_channel(f"📊 Dashboard created in #{interaction.channel.name} by {interaction.user.display_name}", "SUCCESS")
        await interaction.followup.send(f"✅ Dashboard created! Members can now use the interactive buttons above. Auto-updates every 30 seconds.", ephemeral=True)
    except Exception as e:
        await log_to_channel(f"❌ Dashboard creation failed: {str(e)}", "ERROR")
        await interaction.followup.send(f"❌ Error creating dashboard: {str(e)}", ephemeral=True)

@tree.command(name="team_builder", description="Set up team builder in this channel")
async def team_builder_command(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Only admins can set up team builder.", ephemeral=True)
        return
    
    await interaction.response.defer()
    
    try:
        from team_builder import setup_team_builder
        message = await setup_team_builder(interaction.channel)
        await interaction.followup.send("✅ Team builder created! Members can now build balanced teams.", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ Error creating team builder: {str(e)}", ephemeral=True)

@tree.command(name="live_match", description="Set up live match reporter")
@app_commands.describe(match_id="Match ID to track live")
async def live_match_command(interaction: discord.Interaction, match_id: str):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Only admins can set up live match tracking.", ephemeral=True)
        return
    
    await interaction.response.defer()
    
    try:
        from live_match import setup_live_match_reporter
        message = await setup_live_match_reporter(interaction.channel, match_id)
        await interaction.followup.send(f"✅ Live match reporter created for {match_id}!", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ Error creating live match reporter: {str(e)}", ephemeral=True)

@tree.command(name="achievements", description="View your achievements")
async def achievements_command(interaction: discord.Interaction):
    from achievements import AchievementView, load_achievements, ACHIEVEMENTS
    
    view = AchievementView(interaction.user.id)
    
    achievements = load_achievements()
    player_achievements = achievements.get(str(interaction.user.id), {"unlocked": []})
    
    unlocked_count = len(player_achievements["unlocked"])
    total_count = len(ACHIEVEMENTS)
    
    embed = discord.Embed(
        title="🏆 Your Achievements",
        description=f"**{unlocked_count}/{total_count}** achievements unlocked",
        color=0xFFD700
    )
    
    # Show recent achievements
    recent = player_achievements["unlocked"][-5:] if player_achievements["unlocked"] else []
    if recent:
        recent_text = "\n".join([f"• {ACHIEVEMENTS[ach]['emoji']} {ACHIEVEMENTS[ach]['name']}" for ach in recent])
        embed.add_field(name="🎯 Recent Unlocks", value=recent_text, inline=False)
    else:
        embed.add_field(name="🎯 Get Started", value="Play matches to unlock achievements!", inline=False)
    
    await interaction.response.send_message(embed=embed, view=view)

@tree.command(name="profile", description="View and customize your player profile")
async def profile_command(interaction: discord.Interaction):
    from customization import get_player_profile, ProfileCustomizationView
    
    profile = get_player_profile(interaction.user.id)
    stats = load_stats()
    player_stats = stats.get(str(interaction.user.id), {})
    
    embed = discord.Embed(
        title=f"🎯 {interaction.user.display_name}'s Profile",
        color=0x9b59b6
    )
    
    # Profile info
    embed.add_field(name="🎨 Banner", value=profile.get("banner", "default").title(), inline=True)
    embed.add_field(name="🏅 Badge", value=profile.get("badge", "None").replace("_", " ").title() if profile.get("badge") else "None", inline=True)
    embed.add_field(name="🚗 Favorite Car", value=profile.get("favorite_car", "Octane"), inline=True)
    
    # Stats
    rank = player_stats.get("rank", "Unranked")
    mmr = player_stats.get("mmr", 0)
    wins = player_stats.get("wins", 0)
    losses = player_stats.get("losses", 0)
    
    embed.add_field(name="🏆 Rank", value=f"{rank} ({mmr} MMR)", inline=True)
    embed.add_field(name="📊 Record", value=f"{wins}W - {losses}L", inline=True)
    embed.add_field(name="⚽ Goals", value=str(player_stats.get("goals", 0)), inline=True)
    
    # Bio
    bio = profile.get("bio", "Ready to rocket!")
    embed.add_field(name="📝 Bio", value=bio, inline=False)
    
    # Customization buttons
    view = ProfileCustomizationView(interaction.user.id)
    
    await interaction.response.send_message(embed=embed, view=view)

@tree.command(name="unlock_banner", description="Unlock a banner for achievements")
@app_commands.describe(user="User to unlock banner for", banner="Banner ID to unlock")
async def unlock_banner_command(interaction: discord.Interaction, user: discord.Member, banner: str):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Only admins can unlock banners.", ephemeral=True)
        return
    
    from customization import unlock_banner
    
    if unlock_banner(user.id, banner):
        await interaction.response.send_message(f"✅ Unlocked banner '{banner}' for {user.display_name}!")
    else:
        await interaction.response.send_message(f"❌ {user.display_name} already has banner '{banner}'.")

@tree.command(name="server_achievements", description="View all server achievements")
async def server_achievements_command(interaction: discord.Interaction):
    from achievements import ACHIEVEMENTS
    
    embed = discord.Embed(title="🏆 All Server Achievements", color=0xFFD700)
    
    for achievement_id, achievement in ACHIEVEMENTS.items():
        rarity_emoji = {"Common": "⚪", "Uncommon": "🟢", "Rare": "🔵", "Epic": "🟣", "Legendary": "🟠", "Mythic": "🔴"}.get(achievement["rarity"], "⚪")
        
        embed.add_field(
            name=f"{achievement['emoji']} {achievement['name']} {rarity_emoji}",
            value=f"{achievement['description']}\n**Rarity:** {achievement['rarity']} • **Reward:** +{achievement['mmr_bonus']} MMR",
            inline=False
        )
    
    await interaction.response.send_message(embed=embed)

@tree.command(name="generate_match_recap", description="Generate AI-powered match recap")
@app_commands.describe(match_id="Match ID to generate recap for")
async def generate_match_recap(interaction: discord.Interaction, match_id: str):
    history = load_match_history()
    match = next((h for h in history if h["match_id"] == match_id), None)
    
    if not match:
        await interaction.response.send_message("❌ Match not found in history!", ephemeral=True)
        return
    
    # Generate fun recap text
    orange_score = match["orange_score"]
    blue_score = match["blue_score"]
    winner = "Orange" if orange_score > blue_score else "Blue" if blue_score > orange_score else None
    
    recap_lines = [
        f"🔥 **Match Recap: {match['match_id']}**",
        f"🏟️ **{match.get('map', 'Unknown')} - {match.get('format', 'Unknown')}**",
        "",
        f"🟠 **Orange Team**: {orange_score} goals",
        f"🔵 **Blue Team**: {blue_score} goals",
        ""
    ]
    
    if winner:
        recap_lines.append(f"🏆 **{winner} Team dominated with a {abs(orange_score - blue_score)} goal lead!**")
    else:
        recap_lines.append("🤝 **What a nail-biter! It's a tie!**")
    
    # Add goal details if available
    if match.get("orange_goals"):
        total_orange = sum(match["orange_goals"])
        recap_lines.append(f"🟠 Orange players scored {total_orange} total goals")
    
    if match.get("blue_goals"):
        total_blue = sum(match["blue_goals"])
        recap_lines.append(f"🔵 Blue players scored {total_blue} total goals")
    
    # Check for MVP
    mvp_votes = load_mvp_votes()
    if match_id in mvp_votes:
        vote_counts = {}
        for vote in mvp_votes[match_id].values():
            vote_counts[vote] = vote_counts.get(vote, 0) + 1
        
        if vote_counts:
            mvp = max(vote_counts, key=vote_counts.get)
            recap_lines.append(f"⭐ **MVP**: {mvp} ({vote_counts[mvp]} votes)")
    
    recap_text = "\n".join(recap_lines)
    
    embed = discord.Embed(title="📰 Match Recap", description=recap_text, color=0x00ffcc)
    embed.set_footer(text=f"Generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    await interaction.response.send_message(embed=embed)

@tree.command(name="admin_dashboard", description="Create admin dashboard in this channel")
async def admin_dashboard_command(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Only administrators can create the admin dashboard.", ephemeral=True)
        return
    
    await interaction.response.defer()
    
    try:
        from admin_dashboard import setup_admin_dashboard
        message = await setup_admin_dashboard(interaction.channel)
        await interaction.followup.send("✅ Admin dashboard created! Use the buttons to manage your bot.", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ Error creating admin dashboard: {str(e)}", ephemeral=True)

@tree.command(name="testing_dashboard", description="Create testing dashboard for bot features")
async def testing_dashboard_command(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Only administrators can create the testing dashboard.", ephemeral=True)
        return
    
    await interaction.response.defer()
    
    try:
        from test_system import setup_testing_dashboard
        message = await setup_testing_dashboard(interaction.channel)
        await interaction.followup.send("✅ Testing dashboard created! Use the buttons to test bot features with simulated users.", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ Error creating testing dashboard: {str(e)}", ephemeral=True)

@tree.command(name="setup_server", description="Comprehensive server setup for OctaneCore bot")
async def setup_server_command(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Only administrators can run server setup.", ephemeral=True)
        return
    
    try:
        from setup import setup_server_command
        await setup_server_command(interaction)
        await log_to_channel(f"🚀 Server setup initiated by {interaction.user.display_name} in {interaction.guild.name}", "INFO")
    except Exception as e:
        await log_to_channel(f"❌ Server setup failed: {str(e)}", "ERROR")
        await interaction.response.send_message(f"❌ Setup failed: {str(e)}", ephemeral=True)

@tree.command(name="economy", description="Access your credits, shop, and daily rewards")
async def economy_command(interaction: discord.Interaction):
    from economy import EconomyView, get_player_economy
    
    player = get_player_economy(interaction.user.id)
    
    embed = discord.Embed(title="💰 Your Economy Dashboard", color=0x00ff00)
    embed.add_field(name="💳 Balance", value=f"**{player['credits']:,}** credits", inline=True)
    embed.add_field(name="🔥 Daily Streak", value=f"**{player['daily_streak']}** days", inline=True)
    embed.add_field(name="📈 Total Earned", value=f"{player['total_earned']:,} credits", inline=True)
    
    view = EconomyView(interaction.user.id)
    await interaction.response.send_message(embed=embed, view=view)

@tree.command(name="daily", description="Claim your daily credit reward")
async def daily_command(interaction: discord.Interaction):
    from economy import claim_daily_reward
    
    reward, streak = claim_daily_reward(interaction.user.id)
    
    if reward is None:
        embed = discord.Embed(title="⏰ Daily Reward", description="You've already claimed your daily reward today!", color=0xff0000)
        embed.add_field(name="⏱️ Next Reward", value="Available in less than 24 hours", inline=False)
    else:
        embed = discord.Embed(title="🎁 Daily Reward Claimed!", color=0x00ff00)
        embed.add_field(name="💰 Reward", value=f"**+{reward}** credits", inline=True)
        embed.add_field(name="🔥 Streak", value=f"**{streak}** days", inline=True)
        embed.add_field(name="💡 Tip", value="Come back tomorrow for an even bigger reward!", inline=False)
    
    await interaction.response.send_message(embed=embed)

@tree.command(name="clan", description="Access clan system - create, join, or manage your clan")
async def clan_command(interaction: discord.Interaction):
    from clans import ClanView
    
    embed = discord.Embed(title="🏰 Clan System", description="Create teams, compete together, and unlock exclusive perks!", color=0x9b59b6)
    embed.add_field(name="🎯 Features", value="• **Create Clans** - Build your team\n• **Clan Wars** - Compete against others\n• **Exclusive Perks** - XP boosts, priority queues\n• **Social Hub** - Connect with teammates", inline=False)
    
    view = ClanView(interaction.user.id)
    await interaction.response.send_message(embed=embed, view=view)

@tree.command(name="help", description="Complete bot help and information")
async def help_command(interaction: discord.Interaction):
    from bot_info import BotInfoView
    
    embed = discord.Embed(
        title="❓ OctaneCore Help Center",
        description="**Welcome to the ultimate Rocket League Discord bot!**\n\nUse the buttons below to explore all features and get help.",
        color=0x00ffcc
    )
    
    embed.add_field(
        name="🚀 Quick Start",
        value="• **New here?** Use `/setup_server` (admin only)\n• **Join queue** with `/queue` or dashboard buttons\n• **Check stats** with `/mystats`\n• **Claim rewards** with `/daily`",
        inline=False
    )
    
    embed.add_field(
        name="🎮 Popular Features",
        value="• **Smart Matchmaking** - Auto queue system\n• **Tournaments** - Create competitive events\n• **Economy** - Credits, shop, daily rewards\n• **Clans** - Team up with friends\n• **Achievements** - Unlock rewards",
        inline=False
    )
    
    view = BotInfoView()
    await interaction.response.send_message(embed=embed, view=view)

@tree.command(name="ping", description="Check bot latency and status")
async def ping_command(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    
    embed = discord.Embed(title="🏓 Pong!", color=0x00ffcc)
    embed.add_field(name="📡 Latency", value=f"**{latency}ms**", inline=True)
    embed.add_field(name="🤖 Status", value="**🟢 Online**", inline=True)
    embed.add_field(name="⏰ Uptime", value=f"**{get_uptime()}**", inline=True)
    
    await interaction.response.send_message(embed=embed)

@tree.command(name="server_info", description="View server information and OctaneCore integration")
async def server_info_command(interaction: discord.Interaction):
    from bot_info import ServerInfoView
    
    embed = discord.Embed(title=f"🏠 {interaction.guild.name}", color=0x9b59b6)
    embed.add_field(name="👥 Members", value=f"**{interaction.guild.member_count:,}**", inline=True)
    embed.add_field(name="📅 Created", value=f"**{interaction.guild.created_at.strftime('%Y-%m-%d')}**", inline=True)
    embed.add_field(name="🤖 Bot Added", value="**Active**", inline=True)
    
    if interaction.guild.icon:
        embed.set_thumbnail(url=interaction.guild.icon.url)
    
    view = ServerInfoView(interaction.guild)
    await interaction.response.send_message(embed=embed, view=view)

@tree.command(name="moderation", description="Server moderation and management tools")
async def moderation_command(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.moderate_members:
        await interaction.response.send_message("❌ You need moderation permissions to use this command!", ephemeral=True)
        return
    
    from moderation import ModerationView
    
    embed = discord.Embed(title="🛡️ Moderation Center", description="Advanced tools for server management and bot moderation", color=0xff6600)
    embed.add_field(name="🔧 Quick Actions", value="• Clear queue abuse\n• Reset tournaments\n• Economy management\n• View mod logs", inline=True)
    embed.add_field(name="⚙️ Configuration", value="• Auto roles\n• Welcome settings\n• Feature toggles\n• Channel setup", inline=True)
    
    view = ModerationView()
    await interaction.response.send_message(embed=embed, view=view)

@tree.command(name="invite", description="Get bot invite link and server information")
async def invite_command(interaction: discord.Interaction):
    embed = discord.Embed(title="🔗 Invite OctaneCore", description="Bring the ultimate Rocket League bot to your server!", color=0x00ffcc)
    
    embed.add_field(
        name="📋 Bot Permissions Needed",
        value="• **Send Messages** - Core functionality\n• **Embed Links** - Rich embeds\n• **Manage Roles** - Auto role assignment\n• **Read Message History** - Context awareness\n• **Use Slash Commands** - Modern interface",
        inline=False
    )
    
    embed.add_field(
        name="🚀 After Adding Bot",
        value="• Run `/setup_server` for complete setup\n• Use `/help` for command reference\n• Create dashboards with `/setup_dashboard`\n• Start with `/queue` to test features",
        inline=False
    )
    
    embed.add_field(
        name="💡 Pro Tips",
        value="• **Administrator permission** recommended for full features\n• **Dedicated channels** improve organization\n• **Regular updates** keep features fresh\n• **Community feedback** drives new features",
        inline=False
    )
    
    embed.set_footer(text="OctaneCore • The future of Rocket League Discord bots")
    
    await interaction.response.send_message(embed=embed)

@tree.command(name="shop", description="Browse and purchase items with credits")
async def shop_command(interaction: discord.Interaction):
    from economy import SHOP_ITEMS, get_player_economy, ShopView
    
    player = get_player_economy(interaction.user.id)
    
    embed = discord.Embed(title="🛍️ OctaneCore Shop", description=f"**Your Balance:** {player['credits']:,} credits", color=0x9b59b6)
    
    # Show featured items
    featured_items = list(SHOP_ITEMS.items())[:6]
    for item_id, item in featured_items:
        embed.add_field(
            name=f"{item['name']}",
            value=f"**{item['price']} credits**\n{item['type'].title()} item",
            inline=True
        )
    
    embed.add_field(name="💡 Tip", value="Purchase items to customize your profile and gain advantages!", inline=False)
    
    view = ShopView(interaction.user.id)
    await interaction.response.send_message(embed=embed, view=view)

@tree.command(name="leaderboards", description="View various server leaderboards")
async def leaderboards_command(interaction: discord.Interaction):
    from economy import load_economy
    
    embed = discord.Embed(title="🏆 Server Leaderboards", color=0xFFD700)
    
    # MMR Leaderboard
    stats = load_stats()
    if stats:
        sorted_mmr = sorted(stats.items(), key=lambda x: x[1]["mmr"], reverse=True)[:5]
        mmr_text = "\n".join([f"{i+1}. <@{player_id}> - {player_stats['mmr']} MMR" for i, (player_id, player_stats) in enumerate(sorted_mmr)])
        embed.add_field(name="📈 MMR Leaders", value=mmr_text or "No data", inline=True)
    
    # Economy Leaderboard
    economy = load_economy()
    if economy:
        sorted_credits = sorted(economy.items(), key=lambda x: x[1]["credits"], reverse=True)[:5]
        credit_text = "\n".join([f"{i+1}. <@{player_id}> - {player_data['credits']:,} credits" for i, (player_id, player_data) in enumerate(sorted_credits)])
        embed.add_field(name="💰 Richest Players", value=credit_text or "No data", inline=True)
    
    # Goals Leaderboard
    if stats:
        sorted_goals = sorted(stats.items(), key=lambda x: x[1]["goals"], reverse=True)[:5]
        goals_text = "\n".join([f"{i+1}. <@{player_id}> - {player_stats['goals']} goals" for i, (player_id, player_stats) in enumerate(sorted_goals)])
        embed.add_field(name="⚽ Top Scorers", value=goals_text or "No data", inline=True)
    
    await interaction.response.send_message(embed=embed)

@bot.event
async def on_disconnect():
    await log_to_channel("⚠️ Bot disconnected from Discord", "WARNING")

@bot.event
async def on_resumed():
    await log_to_channel("🔄 Bot connection resumed", "SUCCESS")

@bot.event
async def on_error(event, *args, **kwargs):
    import traceback
    error_msg = traceback.format_exc()
    await log_to_channel(f"❌ CRITICAL ERROR in {event}", "ERROR")
    await log_to_channel(f"🔧 Args: {args}", "ERROR")
    await log_to_channel(f"📝 Traceback: ```{error_msg[:1500]}```", "ERROR")

@bot.event
async def on_command_error(ctx, error):
    await log_to_channel(f"❌ Command Error: {ctx.command} - {str(error)}", "ERROR")
    await log_to_channel(f"🔧 Error Type: {type(error).__name__}", "ERROR")
    await log_to_channel(f"👤 User: {ctx.author} ({ctx.author.id})", "ERROR")
    await log_to_channel(f"📍 Guild: {ctx.guild.name if ctx.guild else 'DM'}", "ERROR")

@bot.event
async def on_guild_join(guild):
    await log_to_channel(f"🎉 Bot added to new server: {guild.name} ({guild.id})", "SUCCESS")
    await log_to_channel(f"👥 Members: {guild.member_count}", "INFO")
    await log_to_channel(f"👑 Owner: {guild.owner}", "INFO")

@bot.event
async def on_guild_remove(guild):
    await log_to_channel(f"😢 Bot removed from server: {guild.name} ({guild.id})", "WARNING")

@bot.event
async def on_member_join(member):
    if member.guild:
        await log_to_channel(f"👋 New member joined {member.guild.name}: {member} ({member.id})", "INFO")

@bot.event
async def on_member_remove(member):
    if member.guild:
        await log_to_channel(f"👋 Member left {member.guild.name}: {member} ({member.id})", "INFO")

# Enhanced interaction logging
@bot.event
async def on_interaction(interaction):
    if interaction.type == discord.InteractionType.application_command:
        await log_to_channel(f"🎮 Command used: /{interaction.data['name']} by {interaction.user}", "DEBUG")
    elif interaction.type == discord.InteractionType.component:
        await log_to_channel(f"🔘 Button/Select used: {interaction.data.get('custom_id', 'unknown')} by {interaction.user}", "DEBUG")

try:
    bot.run(TOKEN)
except KeyboardInterrupt:
    print("Bot stopped by user")
except Exception as e:
    print(f"Bot crashed: {e}")
finally:
    # Try to log shutdown if possible
    try:
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(log_to_channel("🛑 Bot shutting down", "WARNING"))
        loop.close()
    except:
        pass
