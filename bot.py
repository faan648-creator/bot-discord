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
    # Render otomatis nyediain port lewat environment variable PORT
    port = int(os.getenv("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    print(f"Fake web server running on port {port}")
    server.serve_forever()

# Jalankan fake web server di background thread secara paralel
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

# Ganti dengan ID asli dari server Discord lu
REKAP_CHANNEL_ID = 123456789012345678  # ID Channel tempat list rekap berada
LIST_MESSAGE_ID = 987654321098765432   # ID Pesan list utama

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

    rekap_channel = interaction.guild.get_channel(REKAP_CHANNEL_ID)
    if not rekap_channel:
        await interaction.followup.send("⚠️ Channel rekap tidak ditemukan!", ephemeral=True)
        return

    try:
        msg = await rekap_channel.fetch_message(LIST_MESSAGE_ID)
    except discord.NotFound:
        await interaction.followup.send("⚠️ Pesan list utama tidak ditemukan!", ephemeral=True)
        return

    current_content = msg.content
    lines = current_content.split("\n")
    updated_lines = []
    found = False

    for line in lines:
        if line.strip().startswith(f"{slot_number}."):
            updated_lines.append(f"{slot_number}. {roblox_usn} ✅")
            found = True
        else:
            updated_lines.append(line)

    if found:
        new_content = "\n".join(updated_lines)
        await msg.edit(content=new_content)
        await interaction.followup.send(f"✅ Slot nomor **{slot_number}** berhasil diisi oleh **{roblox_usn}**!", ephemeral=True)
    else:
        await interaction.followup.send(f"⚠️ Slot nomor {slot_number} tidak ditemukan!", ephemeral=True)

# Jalankan Bot
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not TOKEN:
    print("⚠️ ERROR: Token bot Discord tidak ditemukan!")
else:
    bot.run(TOKEN)
