import os
import nextcord
from nextcord import SlashOption 
from nextcord.ext import commands
from getstats import fetch_skywars_stats
from getstats import fetch_bedwars_stats
from getstats import fetch_additional_stats
from getstats import fetch_murder_stats
from getstats import fetch_survivalgame_stats
from getstats import fetch_deathrun_stats
from getstats import fetch_capturetheflag_stats
from getstats import fetch_justbuild_stats
from dotenv.main import load_dotenv


load_dotenv()


intents = nextcord.Intents.all()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.slash_command(description="ดึงข้อมูลผู้เล่นจาก HiveMC")
async def hivestats(
    interaction: nextcord.Interaction,
    game: str = nextcord.SlashOption(
        name="game",
        description="เลือกเกมที่ต้องการดึงข้อมูล",
        choices=["Skywars", "Bedwars", "Murder", "Deathrun", "Survival", "Capture The Flag", "Build Battle"]
    ),
    player_name: str = nextcord.SlashOption(
        name="player_name",
        description="ชื่อผู้เล่นที่ต้องการดึงข้อมูล"
    )
):
    # ใช้ defer() กันมันเอ๋อหลังผ่านไป 3 วิ
    
    try:
        await interaction.response.defer()
        if game.lower() == "skywars":
            player_stats = await fetch_skywars_stats(player_name)
        elif game.lower() == "bedwars":
            player_stats = await fetch_bedwars_stats(player_name)
        elif game.lower() == "murder":
            player_stats = await fetch_murder_stats(player_name)
        elif game.lower() == "deathrun":
            player_stats = await fetch_deathrun_stats(player_name)
        elif game.lower() == "survival":
            player_stats = await fetch_survivalgame_stats(player_name)
        elif game.lower() == "capture the flag":
            player_stats = await fetch_capturetheflag_stats(player_name)
        elif game.lower() == "build battle":
            player_stats = await fetch_justbuild_stats(player_name)
        else:
            await interaction.followup.send("เกมที่คุณเลือกไม่รองรับ!", ephemeral=True)
            return

        # ดึงข้อมูลเพิ่มเติม
        additional_stats = await fetch_additional_stats(player_name)

        # ตรวจสอบข้อผิดพลาดในข้อมูลที่ดึงมา
        if "error" in player_stats or "error" in additional_stats:
            embed = nextcord.Embed(
                title="เกิดข้อผิดพลาดในการดึงข้อมูล",
                description=f"ไม่สามารถดึงข้อมูลของ **{player_name}** ได้\nโปรดตรวจสอบว่าชื่อหรือข้อมูลใน {game} ถูกต้องหรือไม่",
                color=0xff0000
            )
            embed.set_footer(
                text="ดูข้อมูลเพิ่มเติมที่: https://hivebe.link/p/" + player_name,
                icon_url="https://playhive.com/_next/image?url=%2F_next%2Fstatic%2Fmedia%2Fbeee.87692121.png&w=96&q=100"
            )
            await interaction.followup.send(embed=embed)
        else:
            embed = nextcord.Embed(
                title=f"ข้อมูลผู้เล่น: {player_stats['player_name']}",
                description=f"ฉายา: **{player_stats['details']}**\nข้อมูลสถิติ {game.capitalize()} (ตลอดอายุ)",
                color=0x00ff00
            )
            for stat_name, stat_value in player_stats["stats"].items():
                embed.add_field(name=stat_name, value=stat_value, inline=True)

            embed.add_field(name="ล็อคอินต่อเนื่อง", value=additional_stats["login_streak"], inline=True)
            embed.add_field(name="เควสสำเร็จแล้ว", value=additional_stats["quests_completed"], inline=True)

            embed.set_thumbnail(url=player_stats["avatar_url"])
            embed.set_footer(
                text="ดูข้อมูลเพิ่มเติมที่: https://hivebe.link/p/" + player_name,
                icon_url="https://playhive.com/_next/image?url=%2F_next%2Fstatic%2Fmedia%2Fbeee.87692121.png&w=96&q=100"
            )
            await interaction.followup.send(embed=embed)
    except Exception as e:
        await interaction.followup.send(f"เกิดข้อผิดพลาด: {e}", ephemeral=True)


my_secret = os.environ['DISCORD_BOT_SECRET']
bot.run(my_secret)