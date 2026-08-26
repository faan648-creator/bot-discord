import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import discord
from discord import app_commands
from discord.ext import commands

# ==========================================
# 1. TRIK FAKE WEB SERVER (UNTUK LOLOS PORT RENDER)
# ==========================================
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot Discord is alive!")

def run_web_server():
    port = int(os.getenv("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    print(f"Fake web server running on port {port}")
    server.serve_forever()

web_thread = threading.Thread(target=run_web_server)
web_thread.daemon = True
web_thread.start()

# ==========================================
# 2. KONFIGURASI BOT DISCORD
# ==========================================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ID Pesan list utama yang mau diedit otomatis (tetap pakai ID pesan listnya)
LIST_MESSAGE_ID = 987654321098765432  

@bot.event
async def on_ready():
    print(f"Bot Discord {bot.user} sudah aktif dan online!")
    try:
        synced = await bot.tree.sync()
        print(f"Berhasil mensinkronkan {len(synced)} global slash commands.")
    except Exception as e:
        print(f"Gagal sinkronisasi command: {e}")

# ==========================================
# 3. SLASH COMMAND: /done
# ==========================================
@bot.tree.command(name="done", description="Mengisi slot list rekap Fish It X8 secara otomatis")
@app_commands.describe(
    slot_number="Nomor slot yang ingin diisi (contoh: 1, 2, dst)",
    roblox_usn="Username / Nick Roblox buyer"
)
async def done(interaction: discord.Interaction, slot_number: int, roblox_usn: str):
    await interaction.response.defer(ephemeral=True)

    # Bot otomatis mencari channel berdasarkan nama "ptpt-x8" di server ini
    target_channel_name = "ptpt-x8"
    rekap_channel = discord.utils.get(interaction.guild.text_channels, name=target_channel_name)
    
    if not rekap_channel:
        await interaction.followup.send(
            f"⚠️ Channel dengan nama **#{target_channel_name}** tidak ditemukan di server ini!",
            ephemeral=True
        )
        return

    try:
        # Ambil pesan list utama berdasarkan ID Message dari channel ptpt-x8
        msg = await rekap_channel.fetch_message(1537343199348006993)
    except discord.NotFound:
        await interaction.followup.send(
            f"⚠️ Pesan list utama tidak ditemukan di channel #{target_channel_name}! Pastikan LIST_MESSAGE_ID benar.",
            ephemeral=True
        )
        return

    # Ambil teks asli dari pesan list
    current_content = msg.content
    lines = current_content.split("\n")
    updated_lines = []
    found = False

    # Cari baris yang sesuai dengan nomor slot yang mau diisi
    for line in lines:
        if line.strip().startswith(f"{slot_number}."):
            updated_lines.append(f"{slot_number}. {roblox_usn} ✅")
            found = True
        else:
            updated_lines.append(line)

    if found:
        new_content = "\n".join(updated_lines)
        # Edit pesan list di channel ptpt-x8 secara otomatis
        await msg.edit(content=new_content)
        await interaction.followup.send(
            f"✅ Slot nomor **{slot_number}** berhasil diisi oleh **{roblox_usn}** di channel **#{target_channel_name}**!",
            ephemeral=True
        )
    else:
        await interaction.followup.send(
            f"⚠️ Slot nomor {slot_number} tidak ditemukan dalam format list!",
            ephemeral=True
        )

# Jalankan Bot
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not TOKEN:
    print("⚠️ ERROR: Token bot Discord tidak ditemukan!")
else:
    bot.run(TOKEN)
