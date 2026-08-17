from unittest.mock import AsyncMock, MagicMock, patch

import discord
import pytest
from discord import app_commands

from bot import (
    NoahBot,
    context_userinfo,
    info,
    main,
    on_app_command_error,
    on_ready,
    serverinfo,
    userinfo,
)


@pytest.mark.asyncio
async def test_info_command(mock_interaction, mock_bot):
    with patch("bot.bot", mock_bot):
        await info.callback(mock_interaction)
        mock_interaction.response.send_message.assert_called_once()
        embed = mock_interaction.response.send_message.call_args[1]["embed"]
        assert embed.title == "Bot Information"


@pytest.mark.asyncio
async def test_userinfo_command_self(mock_interaction):
    await userinfo.callback(mock_interaction, None)
    mock_interaction.response.send_message.assert_called_once()
    embed = mock_interaction.response.send_message.call_args[1]["embed"]
    assert "User Info" in embed.title


@pytest.mark.asyncio
async def test_userinfo_command_other(mock_interaction):
    other_member = MagicMock()
    other_member.name = "OtherUser"
    other_member.id = 987654321
    other_member.roles = []
    other_member.discriminator = "5678"
    other_member.color = discord.Color.red()
    other_member.__str__.return_value = "OtherUser#5678"

    await userinfo.callback(mock_interaction, other_member)
    mock_interaction.response.send_message.assert_called_once()
    embed = mock_interaction.response.send_message.call_args[1]["embed"]
    assert "User Info - OtherUser" in embed.title


@pytest.mark.asyncio
async def test_userinfo_with_roles(mock_interaction):
    member_with_roles = MagicMock()
    member_with_roles.name = "RoleUser"
    member_with_roles.id = 11111
    member_with_roles.color = discord.Color.blue()
    member_with_roles.__str__.return_value = "RoleUser#1111"

    # Create mock roles
    role1 = MagicMock(spec=discord.Role)
    role1.mention = "<@&1>"
    role1.name = "Role1"
    role2 = MagicMock(spec=discord.Role)
    role2.mention = "<@&2>"
    role2.name = "Role2"
    # Member always has @everyone role at index 0
    member_with_roles.roles = [MagicMock(), role1, role2]

    await userinfo.callback(mock_interaction, member_with_roles)
    mock_interaction.response.send_message.assert_called_once()
    embed = mock_interaction.response.send_message.call_args[1]["embed"]
    field_value = next(f.value for f in embed.fields if f.name == "Role list")
    assert "<@&1>" in field_value
    assert "<@&2>" in field_value


@pytest.mark.asyncio
async def test_serverinfo_command(mock_interaction):
    await serverinfo.callback(mock_interaction)
    mock_interaction.response.send_message.assert_called_once()
    embed = mock_interaction.response.send_message.call_args[1]["embed"]
    assert "Server Info - TestGuild" in embed.title


@pytest.mark.asyncio
async def test_context_userinfo(mock_interaction):
    target_member = MagicMock(spec=discord.Member)
    target_member.name = "TargetUser"
    target_member.id = 55555
    target_member.roles = []
    target_member.color = discord.Color.green()

    await context_userinfo.callback(mock_interaction, target_member)
    mock_interaction.response.send_message.assert_called_once()
    assert mock_interaction.response.send_message.call_args[1]["ephemeral"] is True


@pytest.mark.asyncio
async def test_on_app_command_error_permissions_not_done(mock_interaction):
    mock_interaction.response.is_done.return_value = False
    error = app_commands.MissingPermissions(["administrator"])
    await on_app_command_error(mock_interaction, error)
    mock_interaction.response.send_message.assert_called_once()
    assert "permission" in mock_interaction.response.send_message.call_args[0][0]


@pytest.mark.asyncio
async def test_on_app_command_error_permissions_done(mock_interaction):
    mock_interaction.response.is_done.return_value = True
    error = app_commands.MissingPermissions(["administrator"])
    await on_app_command_error(mock_interaction, error)
    mock_interaction.followup.send.assert_called_once()
    assert "permission" in mock_interaction.followup.send.call_args[0][0]


@pytest.mark.asyncio
async def test_on_app_command_error_cooldown_not_done(mock_interaction):
    mock_interaction.response.is_done.return_value = False
    error = app_commands.CommandOnCooldown(MagicMock(), 10.5)
    await on_app_command_error(mock_interaction, error)
    mock_interaction.response.send_message.assert_called_once()
    assert "cooldown" in mock_interaction.response.send_message.call_args[0][0]


@pytest.mark.asyncio
async def test_on_app_command_error_cooldown_done(mock_interaction):
    mock_interaction.response.is_done.return_value = True
    error = app_commands.CommandOnCooldown(MagicMock(), 10.5)
    await on_app_command_error(mock_interaction, error)
    mock_interaction.followup.send.assert_called_once()
    assert "cooldown" in mock_interaction.followup.send.call_args[0][0]


@pytest.mark.asyncio
async def test_on_app_command_error_generic_not_done(mock_interaction):
    mock_interaction.response.is_done.return_value = False
    error = app_commands.AppCommandError("Generic error")
    await on_app_command_error(mock_interaction, error)
    mock_interaction.response.send_message.assert_called_once()
    assert "error occurred" in mock_interaction.response.send_message.call_args[0][0]


@pytest.mark.asyncio
async def test_on_app_command_error_generic_done(mock_interaction):
    mock_interaction.response.is_done.return_value = True
    error = app_commands.AppCommandError("Generic error")
    await on_app_command_error(mock_interaction, error)
    mock_interaction.followup.send.assert_called_once()
    assert "error occurred" in mock_interaction.followup.send.call_args[0][0]


@pytest.mark.asyncio
async def test_on_ready(mock_bot):
    with patch("bot.bot", mock_bot):
        await on_ready()


@pytest.mark.asyncio
async def test_setup_hook_success():
    bot_instance = NoahBot(command_prefix="!", intents=discord.Intents.default())
    with patch.object(bot_instance.tree, "sync", new_callable=AsyncMock) as mock_sync:
        mock_sync.return_value = [1, 2, 3]
        await bot_instance.setup_hook()
        mock_sync.assert_called_once()


@pytest.mark.asyncio
async def test_setup_hook_error():
    bot_instance = NoahBot(command_prefix="!", intents=discord.Intents.default())
    with patch.object(bot_instance.tree, "sync", new_callable=AsyncMock) as mock_sync:
        mock_sync.side_effect = Exception("Sync failure")
        await bot_instance.setup_hook()
        mock_sync.assert_called_once()


def test_main_missing_token(monkeypatch):
    monkeypatch.delenv("DISCORD_TOKEN", raising=False)
    with patch("bot.bot.run") as mock_run:
        main()
        mock_run.assert_not_called()


def test_main_with_token(monkeypatch):
    monkeypatch.setenv("DISCORD_TOKEN", "test_fake_token")
    with patch("bot.bot.run") as mock_run:
        main()
        mock_run.assert_called_once_with("test_fake_token")
