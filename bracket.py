

from PIL import Image, ImageDraw, ImageFont
import os

def generate_bracket_image(teams, format_type=None, map_name=None, game_mode=None):
    width = 900
    height = 150 + len(teams) * 70
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    title_font = ImageFont.truetype(font_path, 24) if os.path.exists(font_path) else None
    team_font = ImageFont.truetype(font_path, 18) if os.path.exists(font_path) else None
    info_font = ImageFont.truetype(font_path, 14) if os.path.exists(font_path) else None

    # Header
    draw.rectangle([0, 0, width, 80], fill="#00ffcc", outline="black", width=2)
    draw.text((width//2 - 150, 15), "🏆 ROCKET LEAGUE TOURNAMENT", fill="black", font=title_font)
    
    # Tournament info
    if format_type and map_name and game_mode:
        info_text = f"Format: {format_type} | Map: {map_name} | Mode: {game_mode}"
        draw.text((width//2 - len(info_text)*4, 45), info_text, fill="black", font=info_font)

    # Teams bracket
    for i, team in enumerate(teams):
        y = 100 + i * 70
        
        # Team box
        draw.rectangle([50, y, 450, y + 50], outline="black", width=2, fill="#f0f0f0")
        
        # Team name
        name = team["name"]
        draw.text((60, y + 15), f"#{i+1} {name}", fill="black", font=team_font)
        
        # Players
        players_text = ", ".join(team["players"])
        if len(players_text) > 40:
            players_text = players_text[:37] + "..."
        draw.text((60, y + 35), f"Players: {players_text}", fill="gray", font=info_font)
        
        # VS connector (except for last team)
        if i < len(teams) - 1:
            draw.text((470, y + 25), "VS", fill="red", font=team_font)

    # Bracket lines
    if len(teams) >= 2:
        # Draw bracket structure
        start_y = 125
        end_y = 100 + (len(teams) - 1) * 70 + 25
        
        # Vertical line
        draw.line([500, start_y, 500, end_y], fill="black", width=3)
        
        # Horizontal lines to teams
        for i in range(len(teams)):
            team_y = 125 + i * 70
            draw.line([450, team_y, 500, team_y], fill="black", width=2)

    path = "bracket.png"
    image.save(path)
    return path

