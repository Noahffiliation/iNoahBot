import pytest
import discord
from discord.ext import commands
from unittest.mock import AsyncMock, MagicMock, patch

@pytest.fixture
def mock_bot():
    bot = MagicMock(spec=commands.Bot)
    bot.user = MagicMock()
    bot.user.__str__.return_value = "TestBot#1234"
    bot.guilds = []
    bot.tree = AsyncMock()
    bot.latency = 0.05
    return bot

@pytest.fixture
def mock_interaction():
    interaction = AsyncMock(spec=discord.Interaction)
    interaction.response = AsyncMock()
    interaction.response.is_done = MagicMock(return_value=False)
    interaction.user = MagicMock(spec=discord.Member)
    interaction.user.name = "TestUser"
    interaction.user.discriminator = "1234"
    interaction.user.id = 123456789
    interaction.user.color = discord.Color.blue()
    interaction.guild = MagicMock(spec=discord.Guild)
    interaction.guild.name = "TestGuild"
    interaction.guild.id = 987654321
    interaction.guild.member_count = 100
    interaction.guild.owner = MagicMock(spec=discord.Member)
    interaction.guild.owner.mention = "<@OwnerID>"
    return interaction
