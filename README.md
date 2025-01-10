# HiveMC Stats Discord Bot

บอท Discord ที่ดึงและแสดงสถิติผู้เล่นจาก HiveMC สำหรับเกมต่างๆ เช่น Skywars, Bedwars, Murder Mystery, Deathrun, Survival Games, Capture The Flag, และ Build Battle

## Note
- จะมีการเพิ่มคุณสมบัติสำหรับการเปรียบเทียบระหว่างผู้เล่น 2 คน โดยอ้างอิงข้อมูลจาก API และ Minigame เพิ่มเติมในอนาคต
  
## คุณสมบัติ

![alt text](https://github.com/beamkungza1234/Hivestats/blob/main/Hivestats.png?raw=true)

- ดึงสถิติผู้เล่นสำหรับเกมต่างๆ บน HiveMC
- แสดงสถิติเพิ่มเติม เช่น login streak และ quests completed
- ให้ข้อมูลผู้เล่นอย่างละเอียด รวมถึง avatar, สถิติการเล่นเกม, และสไตล์การเล่น

## ข้อกำหนดเบื้องต้น

- Python 3.8+
- Discord bot token
- HiveMC API access

## การติดตั้ง

1. คัดลอก Repo มา:
    ```sh
    git clone https://github.com/beamkungza1234/Hivestats.git
    cd Hivestats
    ```

2. ติดตั้งไลบารี่ที่จำเป็น:
    ```sh
    pip install -r requirements.txt
    ```

3. สร้าง [.env](http://_vscodecontentref_/0) และใส่โทเค็นบอทของคุณลงไป:
    ```env
    DISCORD_BOT_SECRET=your_discord_bot_token
    ```

## การใช้งาน

1. เปิดใช้งาน:
    ```sh
    python main.py
    ```

2. ใช้คำสั่ง `/hivestats` ในดิสคอร์ดของคุณเพื่อดึงข้อมูลผู้เล่นมา:
    ```sh
    /hivestats game:<game_name> player_name:<player_name>
    ```

## โครงสร้างไฟล์

- [main.py](http://_vscodecontentref_/1): สคริปต์หลักของบอทที่จัดการคำสั่งและการโต้ตอบของ Discord bot
- [getstats.py](http://_vscodecontentref_/2): มีฟังก์ชันสำหรับดึงสถิติผู้เล่นจาก HiveMC
- [.env](http://_vscodecontentref_/3): ไฟล์ environment สำหรับเก็บ Discord bot token ของคุณ
- [.gitignore](http://_vscodecontentref_/4): ระบุไฟล์และไดเรกทอรีที่จะถูกละเว้นโดย Git

## ฟังก์ชัน

### [main.py](http://_vscodecontentref_/5)

- [hivestats(interaction, game, player_name)](http://_vscodecontentref_/6): จัดการคำสั่ง `/hivestats` เพื่อดึงและแสดงสถิติผู้เล่น


## การมีส่วนร่วม

ยินดีต้อนรับการมีส่วนร่วม! โปรดเปิด issue หรือส่ง pull request สำหรับการเปลี่ยนแปลงใดๆ

## ขอบคุณ

- [Nextcord](https://github.com/nextcord/nextcord) สำหรับ Discord API wrapper
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) สำหรับการ web scraping
- [Aiohttp](https://docs.aiohttp.org/en/stable/) สำหรับการร้องขอ HTTP แบบ asynchronous
