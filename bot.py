import os
import discord
from discord import app_commands
from discord.ext import commands

# Konfigurasi Bot Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ==========================================
# KONFIGURASI ID SERVER & CHANNEL
# ==========================================
# Ganti angka di bawah dengan ID asli dari server Discord lu
REKAP_CHANNEL_ID = (  # Ganti dengan ID Channel tempat list rekap berada
    1440987640232017941
)
LIST_MESSAGE_ID = 1440987640232017941  # Ganti dengan ID Pesan list utama


@bot.event
async def on_ready():
  print(f"Bot Discord {bot.user} sudah aktif dan online!")
  try:
    # Sinkronisasi global agar command /done bisa muncul di semua channel
    synced = await bot.tree.sync()
    print(f"Berhasil mensinkronkan {len(synced)} global slash commands.")
  except Exception as e:
    print(f"Gagal sinkronisasi command: {e}")


# ==========================================
# SLASH COMMAND: /done (UNTUK ISI LIST OTOMATIS)
# ==========================================
@bot.tree.command(
    name="done", description="Mengisi slot list rekap Fish It X8 secara otomatis"
)
@app_commands.describe(
    slot_number="Nomor slot yang ingin diisi (contoh: 1, 2, dst)",
    roblox_usn="Username / Nick Roblox buyer",
)
async def done(
    interaction: discord.Interaction, slot_number: int, roblox_usn: str
):
  # Kirim response awal (deferred) agar bot punya waktu proses tanpa timeout
  await interaction.response.defer(ephemeral=True)

  rekap_channel = interaction.guild.get_channel(REKAP_CHANNEL_ID)
  if not rekap_channel:
    await interaction.followup.send(
        "⚠️ Channel rekap tidak ditemukan! Cek kembali REKAP_CHANNEL_ID.",
        ephemeral=True,
    )
    return

  try:
    # Ambil pesan list utama berdasarkan ID Message
    msg = await rekap_channel.fetch_message(LIST_MESSAGE_ID)
  except discord.NotFound:
    await interaction.followup.send(
        "⚠️ Pesan list utama tidak ditemukan! Pastikan LIST_MESSAGE_ID benar.",
        ephemeral=True,
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
      # Ganti baris dengan USN Roblox baru + centang hijau
      updated_lines.append(f"{slot_number}. {roblox_usn} ✅")
      found = True
    else:
      updated_lines.append(line)

  if found:
    new_content = "\n".join(updated_lines)
    # Edit pesan asli di Discord secara otomatis
    await msg.edit(content=new_content)
    await interaction.followup.send(
        f"✅ Slot nomor **{slot_number}** berhasil diisi oleh **{roblox_usn}**"
        f" dengan centang hijau!",
        ephemeral=True,
    )
  else:
    await interaction.followup.send(
        f"⚠️ Slot nomor {slot_number} tidak ditemukan dalam format list!",
        ephemeral=True,
    )


# Ambil Token dari Environment Variable Render (Supaya Aman)
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not TOKEN:
  print("⚠️ ERROR: Token bot Discord tidak ditemukan di Environment Variables!")
else:
  bot.run(TOKEN)
