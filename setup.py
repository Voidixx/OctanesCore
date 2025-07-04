
import discord
from discord.ext import commands
import asyncio
from datetime import datetime

class SetupView(discord.ui.View):
    def __init__(self, guild):
        super().__init__(timeout=300)
        self.guild = guild
        self.setup_progress = {}
        self.created_channels = []
        self.created_roles = []

    @discord.ui.button(label="🚀 Full Setup", style=discord.ButtonStyle.success, emoji="🚀")
    async def full_setup(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Only administrators can run setup!", ephemeral=True)
            return

        await interaction.response.defer()
        
        setup_embed = discord.Embed(
            title="🚀 OctaneCore Bot Setup",
            description="Setting up your server for OctaneCore...",
            color=0x00ffcc
        )
        
        message = await interaction.followup.send(embed=setup_embed)
        
        # Setup steps
        steps = [
            ("🎯 Creating Categories", self.create_categories),
            ("📱 Creating Channels", self.create_channels),
            ("🎭 Creating Roles", self.create_roles),
            ("🔧 Setting Permissions", self.setup_permissions),
            ("📊 Creating Dashboards", self.create_dashboards),
            ("✅ Finalizing Setup", self.finalize_setup)
        ]
        
        for i, (step_name, step_func) in enumerate(steps):
            setup_embed.description = f"**Step {i+1}/6:** {step_name}..."
            await message.edit(embed=setup_embed)
            
            try:
                await step_func()
                await asyncio.sleep(1)
            except Exception as e:
                setup_embed.add_field(name=f"❌ {step_name}", value=f"Error: {str(e)}", inline=False)
                await message.edit(embed=setup_embed)
                continue
        
        # Final summary
        setup_embed.title = "✅ Setup Complete!"
        setup_embed.description = "Your server is now ready for OctaneCore!"
        setup_embed.color = 0x00ff00
        
        summary_text = f"**Created:**\n"
        summary_text += f"• {len(self.created_channels)} channels\n"
        summary_text += f"• {len(self.created_roles)} roles\n"
        summary_text += f"• Multiple dashboards\n"
        summary_text += f"• Proper permissions\n\n"
        summary_text += f"**Next Steps:**\n"
        summary_text += f"• Configure your bot token in Secrets\n"
        summary_text += f"• Set LOG_CHANNEL_ID secret\n"
        summary_text += f"• Invite members to try the bot!\n\n"
        summary_text += f"**Quick Start:**\n"
        summary_text += f"• Check <#{self.created_channels[0].id}> for the main dashboard\n"
        summary_text += f"• Use `/queue` to start matchmaking\n"
        summary_text += f"• Use `/advanced_tournament` to create tournaments"
        
        setup_embed.add_field(name="📋 Setup Summary", value=summary_text, inline=False)
        await message.edit(embed=setup_embed)

    async def create_categories(self):
        """Create category channels for organization"""
        categories = [
            ("🎮 OCTANE CORE", "Main bot channels"),
            ("🏆 TOURNAMENTS", "Tournament related channels"),
            ("📊 STATISTICS", "Stats and leaderboards"),
            ("🔧 ADMIN", "Admin only channels")
        ]
        
        self.categories = {}
        for cat_name, cat_desc in categories:
            # Check if category already exists
            existing = discord.utils.get(self.guild.categories, name=cat_name)
            if not existing:
                category = await self.guild.create_category(cat_name)
                self.categories[cat_name] = category
                
                # Lock admin category immediately
                if "ADMIN" in cat_name:
                    await category.set_permissions(
                        self.guild.default_role,
                        read_messages=False,
                        send_messages=False
                    )
                    # Allow administrators
                    for role in self.guild.roles:
                        if role.permissions.administrator:
                            await category.set_permissions(
                                role,
                                read_messages=True,
                                send_messages=True,
                                manage_messages=True
                            )
            else:
                self.categories[cat_name] = existing

    async def create_channels(self):
        """Create all necessary channels"""
        channels_to_create = [
            # Main category channels
            ("🎮 OCTANE CORE", [
                ("🚀-dashboard", "Main bot dashboard with all features"),
                ("📋-rules", "Community rules and guidelines"),
                ("🎯-queue", "Join matchmaking queues here"),
                ("📢-match-announcements", "Automated match notifications"),
                ("🎮-active-matches", "Live match tracking"),
                ("🏅-achievements", "Achievement notifications and guides")
            ]),
            # Tournament channels
            ("🏆 TOURNAMENTS", [
                ("🏆-tournament-hub", "Tournament creation and management"),
                ("📋-tournament-brackets", "Tournament brackets and results"),
                ("🎪-tournament-chat", "Tournament discussion"),
                ("🔄-auto-tournaments", "Automatic tournament announcements")
            ]),
            # Statistics channels
            ("📊 STATISTICS", [
                ("📈-leaderboards", "Server rankings and stats"),
                ("📜-match-history", "Match results and history"),
                ("⭐-mvp-showcase", "MVP highlights")
            ]),
            # Admin channels
            ("🔧 ADMIN", [
                ("🛠️-admin-panel", "Admin dashboard"),
                ("📝-bot-logs", "Bot activity logs"),
                ("🧪-testing-area", "Bot testing and debugging")
            ])
        ]
        
        for category_name, channels in channels_to_create:
            category = self.categories.get(category_name)
            if not category:
                continue
                
            for channel_name, channel_desc in channels:
                # Check if channel already exists
                existing = discord.utils.get(self.guild.channels, name=channel_name)
                if not existing:
                    channel = await self.guild.create_text_channel(
                        channel_name,
                        category=category,
                        topic=channel_desc
                    )
                    
                    # Set admin-only permissions for admin channels
                    if category_name == "🔧 ADMIN":
                        await channel.set_permissions(
                            self.guild.default_role,
                            read_messages=False,
                            send_messages=False
                        )
                        # Allow administrators
                        for role in self.guild.roles:
                            if role.permissions.administrator:
                                await channel.set_permissions(
                                    role,
                                    read_messages=True,
                                    send_messages=True,
                                    manage_messages=True
                                )
                    
                    self.created_channels.append(channel)
                else:
                    self.created_channels.append(existing)

    async def create_roles(self):
        """Create bot-specific roles"""
        roles_to_create = [
            ("🏆 Tournament Winner", 0xFFD700, "Tournament champions"),
            ("⭐ MVP Player", 0xFF6B00, "MVP award winners"),
            ("🎯 Queue Master", 0x00FFCC, "Active queue participants"),
            ("📊 Stats Tracked", 0x9B59B6, "Players with tracked statistics"),
            ("🤖 Bot Tester", 0x00FF00, "Beta testers and feedback providers")
        ]
        
        for role_name, color, description in roles_to_create:
            # Check if role already exists
            existing = discord.utils.get(self.guild.roles, name=role_name)
            if not existing:
                role = await self.guild.create_role(
                    name=role_name,
                    color=discord.Color(color),
                    mentionable=True,
                    reason=f"OctaneCore Setup: {description}"
                )
                self.created_roles.append(role)
            else:
                self.created_roles.append(existing)

    async def setup_permissions(self):
        """Configure additional channel permissions if needed"""
        # Permissions are now set during channel creation
        # This step can be used for additional permission tweaks if needed
        pass

    async def create_dashboards(self):
        """Create interactive dashboards in channels"""
        from dashboard import setup_dashboard
        from admin_dashboard import setup_admin_dashboard
        from test_system import setup_testing_dashboard
        
        # Main dashboard
        dashboard_channel = discord.utils.get(self.created_channels, name="🚀-dashboard")
        if dashboard_channel:
            await setup_dashboard(dashboard_channel)
        
        # Admin dashboard
        admin_channel = discord.utils.get(self.created_channels, name="🛠️-admin-panel")
        if admin_channel:
            await setup_admin_dashboard(admin_channel)
        
        # Testing dashboard
        testing_channel = discord.utils.get(self.created_channels, name="🧪-testing-area")
        if testing_channel:
            await setup_testing_dashboard(testing_channel)

    async def finalize_setup(self):
        """Final setup steps with comprehensive channel content"""
        # Main dashboard
        main_channel = discord.utils.get(self.created_channels, name="🚀-dashboard")
        if main_channel:
            from dashboard import setup_dashboard
            await setup_dashboard(main_channel)
            
            welcome_embed = discord.Embed(
                title="🎉 Welcome to OctaneCore Community!",
                description="**Your premier Rocket League Discord server is now online!**\n\nWe're building the ultimate competitive gaming community.",
                color=0x00ffcc
            )
            welcome_embed.add_field(
                name="🚀 Getting Started",
                value="• **New here?** Check <#rules> first\n• **Ready to play?** Use the dashboard above\n• **Need help?** Use `/help` command\n• **Join tournaments** for prizes!",
                inline=False
            )
            welcome_embed.add_field(
                name="🏆 Community Features",
                value="• **24/7 Matchmaking** - Always find games\n• **Tournaments** - Daily competitions\n• **Rankings** - Climb the leaderboards\n• **Economy** - Earn credits and rewards\n• **Clans** - Team up with friends",
                inline=False
            )
            welcome_embed.set_footer(text="🎮 Let's rocket! Welcome to the community!")
            await main_channel.send(embed=welcome_embed)

        # Rules channel
        rules_channel = discord.utils.get(self.created_channels, name="📋-rules")
        if rules_channel:
            rules_embed = discord.Embed(
                title="📋 OctaneCore Community Rules",
                description="**Welcome to our community! Please follow these rules to ensure everyone has a great experience.**",
                color=0xff6600
            )
            rules_embed.add_field(
                name="🎮 Gaming Rules",
                value="• **No smurfing** - Play at your skill level\n• **No toxicity** - Be respectful to all players\n• **No rage quitting** - Finish your matches\n• **Report cheaters** - Keep the game fair\n• **Use real names** - No offensive usernames",
                inline=False
            )
            rules_embed.add_field(
                name="💬 Chat Rules",
                value="• **Be respectful** - Treat others kindly\n• **No spam** - Keep conversations meaningful\n• **No NSFW content** - Keep it family-friendly\n• **English only** - In main channels\n• **Stay on topic** - Use appropriate channels",
                inline=False
            )
            rules_embed.add_field(
                name="🏆 Tournament Rules",
                value="• **Show up on time** - Respect schedules\n• **No stream sniping** - Play fair\n• **Follow admin decisions** - They're final\n• **Report issues quickly** - During matches\n• **Have fun!** - It's about community",
                inline=False
            )
            rules_embed.add_field(
                name="⚠️ Violations & Consequences",
                value="• **1st offense:** Warning\n• **2nd offense:** Temporary queue ban\n• **3rd offense:** Tournament ban\n• **Severe violations:** Immediate ban",
                inline=False
            )
            rules_embed.set_footer(text="By using OctaneCore, you agree to follow these rules • Last updated: Today")
            await rules_channel.send(embed=rules_embed)

        # Queue channel with enhanced content
        queue_channel = discord.utils.get(self.created_channels, name="🎯-queue")
        if queue_channel:
            from main import QueueView
            queue_embed = discord.Embed(
                title="🎮 Matchmaking Central",
                description="**Find your perfect match in seconds!**\n\nOur smart matchmaking system creates balanced games across all skill levels.",
                color=0x00ffcc
            )
            queue_embed.add_field(
                name="🎯 Available Modes",
                value="⚽ **Soccar** - Classic Rocket League\n🏀 **Hoops** - Basketball mode\n🏒 **Snow Day** - Hockey with puck\n🎯 **Heatseeker** - Auto-targeting ball",
                inline=True
            )
            queue_embed.add_field(
                name="🔥 Queue Status",
                value="**1v1:** 0 players\n**2v2:** 0 players\n**3v3:** 0 players",
                inline=True
            )
            queue_embed.add_field(
                name="💡 Pro Tips",
                value="• **Peak hours:** 6-10 PM\n• **Fastest queue:** 2v2 Soccar\n• **Rank matters:** Similar skill levels\n• **Be patient:** Quality over speed",
                inline=False
            )
            queue_embed.set_footer(text="🔄 Updates every 15 seconds • Average wait time: 2 minutes")
            
            view = QueueView()
            await queue_channel.send(embed=queue_embed, view=view)

        # Achievement channel
        achievement_channel = discord.utils.get(self.created_channels, name="🏅-achievements")
        if achievement_channel:
            from achievements import ACHIEVEMENTS
            
            achievement_embed = discord.Embed(
                title="🏅 Achievement System",
                description="**Unlock rewards by showing your skills!**\n\nComplete challenges to earn MMR bonuses, badges, and exclusive rewards.",
                color=0xFFD700
            )
            
            # Group achievements by rarity
            rarity_groups = {}
            for ach_id, ach in ACHIEVEMENTS.items():
                rarity = ach["rarity"]
                if rarity not in rarity_groups:
                    rarity_groups[rarity] = []
                rarity_groups[rarity].append(ach)
            
            for rarity in ["Common", "Uncommon", "Rare", "Epic", "Legendary", "Mythic"]:
                if rarity in rarity_groups:
                    ach_list = rarity_groups[rarity]
                    ach_text = "\n".join([f"{ach['emoji']} **{ach['name']}** - {ach['description']}" for ach in ach_list[:3]])
                    if len(ach_list) > 3:
                        ach_text += f"\n*...and {len(ach_list)-3} more*"
                    achievement_embed.add_field(name=f"🎖️ {rarity} Achievements", value=ach_text, inline=False)
            
            achievement_embed.add_field(
                name="💡 How to Unlock",
                valu�e="• **Play matches** - All stats are tracked\n• **Score goals** - Show your offensive skills\n• **Make saves** - Defensive prowess counts\n• **Win tournaments** - Ultimate achievement\n• **Use `/achievements`** - Check your progress",
                inline=False
            )
            await achievement_channel.send(embed=achievement_embed)

        # Tournament hub
        tournament_channel = discord.utils.get(self.created_channels, name="🏆-tournament-hub")
        if tournament_channel:
            tournament_embed = discord.Embed(
                title="🏆 Tournament Central",
                description="**Compete for glory and prizes!**\n\nJoin tournaments to test your skills against the best players in our community.",
                color=0xFFD700
            )
            tournament_embed.add_field(
                name="🎯 Tournament Types",
                value="• **Daily Tournaments** - Quick competitions\n• **Weekly Championships** - Big prizes\n• **Seasonal Leagues** - Long-term competition\n• **Special Events** - Holiday tournaments",
                inline=True
            )
            tournament_embed.add_field(
                name="🏅 Prizes",
                value="• **Credits** - 100-1000 per tournament\n• **Exclusive Roles** - Show your victories\n• **Custom Badges** - Profile customization\n• **Special Perks** - VIP queue access",
                inline=True
            )
            tournament_embed.add_field(
                name="📅 Schedule",
                value="• **Auto Tournaments:** Every 2 hours\n• **Featured Events:** Weekends\n• **Clan Wars:** Monthly\n• **Check announcements** for special events",
                inline=False
            )
            await tournament_channel.send(embed=tournament_embed)

        # Match announcements
        announcement_channel = discord.utils.get(self.created_channels, name="📢-match-announcements")
        if announcement_channel:
            announcement_embed = discord.Embed(
                title="📢 Match Announcements",
                description="**Stay updated on all the action!**\n\nThis channel automatically posts match results, MVP awards, and tournament updates.",
                color=0x00ff00
            )
            announcement_embed.add_field(
                name="📊 What Gets Posted",
                value="• **Match Results** - Scores and highlights\n• **MVP Awards** - Outstanding performances\n• **Tournament Updates** - Bracket progression\n• **Achievement Unlocks** - Player milestones\n• **Leaderboard Changes** - Rank updates",
                inline=False
            )
            announcement_embed.add_field(
                name="🔔 Notification Settings",
                value="Right-click this channel → Notification Settings → All Messages\nNever miss important updates!",
                inline=False
            )
            await announcement_channel.send(embed=announcement_embed)

        # Statistics channel
        stats_channel = discord.utils.get(self.created_channels, name="📈-leaderboards")
        if stats_channel:
            stats_embed = discord.Embed(
                title="📈 Community Leaderboards",
                description="**See who's dominating the competition!**\n\nTrack your progress and compete for the top spots.",
                color=0x9b59b6
            )
            stats_embed.add_field(
                name="🏆 Leaderboard Categories",
                value="• **MMR Rankings** - Overall skill level\n• **Goals Scored** - Offensive leaders\n• **Saves Made** - Defensive masters\n• **MVP Awards** - Most valuable players\n• **Tournament Wins** - Champions",
                inline=True
            )
            stats_embed.add_field(
                name="📊 Stats Tracked",
                value="• **Matches Played** - Activity level\n• **Win/Loss Ratio** - Success rate\n• **Average Goals** - Scoring ability\n• **Match Duration** - Playing time\n• **Rank Progression** - Improvement",
                inline=True
            )
            stats_embed.add_field(
                name="🎯 Use Commands",
                value="• `/mystats` - Your personal stats\n• `/leaderboard` - Server rankings\n• `/match_history` - Recent games\n• Updates automatically every hour",
                inline=False
            )
            await stats_channel.send(embed=stats_embed)

        # Auto tournament setup
        auto_tournament_channel = discord.utils.get(self.created_channels, name="🔄-auto-tournaments")
        if auto_tournament_channel:
            from utils import load_admin_settings, save_admin_settings
            settings = load_admin_settings()
            
            settings["auto_tournament"] = {
                "enabled": True,
                "interval_minutes": 120,
                "format": "3v3",
                "map": "DFH Stadium",
                "mode": "Soccar",
                "max_teams": 16,
                "channel_id": auto_tournament_channel.id
            }
            save_admin_settings(settings)
            
            auto_embed = discord.Embed(
                title="🔄 Automated Tournament Hub",
                description="**24/7 Tournament Action!**\n\nTournaments are automatically created every 2 hours. Never miss the competition!",
                color=0xFF6B00
            )
            auto_embed.add_field(
                name="⏰ Schedule",
                value="• **Every 2 hours** - New tournament created\n• **2-hour registration** - Sign up period\n• **Auto-start** - When enough teams join\n• **Quick matches** - 15-30 minutes each",
                inline=False
            )
            auto_embed.add_field(
                name="🎯 How to Join",
                value="1️⃣ Wait for tournament announcement\n2️⃣ Click registration button\n3️⃣ Fill in team details\n4️⃣ Compete for prizes!",
                inline=False
            )
            auto_embed.set_footer(text="🏆 Next tournament in ~2 hours • Check back regularly!")
            await auto_tournament_channel.send(embed=auto_embed)

        # Admin logs setup
        if LOG_CHANNEL_ID:
            try:
                log_channel = self.guild.get_channel(int(LOG_CHANNEL_ID))
                if log_channel:
                    log_embed = discord.Embed(
                        title="🤖 Bot Activity Logs",
                        description="**Comprehensive logging system active!**\n\nThis channel receives all bot activity, errors, and system events.",
                        color=0x36393f
                    )
                    log_embed.add_field(
                        name="📊 Log Types",
                        value="• **INFO** - General activities\n• **DEBUG** - Detailed system info\n• **WARNING** - Potential issues\n• **ERROR** - System errors\n• **SUCCESS** - Completed actions",
                        inline=False
                    )
                    await log_channel.send(embed=log_embed)
            except:
                pass

    @discord.ui.button(label="🗑️ Clean Setup", style=discord.ButtonStyle.danger, emoji="🗑️")
    async def clean_setup(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Only administrators can clean setup!", ephemeral=True)
            return

        view = discord.ui.View()
        
        confirm_btn = discord.ui.Button(label="✅ Confirm Clean", style=discord.ButtonStyle.danger)
        cancel_btn = discord.ui.Button(label="❌ Cancel", style=discord.ButtonStyle.secondary)
        
        async def confirm_clean(confirm_interaction):
            await confirm_interaction.response.defer()
            
            # Delete OctaneCore channels and roles
            deleted_channels = 0
            deleted_roles = 0
            
            # Delete channels with OctaneCore names
            octane_keywords = ["octane", "dashboard", "queue", "tournament", "match", "stats", "admin-panel", "testing-area"]
            for channel in self.guild.channels:
                if any(keyword in channel.name.lower() for keyword in octane_keyw�ords):
                    try:
                        await channel.delete(reason="OctaneCore cleanup")
                        deleted_channels += 1
                    except:
                        pass
            
            # Delete OctaneCore roles
            octane_role_keywords = ["tournament winner", "mvp player", "queue master", "stats tracked", "bot tester"]
            for role in self.guild.roles:
                if any(keyword in role.name.lower() for keyword in octane_role_keywords):
                    try:
                        await role.delete(reason="OctaneCore cleanup")
                        deleted_roles += 1
                    except:
                        pass
            
            embed = discord.Embed(
                title="🗑️ Cleanup Complete",
                description=f"Removed {deleted_channels} channels and {deleted_roles} roles",
                color=0xff0000
            )
            await confirm_interaction.followup.send(embed=embed)
        
        async def cancel_clean(cancel_interaction):
            await cancel_interaction.response.send_message("❌ Cleanup cancelled.", ephemeral=True)
        
        confirm_btn.callback = confirm_clean
        cancel_btn.callback = cancel_clean
        view.add_item(confirm_btn)
        view.add_item(cancel_btn)
        
        await interaction.response.send_message(
            "⚠️ **WARNING**: This will delete all OctaneCore channels and roles. Are you sure?",
            view=view,
            ephemeral=True
        )

async def setup_server_command(interaction: discord.Interaction):
    """Main setup command function"""
    embed = discord.Embed(
        title="🚀 OctaneCore Server Setup",
        description="Welcome to the OctaneCore setup wizard!\n\nThis will create all necessary channels, roles, and dashboards for your server.",
        color=0x00ffcc
    )
    
    embed.add_field(
        name="📋 What will be created:",
        value="• **Categories**: Organized channel structure\n• **Channels**: Dashboard, queue, tournaments, stats\n• **Roles**: Tournament winners, MVP players, etc.\n• **Dashboards**: Interactive control panels\n• **Permissions**: Proper access control",
        inline=False
    )
    
    embed.add_field(
        name="⚠️ Requirements:",
        value="• Administrator permissions\n• Bot has necessary permissions\n• Server has available channel/role slots",
        inline=False
    )
    
    embed.set_footer(text="Click 'Full Setup' to begin the automated setup process")
    
    view = SetupView(interaction.guild)
    await interaction.response.send_message(embed=embed, view=view)
