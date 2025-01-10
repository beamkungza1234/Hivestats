import requests
from bs4 import BeautifulSoup
import nextcord
from nextcord.ext import commands
import aiohttp
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta

import math

def xp_to_level(xp):
    """
    คำนวณเลเวลจาก XP โดยใช้สมการ XP = 75n(n-1)
    :param xp: ค่าประสบการณ์สะสมของผู้เล่น
    :return: เลเวลที่คำนวณได้
    """
    # แปลง xp เป็นเลข LV เอาเป็นว่ามันแม่นอยู่
    a = 75
    b = -75
    c = -xp


    n = (-b + math.sqrt(b**2 - 4 * a * c)) / (2 * a)
    return math.floor(n)  

# ดึงข้อมูลเพิ่มเช่น Login Streak และ Quests Completed
async def fetch_additional_stats(player_name):
    url = f"https://hivebe.link/p/{player_name}" 

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                html = await response.text()

        soup = BeautifulSoup(html, 'html.parser')

        # ดึงข้อมูล Login Streak
        login_streak_tag = soup.find("p", string="Login Streak")
        login_streak_value = login_streak_tag.find_previous("h1").text.strip() if login_streak_tag else "ไม่พบข้อมูล"

        # ดึงข้อมูล Quests Completed
        quests_completed_tag = soup.find("p", string="Quests Completed")
        quests_completed_value = quests_completed_tag.find_previous("h1").text.strip() if quests_completed_tag else "ไม่พบข้อมูล"

        return {
            "login_streak": login_streak_value,
            "quests_completed": quests_completed_value
        }

    except aiohttp.ClientError as e:
        return {"error": f"ไม่สามารถเชื่อมต่อกับเว็บไซต์ได้: {e}"}
    except Exception as e:
        return {"error": f"เกิดข้อผิดพลาด: {e}"}

import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime

# Skywars
async def fetch_skywars_stats(player_name):
    api_url = f"https://api.playhive.com/v0/game/all/sky/{player_name}"
    profile_url = f"https://hivebe.link/p/{player_name}" # URL นี้ใช้ดึง pfp และฉายา

    try:
        # ดึงข้อมูลจาก API
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as api_response:
                if api_response.status == 200:
                    api_data = await api_response.json()
                else:
                    return {"error": f"ไม่สามารถดึงข้อมูลจาก API ได้ (สถานะ: {api_response.status})"}

            # ดึง HTML ของโปรไฟล์
            async with session.get(profile_url) as profile_response:
                profile_response.raise_for_status()
                html = await profile_response.text()

        soup = BeautifulSoup(html, 'html.parser')

        # ดึง URL รูปภาพ
        img_tag = soup.find("img", class_="object-contain")
        img_url = f"https://playhive.com{img_tag['src']}" if img_tag else "https://via.placeholder.com/150"

        # ดึงรายละเอียดเพิ่มเติม
        details_tag = soup.find("p", class_="text-shadow-sm text-shadow-black flex items-center pt-1 text-xl font-medium leading-5 text-white")
        details_text = details_tag.text.strip() if details_tag else "ไม่ได้ระบุฉายาไว้"

        # ดึงชื่อผู้เล่น
        player_name_tag = soup.find("h1", class_="text-shadow-lg text-shadow-black text-4xl font-semibold text-white md:text-6xl")
        player_name_text = player_name_tag.text.strip() if player_name_tag else "ไม่พบชื่อผู้เล่น"

        # เช็คยศพิเศษ
        special_rank_tag = soup.find("div", class_="text-shadow-sm")
        if special_rank_tag and "plus" in special_rank_tag.get("class", []):
            player_name_text += " ✨"  # เพิ่มอิโมจิเมื่อมียศพิเศษ

        # จัดรูปแบบข้อมูลที่ได้จาก API
        first_played_timestamp = api_data.get("first_played", 0)
        if first_played_timestamp:
            # แปลง Unix timestamp เป็น UTC
            first_played_utc = datetime.utcfromtimestamp(first_played_timestamp)
            # ปรับเวลาให้เป็น UTC+7 (เวลาของประเทศไทย)
            first_played_utc7 = first_played_utc + timedelta(hours=7)
            first_played = first_played_utc7.strftime('%Y-%m-%d %H:%M:%S')
        else:
            first_played = "ไม่พบข้อมูล"

        kills = api_data.get("kills", 0)
        deaths = api_data.get("deaths", 0)
        games_played = api_data.get("played", 0)
        victories = api_data.get("victories", 0)

        # คำนวณ K/D (Kill/Death ratio)
        kd_ratio = kills / deaths if deaths > 0 else kills  # ถ้าจำนวนการตายเป็น 0 ให้ค่าเป็นจำนวนการฆ่า (ไม่ตาย)

        # คำนวณเลเวลจาก XP
        xp = api_data.get("xp", 0)
        level = xp_to_level(xp)

        # คำนวณจำนวนการฆ่าต่อเกม
        kills_per_game = kills / games_played if games_played > 0 else 0

        # คำนวณอัตราการชนะ
        win_rate = (victories / games_played * 100) if games_played > 0 else 0

        # วิเคราะห์สไตล์การเล่น
        if kd_ratio > 2.0 and kills_per_game > 3.0:
            play_style = "เน้นการรุก"
        elif kd_ratio > 1.0 and win_rate > 50:
            play_style = "เน้นเอาตัวรอด"
        elif kd_ratio >= 1.5 and kd_ratio <= 2.5 and 40 <= win_rate <= 60:
            play_style = "สมดุล"
        elif win_rate > 60:
            play_style = "เน้นเป้าหมาย"
        else:
            play_style = "ไม่มีสไตล์การเล่นที่โดดเด่น"

        stats = {
            "เกมที่เล่นไปแล้ว": games_played,
            "เกมที่ชนะ": victories,
            "อัตราการชนะ": f"{win_rate:.2f}%",
            "จำนวนฆ่า": kills,
            "จำนวนการตาย": deaths,
            "K/D": f"{kd_ratio:.2f}",
            "จำนวนฆ่าต่อเกม": f"{kills_per_game:.2f}",
            "จำนวนแร่ที่ขุด": api_data.get("ores_mined", 0),
            "จำนวน Spellbook ที่ใช้": api_data.get("spells_used", 0),
            "หีบกลางเกาะที่ถูกทำลาย": api_data.get("mystery_chests_destroyed", 0),
            "XP": f"{xp} (LV.{level})",
            "เริ่มเล่นครั้งแรกเมื่อ": first_played,
            "สไตล์การเล่น": play_style  # เพิ่มข้อมูลสไตล์การเล่น
        }

        # ส่งข้อมูลกลับ
        return {
            "player_name": player_name_text,
            "avatar_url": img_url,
            "stats": stats,
            "details": details_text
        }

    except aiohttp.ClientError as e:
        return {"error": f"ไม่สามารถเชื่อมต่อกับ API หรือเว็บไซต์ได้: {e}"}
    except Exception as e:
        return {"error": f"เกิดข้อผิดพลาด: {e}"}



# Bedwars
async def fetch_bedwars_stats(player_name):
    api_url = f"https://api.playhive.com/v0/game/all/bed/{player_name}"
    profile_url = f"https://hivebe.link/p/{player_name}" # URL นี้ใช้ดึง pfp และฉายา

    try:
        # ดึงข้อมูลจาก API
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as api_response:
                if api_response.status == 200:
                    api_data = await api_response.json()
                else:
                    return {"error": f"ไม่สามารถดึงข้อมูลจาก API ได้ (สถานะ: {api_response.status})"}

            # ดึง HTML ของโปรไฟล์
            async with session.get(profile_url) as profile_response:
                profile_response.raise_for_status()
                html = await profile_response.text()

        soup = BeautifulSoup(html, 'html.parser')

        # ดึง URL รูปภาพ
        img_tag = soup.find("img", class_="object-contain")
        img_url = f"https://playhive.com{img_tag['src']}" if img_tag else "https://via.placeholder.com/150"

        # ดึงรายละเอียดเพิ่มเติม
        details_tag = soup.find("p", class_="text-shadow-sm text-shadow-black flex items-center pt-1 text-xl font-medium leading-5 text-white")
        details_text = details_tag.text.strip() if details_tag else "ไม่ได้ระบุฉายาไว้"

        # ดึงชื่อผู้เล่น
        player_name_tag = soup.find("h1", class_="text-shadow-lg text-shadow-black text-4xl font-semibold text-white md:text-6xl")
        player_name_text = player_name_tag.text.strip() if player_name_tag else "ไม่พบชื่อผู้เล่น"

        # เช็คยศพิเศษ
        special_rank_tag = soup.find("div", class_="text-shadow-sm")
        if special_rank_tag and "plus" in special_rank_tag.get("class", []):
            player_name_text += " ✨"  # เพิ่มอิโมจิเมื่อมียศพิเศษ

        # จัดรูปแบบข้อมูลที่ได้จาก API
        first_played_timestamp = api_data.get("first_played", 0)
        if first_played_timestamp:
            # แปลง Unix timestamp เป็น UTC
            first_played_utc = datetime.utcfromtimestamp(first_played_timestamp)
            # ปรับเวลาให้เป็น UTC+7 (เวลาของประเทศไทย)
            first_played_utc7 = first_played_utc + timedelta(hours=7)
            first_played = first_played_utc7.strftime('%Y-%m-%d %H:%M:%S')
        else:
            first_played = "ไม่พบข้อมูล"

        kills = api_data.get("kills", 0)
        deaths = api_data.get("deaths", 0)
        games_played = api_data.get("played", 0)
        victories = api_data.get("victories", 0)

        # คำนวณ K/D (Kill/Death ratio)
        kd_ratio = kills / deaths if deaths > 0 else kills  # ถ้าจำนวนการตายเป็น 0 ให้ค่าเป็นจำนวนการฆ่า (ไม่ตาย)

        # คำนวณเลเวลจาก XP
        xp = api_data.get("xp", 0)
        level = xp_to_level(xp)

        # คำนวณจำนวนการฆ่าต่อเกม
        kills_per_game = kills / games_played if games_played > 0 else 0

        # คำนวณอัตราการชนะ
        win_rate = (victories / games_played * 100) if games_played > 0 else 0

        # วิเคราะห์สไตล์การเล่น
        if kd_ratio > 2.0 and kills_per_game > 3.0:
            play_style = "เน้นการรุก"
        elif kd_ratio > 1.0 and win_rate > 50:
            play_style = "เน้นเอาตัวรอด"
        elif kd_ratio >= 1.5 and kd_ratio <= 2.5 and 40 <= win_rate <= 60:
            play_style = "สมดุล"
        elif win_rate > 60:
            play_style = "เน้นเป้าหมาย"
        else:
            play_style = "ไม่มีสไตล์ความถนัดที่โดดเด่น"

        stats = {
            "เกมที่เล่นไปแล้ว": games_played,
            "เกมที่ชนะ": victories,
            "อัตราการชนะ": f"{win_rate:.2f}%",
            "จำนวนฆ่า": kills,
            "จำนวนการตาย": deaths,
            "K/D": f"{kd_ratio:.2f}",
            "จำนวนฆ่าต่อเกม": f"{kills_per_game:.2f}",
            "เตียงที่ทำลาย": api_data.get("beds_destroyed", 0),
            "Final Kills": api_data.get("final_kills", 0),
            "XP": f"{xp} (LV.{level})",
            "เริ่มเล่นครั้งแรกเมื่อ": first_played,
            "ความถนัดในการเล่น": play_style  # เพิ่มข้อมูลสไตล์การเล่น
        }

        # ส่งข้อมูลกลับ
        return {
            "player_name": player_name_text,
            "avatar_url": img_url,
            "stats": stats,
            "details": details_text
        }

    except aiohttp.ClientError as e:
        return {"error": f"ไม่สามารถเชื่อมต่อกับ API หรือเว็บไซต์ได้: {e}"}
    except Exception as e:
        return {"error": f"เกิดข้อผิดพลาด: {e}"}
    
#MurderMystety
async def fetch_murder_stats(player_name):
    api_url = f"https://api.playhive.com/v0/game/all/murder/{player_name}"
    profile_url = f"https://hivebe.link/p/{player_name}"

    try:
        # ดึงข้อมูลจาก API
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as api_response:
                if api_response.status == 200:
                    api_data = await api_response.json()
                else:
                    return {"error": f"ไม่สามารถดึงข้อมูลจาก API ได้ (สถานะ: {api_response.status})"}

            # ดึง HTML ของโปรไฟล์
            async with session.get(profile_url) as profile_response:
                profile_response.raise_for_status()
                html = await profile_response.text()

        soup = BeautifulSoup(html, 'html.parser')

        # ดึง URL รูปภาพ
        img_tag = soup.find("img", class_="object-contain")
        img_url = f"https://playhive.com{img_tag['src']}" if img_tag else "https://via.placeholder.com/150"

        # ดึงรายละเอียดเพิ่มเติม
        details_tag = soup.find("p", class_="text-shadow-sm text-shadow-black flex items-center pt-1 text-xl font-medium leading-5 text-white")
        details_text = details_tag.text.strip() if details_tag else "ไม่ได้ระบุฉายาไว้"

        # ดึงชื่อผู้เล่น
        player_name_tag = soup.find("h1", class_="text-shadow-lg text-shadow-black text-4xl font-semibold text-white md:text-6xl")
        player_name_text = player_name_tag.text.strip() if player_name_tag else "ไม่พบชื่อผู้เล่น"

        # เช็คยศพิเศษ
        special_rank_tag = soup.find("div", class_="text-shadow-sm")
        if special_rank_tag and "plus" in special_rank_tag.get("class", []):
            player_name_text += " ✨"  # เพิ่มอิโมจิเมื่อมียศพิเศษ

        # จัดรูปแบบข้อมูลที่ได้จาก API
        first_played_timestamp = api_data.get("first_played", 0)
        if first_played_timestamp:
            # แปลง Unix timestamp เป็น UTC
            first_played_utc = datetime.utcfromtimestamp(first_played_timestamp)
            # ปรับเวลาให้เป็น UTC+7 (เวลาของประเทศไทย)
            first_played_utc7 = first_played_utc + timedelta(hours=7)
            first_played = first_played_utc7.strftime('%Y-%m-%d %H:%M:%S')
        else:
            first_played = "ไม่พบข้อมูล"

        kills = api_data.get("murders", 0)
        deaths = api_data.get("deaths", 0)
        games_played = api_data.get("played", 0)
        victories = api_data.get("victories", 0)

        # คำนวณเลเวลจาก XP
        xp = api_data.get("xp", 0)
        level = xp_to_level(xp)

        # คำนวณอัตราการชนะ
        win_rate = (victories / games_played * 100) if games_played > 0 else 0

        stats = {
            "เกมที่เล่นไปแล้ว": games_played,
            "เกมที่ชนะ": victories,
            "อัตราการชนะ": f"{win_rate:.2f}%",
            "จำนวนการตาย": deaths,
            "จำนวนเหรียญที่เก็บได้": api_data.get("coins", 0),
            "จำนวนการฆ่า": kills,
            "กำจัดฆาตกรไปแล้ว": api_data.get("murderer_eliminations", 0),
            "XP": f"{xp} (LV.{level})",
            "เริ่มเล่นครั้งแรกเมื่อ": first_played,
        }

        # ส่งข้อมูลกลับ
        return {
            "player_name": player_name_text,
            "avatar_url": img_url,
            "stats": stats,
            "details": details_text
        }

    except aiohttp.ClientError as e:
        return {"error": f"ไม่สามารถเชื่อมต่อกับ API หรือเว็บไซต์ได้: {e}"}
    except Exception as e:
        return {"error": f"เกิดข้อผิดพลาด: {e}"}
    
#Deathrun
async def fetch_deathrun_stats(player_name):
    api_url = f"https://api.playhive.com/v0/game/all/dr/{player_name}"
    profile_url = f"https://hivebe.link/p/{player_name}"

    try:
        # ดึงข้อมูลจาก API
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as api_response:
                if api_response.status == 200:
                    api_data = await api_response.json()
                else:
                    return {"error": f"ไม่สามารถดึงข้อมูลจาก API ได้ (สถานะ: {api_response.status})"}

            # ดึง HTML ของโปรไฟล์
            async with session.get(profile_url) as profile_response:
                profile_response.raise_for_status()
                html = await profile_response.text()

        soup = BeautifulSoup(html, 'html.parser')

        # ดึง URL รูปภาพ
        img_tag = soup.find("img", class_="object-contain")
        img_url = f"https://playhive.com{img_tag['src']}" if img_tag else "https://via.placeholder.com/150"

        # ดึงรายละเอียดเพิ่มเติม
        details_tag = soup.find("p", class_="text-shadow-sm text-shadow-black flex items-center pt-1 text-xl font-medium leading-5 text-white")
        details_text = details_tag.text.strip() if details_tag else "ไม่ได้ระบุฉายาไว้"

        # ดึงชื่อผู้เล่น
        player_name_tag = soup.find("h1", class_="text-shadow-lg text-shadow-black text-4xl font-semibold text-white md:text-6xl")
        player_name_text = player_name_tag.text.strip() if player_name_tag else "ไม่พบชื่อผู้เล่น"

        # เช็คยศพิเศษ
        special_rank_tag = soup.find("div", class_="text-shadow-sm")
        if special_rank_tag and "plus" in special_rank_tag.get("class", []):
            player_name_text += " ✨"  # เพิ่มอิโมจิเมื่อมียศพิเศษ

        # จัดรูปแบบข้อมูลที่ได้จาก API
        first_played_timestamp = api_data.get("first_played", 0)
        if first_played_timestamp:
            # แปลง Unix timestamp เป็น UTC
            first_played_utc = datetime.utcfromtimestamp(first_played_timestamp)
            # ปรับเวลาให้เป็น UTC+7 (เวลาของประเทศไทย)
            first_played_utc7 = first_played_utc + timedelta(hours=7)
            first_played = first_played_utc7.strftime('%Y-%m-%d %H:%M:%S')
        else:
            first_played = "ไม่พบข้อมูล"

        kills = api_data.get("kills", 0)
        deaths = api_data.get("deaths", 0)
        games_played = api_data.get("played", 0)
        victories = api_data.get("victories", 0)

        # คำนวณเลเวลจาก XP
        xp = api_data.get("xp", 0)
        level = xp_to_level(xp)

        # คำนวณอัตราการชนะ
        win_rate = (victories / games_played * 100) if games_played > 0 else 0

        stats = {
            "เกมที่เล่นไปแล้ว": games_played,
            "เกมที่ชนะ": victories,
            "อัตราการชนะ": f"{win_rate:.2f}%",
            "จำนวนที่ฆ่า": kills,
            "จำนวนการตาย": deaths,
            "Checkpoints": api_data.get("checkpoints", 0),
            "ใช้งานกับดักไปแล้ว": api_data.get("activated", 0),
            "XP": f"{xp} (LV.{level})",
            "เริ่มเล่นครั้งแรกเมื่อ": first_played,
        }

        # ส่งข้อมูลกลับ
        return {
            "player_name": player_name_text,
            "avatar_url": img_url,
            "stats": stats,
            "details": details_text
        }

    except aiohttp.ClientError as e:
        return {"error": f"ไม่สามารถเชื่อมต่อกับ API หรือเว็บไซต์ได้: {e}"}
    except Exception as e:
        return {"error": f"เกิดข้อผิดพลาด: {e}"}

#SuvivalGames
async def fetch_survivalgame_stats(player_name):
    api_url = f"https://api.playhive.com/v0/game/all/sg/{player_name}"
    profile_url = f"https://hivebe.link/p/{player_name}"

    try:
        # ดึงข้อมูลจาก API
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as api_response:
                if api_response.status == 200:
                    api_data = await api_response.json()
                else:
                    return {"error": f"ไม่สามารถดึงข้อมูลจาก API ได้ (สถานะ: {api_response.status})"}

            # ดึง HTML ของโปรไฟล์
            async with session.get(profile_url) as profile_response:
                profile_response.raise_for_status()
                html = await profile_response.text()

        soup = BeautifulSoup(html, 'html.parser')

        # ดึง URL รูปภาพ
        img_tag = soup.find("img", class_="object-contain")
        img_url = f"https://playhive.com{img_tag['src']}" if img_tag else "https://via.placeholder.com/150"

        # ดึงรายละเอียดเพิ่มเติม
        details_tag = soup.find("p", class_="text-shadow-sm text-shadow-black flex items-center pt-1 text-xl font-medium leading-5 text-white")
        details_text = details_tag.text.strip() if details_tag else "ไม่ได้ระบุฉายาไว้"

        # ดึงชื่อผู้เล่น
        player_name_tag = soup.find("h1", class_="text-shadow-lg text-shadow-black text-4xl font-semibold text-white md:text-6xl")
        player_name_text = player_name_tag.text.strip() if player_name_tag else "ไม่พบชื่อผู้เล่น"

        # เช็คยศพิเศษ
        special_rank_tag = soup.find("div", class_="text-shadow-sm")
        if special_rank_tag and "plus" in special_rank_tag.get("class", []):
            player_name_text += " ✨"  # เพิ่มอิโมจิเมื่อมียศพิเศษ

        # จัดรูปแบบข้อมูลที่ได้จาก API
        first_played_timestamp = api_data.get("first_played", 0)
        if first_played_timestamp:
            # แปลง Unix timestamp เป็น UTC
            first_played_utc = datetime.utcfromtimestamp(first_played_timestamp)
            # ปรับเวลาให้เป็น UTC+7 (เวลาของประเทศไทย)
            first_played_utc7 = first_played_utc + timedelta(hours=7)
            first_played = first_played_utc7.strftime('%Y-%m-%d %H:%M:%S')
        else:
            first_played = "ไม่พบข้อมูล"

        kills = api_data.get("kills", 0)
        deaths = api_data.get("deaths", 0)
        games_played = api_data.get("played", 0)
        victories = api_data.get("victories", 0)

        # คำนวณ K/D (Kill/Death ratio)
        kd_ratio = kills / deaths if deaths > 0 else kills  # ถ้าจำนวนการตายเป็น 0 ให้ค่าเป็นจำนวนการฆ่า (ไม่ตาย)

        # คำนวณเลเวลจาก XP
        xp = api_data.get("xp", 0)
        level = xp_to_level(xp)

        # คำนวณจำนวนการฆ่าต่อเกม
        kills_per_game = kills / games_played if games_played > 0 else 0

        # คำนวณอัตราการชนะ
        win_rate = (victories / games_played * 100) if games_played > 0 else 0

        # วิเคราะห์สไตล์การเล่น
        if kd_ratio > 2.0 and kills_per_game > 3.0:
            play_style = "เน้นการรุก"
        elif kd_ratio > 1.0 and win_rate > 50:
            play_style = "เน้นเอาตัวรอด"
        elif kd_ratio >= 1.5 and kd_ratio <= 2.5 and 40 <= win_rate <= 60:
            play_style = "สมดุล"
        elif win_rate > 60:
            play_style = "เน้นเป้าหมาย"
        else:
            play_style = "ไม่มีสไตล์การเล่นที่โดดเด่น"

        stats = {
            "เกมที่เล่นไปแล้ว": games_played,
            "เกมที่ชนะ": victories,
            "อัตราการชนะ": f"{win_rate:.2f}%",
            "จำนวนฆ่า": kills,
            "จำนวนการตาย": deaths,
            "K/D": f"{kd_ratio:.2f}",
            "จำนวนฆ่าต่อเกม": f"{kills_per_game:.2f}",
            "จำนวนกล่องที่เปิด": api_data.get("crates", 0),
            "สู้ใน Deathmatch": api_data.get("deathmatches", 0),
            "พบวัวนำโชค": api_data.get("cows", 0),
            "ใช้จุด TP": api_data.get("teleporters_used", 0),
            "เหยียบแป้นโดด": api_data.get("launchpads_used", 0),
            "ยิงพลุไปแล้ว": api_data.get("flares_used", 0),
            "XP": f"{xp} (LV.{level})",
            "เริ่มเล่นครั้งแรกเมื่อ": first_played,
            "สไตล์การเล่น": play_style  # เพิ่มข้อมูลสไตล์การเล่น
        }

        # ส่งข้อมูลกลับ
        return {
            "player_name": player_name_text,
            "avatar_url": img_url,
            "stats": stats,
            "details": details_text
        }

    except aiohttp.ClientError as e:
        return {"error": f"ไม่สามารถเชื่อมต่อกับ API หรือเว็บไซต์ได้: {e}"}
    except Exception as e:
        return {"error": f"เกิดข้อผิดพลาด: {e}"}

#CaptureTheFlag
async def fetch_capturetheflag_stats(player_name):
    api_url = f"https://api.playhive.com/v0/game/all/ctf/{player_name}"
    profile_url = f"https://hivebe.link/p/{player_name}"

    try:
        # ดึงข้อมูลจาก API
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as api_response:
                if api_response.status == 200:
                    api_data = await api_response.json()
                else:
                    return {"error": f"ไม่สามารถดึงข้อมูลจาก API ได้ (สถานะ: {api_response.status})"}

            # ดึง HTML ของโปรไฟล์
            async with session.get(profile_url) as profile_response:
                profile_response.raise_for_status()
                html = await profile_response.text()

        soup = BeautifulSoup(html, 'html.parser')

        # ดึง URL รูปภาพ
        img_tag = soup.find("img", class_="object-contain")
        img_url = f"https://playhive.com{img_tag['src']}" if img_tag else "https://via.placeholder.com/150"

        # ดึงรายละเอียดเพิ่มเติม
        details_tag = soup.find("p", class_="text-shadow-sm text-shadow-black flex items-center pt-1 text-xl font-medium leading-5 text-white")
        details_text = details_tag.text.strip() if details_tag else "ไม่ได้ระบุฉายาไว้"

        # ดึงชื่อผู้เล่น
        player_name_tag = soup.find("h1", class_="text-shadow-lg text-shadow-black text-4xl font-semibold text-white md:text-6xl")
        player_name_text = player_name_tag.text.strip() if player_name_tag else "ไม่พบชื่อผู้เล่น"

        # เช็คยศพิเศษ
        special_rank_tag = soup.find("div", class_="text-shadow-sm")
        if special_rank_tag and "plus" in special_rank_tag.get("class", []):
            player_name_text += " ✨"  # เพิ่มอิโมจิเมื่อมียศพิเศษ

        # จัดรูปแบบข้อมูลที่ได้จาก API
        first_played_timestamp = api_data.get("first_played", 0)
        if first_played_timestamp:
            # แปลง Unix timestamp เป็น UTC
            first_played_utc = datetime.utcfromtimestamp(first_played_timestamp)
            # ปรับเวลาให้เป็น UTC+7 (เวลาของประเทศไทย)
            first_played_utc7 = first_played_utc + timedelta(hours=7)
            first_played = first_played_utc7.strftime('%Y-%m-%d %H:%M:%S')
        else:
            first_played = "ไม่พบข้อมูล"

        kills = api_data.get("kills", 0)
        deaths = api_data.get("deaths", 0)
        games_played = api_data.get("played", 0)
        victories = api_data.get("victories", 0)

        # คำนวณ K/D (Kill/Death ratio)
        kd_ratio = kills / deaths if deaths > 0 else kills  # ถ้าจำนวนการตายเป็น 0 ให้ค่าเป็นจำนวนการฆ่า (ไม่ตาย)

        # คำนวณเลเวลจาก XP
        xp = api_data.get("xp", 0)
        level = xp_to_level(xp)

        # คำนวณจำนวนการฆ่าต่อเกม
        kills_per_game = kills / games_played if games_played > 0 else 0

        # คำนวณอัตราการชนะ
        win_rate = (victories / games_played * 100) if games_played > 0 else 0

        # วิเคราะห์สไตล์การเล่น
        if kd_ratio > 2.0 and kills_per_game > 3.0:
            play_style = "เน้นการรุก"
        elif kd_ratio > 1.0 and win_rate > 50:
            play_style = "เน้นเอาตัวรอด"
        elif kd_ratio >= 1.5 and kd_ratio <= 2.5 and 40 <= win_rate <= 60:
            play_style = "สมดุล"
        elif win_rate > 60:
            play_style = "เน้นเป้าหมาย"
        else:
            play_style = "ไม่มีสไตล์การเล่นที่โดดเด่น"

        stats = {
            "เกมที่เล่นไปแล้ว": games_played,
            "เกมที่ชนะ": victories,
            "อัตราการชนะ": f"{win_rate:.2f}%",
            "จำนวนฆ่า": kills,
            "จำนวนการตาย": deaths,
            "K/D": f"{kd_ratio:.2f}",
            "จำนวนฆ่าต่อเกม": f"{kills_per_game:.2f}",
            "Assist": api_data.get("assists", 0),
            "ขโมยธงจากอีกฝั่ง": api_data.get("flags_captured", 0),
            "นำธงกลับฐาน": api_data.get("flags_returned", 0),
            "XP": f"{xp} (LV.{level})",
            "เริ่มเล่นครั้งแรกเมื่อ": first_played,
            "สไตล์การเล่น": play_style  # เพิ่มข้อมูลสไตล์การเล่น
        }

        # ส่งข้อมูลกลับ
        return {
            "player_name": player_name_text,
            "avatar_url": img_url,
            "stats": stats,
            "details": details_text
        }

    except aiohttp.ClientError as e:
        return {"error": f"ไม่สามารถเชื่อมต่อกับ API หรือเว็บไซต์ได้: {e}"}
    except Exception as e:
        return {"error": f"เกิดข้อผิดพลาด: {e}"}
    
#BuildBattle
async def fetch_justbuild_stats(player_name):
    api_url = f"https://api.playhive.com/v0/game/all/build/{player_name}"
    profile_url = f"https://hivebe.link/p/{player_name}"

    try:
        # ดึงข้อมูลจาก API
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as api_response:
                if api_response.status == 200:
                    api_data = await api_response.json()
                else:
                    return {"error": f"ไม่สามารถดึงข้อมูลจาก API ได้ (สถานะ: {api_response.status})"}

            # ดึง HTML ของโปรไฟล์
            async with session.get(profile_url) as profile_response:
                profile_response.raise_for_status()
                html = await profile_response.text()

        soup = BeautifulSoup(html, 'html.parser')

        # ดึง URL รูปภาพ
        img_tag = soup.find("img", class_="object-contain")
        img_url = f"https://playhive.com{img_tag['src']}" if img_tag else "https://via.placeholder.com/150"

        # ดึงรายละเอียดเพิ่มเติม
        details_tag = soup.find("p", class_="text-shadow-sm text-shadow-black flex items-center pt-1 text-xl font-medium leading-5 text-white")
        details_text = details_tag.text.strip() if details_tag else "ไม่ได้ระบุฉายาไว้"

        # ดึงชื่อผู้เล่น
        player_name_tag = soup.find("h1", class_="text-shadow-lg text-shadow-black text-4xl font-semibold text-white md:text-6xl")
        player_name_text = player_name_tag.text.strip() if player_name_tag else "ไม่พบชื่อผู้เล่น"

        # เช็คยศพิเศษ
        special_rank_tag = soup.find("div", class_="text-shadow-sm")
        if special_rank_tag and "plus" in special_rank_tag.get("class", []):
            player_name_text += " ✨"  # เพิ่มอิโมจิเมื่อมียศพิเศษ

        # จัดรูปแบบข้อมูลที่ได้จาก API
        first_played_timestamp = api_data.get("first_played", 0)
        if first_played_timestamp:
            # แปลง Unix timestamp เป็น UTC
            first_played_utc = datetime.utcfromtimestamp(first_played_timestamp)
            # ปรับเวลาให้เป็น UTC+7 (เวลาของประเทศไทย)
            first_played_utc7 = first_played_utc + timedelta(hours=7)
            first_played = first_played_utc7.strftime('%Y-%m-%d %H:%M:%S')
        else:
            first_played = "ไม่พบข้อมูล"

        # คำนวณเลเวลจาก XP
        xp = api_data.get("xp", 0)
        level = xp_to_level(xp)
        
        games_played = api_data.get("played", 0)
        victories = api_data.get("victories", 0)

        # คำนวณอัตราการชนะ
        win_rate = (victories / games_played * 100) if games_played > 0 else 0

        ratings = {
            "Meh": api_data.get("rating_meh_received"),
            "Okay": api_data.get("rating_okay_received"),
            "Good": api_data.get("rating_good_received"),
            "Great": api_data.get("rating_great_received"),
            "Love": api_data.get("rating_love_received")
        }
        
        # สร้างตารางสำหรับแสดงผลการโหวต
        rating_table = "ประเภทการโหวต | จำนวนครั้ง \n"
        rating_table += "\n".join(f"{key: <12} | {value}" for key, value in ratings.items())
        rating_blocks = f"```\n{rating_table}\n```"

        stats = {
            "เกมที่เล่นไปแล้ว": games_played,
            "เกมที่ชนะ": victories,
            "อัตราการชนะ": f"{win_rate:.2f}%",
            "ผลการโหวตที่เคยได้รับ": rating_blocks,
            "XP": f"{xp} (LV.{level})",
            "เล่นครั้งแรกเมื่อ": first_played
        }
        
        
        # ส่งข้อมูลกลับ
        return {
            "player_name": player_name_text,
            "avatar_url": img_url,
            "stats": stats,
            "details": details_text
        }

    except aiohttp.ClientError as e:
        return {"error": f"ไม่สามารถเชื่อมต่อกับ API หรือเว็บไซต์ได้: {e}"}
    except Exception as e:
        return {"error": f"เกิดข้อผิดพลาด: {e}"}
    