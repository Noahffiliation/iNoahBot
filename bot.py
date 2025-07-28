import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True  # Still useful for some features
bot = commands.Bot(command_prefix='!', intents=intents)

NO_PERMISSION_COMMAND_MESSAGE = "You don't have permission to use this command!"

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} servers')

    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} command(s)')
    except Exception as e:
        print(f'Failed to sync commands: {e}')

# Slash Commands
@bot.tree.command(name='info', description='Display bot information')
async def info(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Bot Information",
        description="A simple Discord bot with slash commands",
        color=0x00ff00
    )
    embed.add_field(name="Servers", value=len(bot.guilds), inline=True)
    embed.add_field(name="Users", value=len(bot.users), inline=True)
    embed.add_field(name="Latency", value=f"{round(bot.latency * 1000)}ms", inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='userinfo', description='Get information about a user')
@app_commands.describe(member='The member to get info about (defaults to you)')
async def userinfo(interaction: discord.Interaction, member: discord.Member = None):
    if member is None:
        member = interaction.user

    embed = discord.Embed(
        title=f"User Info - {member}",
        color=member.color
    )
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    embed.add_field(name="ID", value=member.id, inline=True)
    embed.add_field(name="Created", value=discord.utils.format_dt(member.created_at, style='D'), inline=True)
    embed.add_field(name="Joined", value=discord.utils.format_dt(member.joined_at, style='D'), inline=True)
    embed.add_field(name="Roles", value=len(member.roles) - 1, inline=True)  # -1 to exclude @everyone

    # Add role list if user has roles
    if len(member.roles) > 1:
        roles = [role.mention for role in member.roles[1:]]  # Exclude @everyone
        roles_text = ', '.join(roles) if len(roles) <= 10 else ', '.join(roles[:10]) + f' (+{len(roles) - 10} more)'
        embed.add_field(name="Role list", value=roles_text, inline=False)

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='serverinfo', description='Get information about the server')
async def serverinfo(interaction: discord.Interaction):
    guild = interaction.guild

    embed = discord.Embed(
        title=f"Server Info - {guild.name}",
        color=0x0099ff
    )

    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)

    embed.add_field(name="Server ID", value=guild.id, inline=True)
    embed.add_field(name="Owner", value=guild.owner.mention if guild.owner else "Unknown", inline=True)
    embed.add_field(name="Created", value=discord.utils.format_dt(guild.created_at, style='D'), inline=True)
    embed.add_field(name="Members", value=guild.member_count, inline=True)
    embed.add_field(name="Channels", value=len(guild.channels), inline=True)
    embed.add_field(name="Roles", value=len(guild.roles), inline=True)
    embed.add_field(name="Boosts", value=guild.premium_subscription_count, inline=True)
    embed.add_field(name="Boost Level", value=guild.premium_tier, inline=True)

    await interaction.response.send_message(embed=embed)

# Context menu commands (right-click commands)
@bot.tree.context_menu(name='User Info')
async def context_userinfo(interaction: discord.Interaction, member: discord.Member):
    """Right-click context menu command for user info"""
    embed = discord.Embed(
        title=f"User Info - {member}",
        color=member.color
    )
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    embed.add_field(name="ID", value=member.id, inline=True)
    embed.add_field(name="Created", value=discord.utils.format_dt(member.created_at, style='D'), inline=True)
    embed.add_field(name="Joined", value=discord.utils.format_dt(member.joined_at, style='D'), inline=True)
    embed.add_field(name="Roles", value=len(member.roles) - 1, inline=True)

    await interaction.response.send_message(embed=embed, ephemeral=True)

# Error handling for slash commands
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message(NO_PERMISSION_COMMAND_MESSAGE, ephemeral=True)
    elif isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(f"Command is on cooldown. Try again in {error.retry_after:.2f} seconds.", ephemeral=True)
    else:
        print(f'Slash command error: {error}')
        if not interaction.response.is_done():
            await interaction.response.send_message("An error occurred while processing the command.", ephemeral=True)

# Run the bot
if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("Error: DISCORD_TOKEN not found in environment variables!")
        print("Please create a .env file with your bot token:")
        print("DISCORD_TOKEN=your_bot_token_here")
    else:
        bot.run(token)
