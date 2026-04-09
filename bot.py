import os
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from quotes import get_random_quote, get_quote_by_category, format_quote

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree


@bot.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("FFXI Quote Bot is ready - Vana'diel awaits!")


@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    import random
    if random.random() < 0.10:
        speaker, quote = get_random_quote()
        await message.channel.send(format_quote(speaker, quote))
    await bot.process_commands(message)


@bot.event
async def on_voice_state_update(
    member: discord.Member,
    before: discord.VoiceState,
    after: discord.VoiceState,
):
    if before.channel is None and after.channel is not None:
        speaker, quote = get_random_quote()
        guild = member.guild
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                await channel.send(
                    f"Joined: {after.channel.name}\n"
                    + format_quote(speaker, quote)
                )
                break


@bot.event
async def on_member_join(member: discord.Member):
    speaker, quote = get_random_quote()
    guild = member.guild
    target = guild.system_channel
    if target is None or not target.permissions_for(guild.me).send_messages:
        for ch in guild.text_channels:
            if ch.permissions_for(guild.me).send_messages:
                target = ch
                break
    if target:
        await target.send(
            f"{member.mention} has arrived in Vana'diel!\n"
            + format_quote(speaker, quote)
        )


@tree.command(name="ffxi", description="Get a random FFXI quote from Vana'diel!")
async def ffxi_quote(interaction: discord.Interaction):
    speaker, quote = get_random_quote()
    await interaction.response.send_message(format_quote(speaker, quote))


@tree.command(name="ffxi_category", description="Get an FFXI quote from a specific category.")
@app_commands.describe(category="Choose a category: npc, battle, moogle, emote")
@app_commands.choices(category=[
    app_commands.Choice(name="NPC / Story Quotes", value="npc"),
    app_commands.Choice(name="Battle Cries & Job Abilities", value="battle"),
    app_commands.Choice(name="Moogle Quips", value="moogle"),
    app_commands.Choice(name="Player Emote Flavor", value="emote"),
])
async def ffxi_category(interaction: discord.Interaction, category: app_commands.Choice[str]):
    speaker, quote = get_quote_by_category(category.value)
    await interaction.response.send_message(format_quote(speaker, quote))


if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError("DISCORD_TOKEN not set in .env file!")
    bot.run(TOKEN)
