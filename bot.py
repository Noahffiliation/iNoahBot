import logging
import os

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Logger setup
logger = logging.getLogger("iNoahBot")


# Bot configuration
class NoahBot(commands.Bot):
    async def setup_hook(self):
        # Sync slash commands once during startup
        try:
            synced = await self.tree.sync()
            logger.info("Synced %d command(s)", len(synced))
        except Exception:
            logger.exception("Failed to sync commands!")


intents = discord.Intents.default()
bot = NoahBot(command_prefix="!", intents=intents)

NO_PERMISSION_COMMAND_MESSAGE = "You don't have permission to use this command!"


@bot.event
async def on_ready():
    logger.info("%s has connected to Discord!", bot.user)
    logger.info("Bot is in %d servers", len(bot.guilds))


def create_user_info_embed(member: discord.Member | discord.User) -> discord.Embed:
    """Build a standardized user info embed for slash commands and context menus."""
    color = getattr(member, "color", discord.Color.default())
    embed = discord.Embed(title=f"User Info - {member}", color=color)
    avatar_url = member.avatar.url if member.avatar else member.default_avatar.url
    embed.set_thumbnail(url=avatar_url)
    embed.add_field(name="ID", value=str(member.id), inline=True)
    embed.add_field(
        name="Created", value=discord.utils.format_dt(member.created_at, style="D"), inline=True
    )
    joined_at = getattr(member, "joined_at", None)
    if joined_at:
        embed.add_field(
            name="Joined", value=discord.utils.format_dt(joined_at, style="D"), inline=True
        )
    roles = getattr(member, "roles", None)
    if roles is not None and len(roles) > 0:
        embed.add_field(
            name="Roles", value=str(len(roles) - 1), inline=True
        )  # -1 to exclude @everyone

        # Add role list if user has roles
        if len(roles) > 1:
            role_mentions = [role.mention for role in roles[1:]]  # Exclude @everyone
            roles_text = (
                ", ".join(role_mentions)
                if len(role_mentions) <= 10
                else ", ".join(role_mentions[:10]) + f" (+{len(role_mentions) - 10} more)"
            )
            embed.add_field(name="Role list", value=roles_text, inline=False)

    return embed


# Slash Commands
@bot.tree.command(name="info", description="Display bot information")
async def info(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Bot Information",
        description="A simple Discord bot with slash commands",
        color=0x00FF00,
    )
    embed.add_field(name="Servers", value=str(len(bot.guilds)), inline=True)
    embed.add_field(name="Users", value=str(len(bot.users)), inline=True)
    embed.add_field(name="Latency", value=f"{round(bot.latency * 1000)}ms", inline=True)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="userinfo", description="Get information about a user")
@app_commands.guild_only()
@app_commands.describe(member="The member to get info about (defaults to you)")
async def userinfo(
    interaction: discord.Interaction, member: discord.Member | discord.User | None = None
):
    target = member or interaction.user
    embed = create_user_info_embed(target)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="serverinfo", description="Get information about the server")
@app_commands.guild_only()
async def serverinfo(interaction: discord.Interaction):
    guild = interaction.guild
    if not guild:
        await interaction.response.send_message(
            "This command can only be used in a server.", ephemeral=True
        )
        return

    embed = discord.Embed(title=f"Server Info - {guild.name}", color=0x0099FF)

    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)

    embed.add_field(name="Server ID", value=str(guild.id), inline=True)
    embed.add_field(
        name="Owner", value=guild.owner.mention if guild.owner else "Unknown", inline=True
    )
    embed.add_field(
        name="Created", value=discord.utils.format_dt(guild.created_at, style="D"), inline=True
    )
    embed.add_field(name="Members", value=str(guild.member_count or 0), inline=True)
    embed.add_field(name="Channels", value=str(len(guild.channels)), inline=True)
    embed.add_field(name="Roles", value=str(len(guild.roles)), inline=True)
    embed.add_field(name="Boosts", value=str(guild.premium_subscription_count or 0), inline=True)
    embed.add_field(name="Boost Level", value=str(guild.premium_tier), inline=True)

    await interaction.response.send_message(embed=embed)


# Context menu commands (right-click commands)
@bot.tree.context_menu(name="User Info")
@app_commands.guild_only()
async def context_userinfo(interaction: discord.Interaction, member: discord.Member):
    """Right-click context menu command for user info"""
    embed = create_user_info_embed(member)
    await interaction.response.send_message(embed=embed, ephemeral=True)


# Error handling for slash commands
@bot.tree.error
async def on_app_command_error(
    interaction: discord.Interaction, error: app_commands.AppCommandError
):
    if isinstance(error, app_commands.MissingPermissions):
        msg = NO_PERMISSION_COMMAND_MESSAGE
    elif isinstance(error, app_commands.CommandOnCooldown):
        msg = f"Command is on cooldown. Try again in {error.retry_after:.2f} seconds."
    else:
        logger.error("Slash command error: %s", error, exc_info=error)
        msg = "An error occurred while processing the command."

    if not interaction.response.is_done():
        await interaction.response.send_message(msg, ephemeral=True)
    else:
        await interaction.followup.send(msg, ephemeral=True)


def main():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        logger.error("DISCORD_TOKEN not found in environment variables!")
        logger.error(
            "Please create a .env file with your bot token: DISCORD_TOKEN=your_bot_token_here"
        )
        return
    bot.run(token)


# Run the bot
if __name__ == "__main__":  # pragma: no cover
    main()
