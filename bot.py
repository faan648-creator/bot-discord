import asyncio
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
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

  def do_HEAD(self):
    self.send_response(200)
    self.end_headers()


def run_web_server():
  port = int(os.getenv("PORT", 10000))
  server = HTTPServer(("0.0.0.0", port), SimpleHandler)
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
intents.members = True  # Wajib diaktifkan untuk event member join/remove

bot = commands.Bot(command_prefix="!", intents=intents)

# ID Pesan list utama yang mau diedit otomatis (untuk command /done)
LIST_MESSAGE_ID = int(os.getenv("LIST_MESSAGE_ID")

# Konfigurasi Channel ID untuk Welcome & Goodbye (Ganti dengan ID Channel tujuan)
WELCOME_CHANNEL_ID = (
    123456789012345678  # Sesuaikan dengan ID channel sambutan di server kamu
)
GOODBYE_CHANNEL_ID = (
    123456789012345678  # Bisa disamakan atau dibedakan dengan channel welcome
)


@bot.event
async def on_ready():
  print(f"Bot Discord {bot.user} sudah aktif dan online!")
  try:
    synced = await bot.tree.sync()
    print(f"Berhasil mensinkronkan {len(synced)} global slash commands.")
  except Exception as e:
    print(f"Gagal sinkronisasi command: {e}")


# ==========================================
# 3. FITUR WELCOME & GOODBYE (INTERAKTIF & MENARIK)
# ==========================================


@bot.event
async def on_member_join(member):
  channel = member.guild.get_channel(WELCOME_CHANNEL_ID)
  if not channel:
    return

  embed = discord.Embed(
      title="🎉 WELCOME TO THE SERVER! 🎉",
      description=(
          f"Halo {member.mention}, selamat datang di **{member.guild.name}**!\n\n"
          "✨ *Selamat Datang Di Server Kesayangan Talon.*\n"
          "📜 Jangan lupa untuk membaca rules/peraturan server, ya!\n"
          
      ),
      color=discord.Color.green(),
  )
  # Menampilkan foto profil member sebagai thumbnail dan banner besar (image)
  embed.set_thumbnail(url=member.display_avatar.url)
  embed.set_image(url=member.display_avatar.url)
  embed.set_footer(
      text=f"Member ke-{member.guild.member_count} | ID: {member.id}",
      icon_url=member.guild.icon.url if member.guild.icon else None,
  )
  embed.timestamp = discord.utils.utcnow()

  await channel.send(
      content=f"👋 Selamat datang, {member.mention}!", embed=embed
  )


@bot.event
async def on_member_remove(member):
  channel = member.guild.get_channel(GOODBYE_CHANNEL_ID)
  if not channel:
    return

  embed = discord.Embed(
      title="😢 GOODBYE...",
      description=(
          f"**{member.name}** (`{member.id}`) telah meninggalkan server.\n\n"
          "👋 *Selamat Jalan.*"
          " Semoga kita bisa berjumpa lagi di lain kesempatan!"
      ),
      color=discord.Color.red(),
  )
  # Menampilkan foto profil member yang keluar
  embed.set_thumbnail(url=member.display_avatar.url)
  embed.set_footer(
      text=f"Sisa member: {member.guild.member_count}",
      icon_url=member.guild.icon.url if member.guild.icon else None,
  )
  embed.timestamp = discord.utils.utcnow()

  await channel.send(embed=embed)


# ==========================================
# 4. INTERACTIVE VIEWS & COMPONENTS
# ==========================================


# View untuk Tombol Metode Pembayaran
class PaymentView(discord.ui.View):

  def __init__(self):
    super().__init__(timeout=None)

  @discord.ui.button(label="QRIS", style=discord.ButtonStyle.green, emoji="🪪")
  async def qris_button(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    qris_url = os.getenv("QRIS_IMAGE_URL", "https://link-default-gambar.com")
    await interaction.response.send_message(
        f"📌 {interaction.user.mention} memilih metode pembayaran **QRIS**:\n"
        f"Silakan scan QR Code di bawah ini:\n{qris_url}\n\n"
        f"*(Harap kirimkan bukti transfer & username Roblox jika sudah"
        " melakukan pembayaran!)*"
    )

  @discord.ui.button(label="DANA", style=discord.ButtonStyle.primary, emoji="💳")
  async def dana_button(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    number = os.getenv("DANA_NUMBER", "08xxxxxxxxxx")
    name = os.getenv("DANA_NAME", "Nama Pemilik")
    await interaction.response.send_message(
        f"📌 {interaction.user.mention} memilih metode pembayaran **DANA**:\n"
        f"• Nomor: `{number}`\n"
        f"• Atas Nama: `{name}`\n\n"
        f"*(Harap kirimkan bukti transfer & username Roblox jika sudah"
        " melakukan pembayaran!)*"
    )

  @discord.ui.button(
      label="GOPAY", style=discord.ButtonStyle.blurple, emoji="💳"
  )
  async def gopay_button(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    number = os.getenv("GOPAY_NUMBER", "08xxxxxxxxxx")
    name = os.getenv("GOPAY_NAME", "Nama Pemilik")
    await interaction.response.send_message(
        f"📌 {interaction.user.mention} memilih metode pembayaran **GOPAY**:\n"
        f"• Nomor: `{number}`\n"
        f"• Atas Nama: `{name}`\n\n"
        f"*(Harap kirimkan bukti transfer & username Roblox jika sudah"
        " melakukan pembayaran!)*"
    )

  @discord.ui.button(
      label="ShopeePay", style=discord.ButtonStyle.danger, emoji="💳"
  )
  async def shopeepay_button(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    number = os.getenv("SHOPEEPAY_NUMBER", "08xxxxxxxxxx")
    name = os.getenv("SHOPEEPAY_NAME", "Nama Pemilik")
    await interaction.response.send_message(
        f"📌 {interaction.user.mention} memilih metode pembayaran"
        f" **ShopeePay**:\n"
        f"• Nomor: `{number}`\n"
        f"• Atas Nama: `{name}`\n\n"
        f"*(Harap kirimkan bukti transfer & username Roblox jika sudah"
        " melakukan pembayaran!)*"
    )


# Tombol Close khusus Admin dengan auto-delete 5 detik
class CloseTicketButton(discord.ui.Button):

  def __init__(self):
    super().__init__(
        label="🔒 Close Ticket",
        style=discord.ButtonStyle.red,
        custom_id="btn_close_ticket",
    )

  async def callback(self, interaction: discord.Interaction):
    if not interaction.user.guild_permissions.manage_channels:
      await interaction.response.send_message(
          "❌ Kamu tidak memiliki izin untuk menutup tiket ini!", ephemeral=True
      )
      return

    await interaction.response.send_message(
        "🔒 Tiket dikonfirmasi ditutup. Channel akan dihapus otomatis dalam"
        " **5 detik**..."
    )

    await asyncio.sleep(5)

    try:
      await interaction.channel.delete()
    except Exception as e:
      print(f"Gagal menghapus channel: {e}")


# View di dalam Tiket SETELAH jumlah akun dipilih (Muncul tombol Payment & Close)
class ActiveTicketView(discord.ui.View):

  def __init__(self):
    super().__init__(timeout=None)
    self.add_item(PaymentButtonSelect())
    self.add_item(CloseTicketButton())


class PaymentButtonSelect(discord.ui.Button):

  def __init__(self):
    super().__init__(
        label="💳 Pilih Metode Pembayaran",
        style=discord.ButtonStyle.blurple,
        custom_id="btn_pay_inside",
    )

  async def callback(self, interaction: discord.Interaction):
    view = PaymentView()
    await interaction.response.send_message(
        "💳 **SILAKAN PILIH METODE PEMBAYARAN DI BAWAH INI:**", view=view
    )


# Dropdown (Select Menu) untuk Memilih Jumlah Akun di dalam Tiket
class SlotSelect(discord.ui.Select):

  def __init__(self):
    options = [
        discord.SelectOption(
            label="1 Akun / Slot",
            value="1",
            description="Total: Rp 14.000",
            emoji="🛒",
        ),
        discord.SelectOption(
            label="2 Akun / Slot",
            value="2",
            description="Total: Rp 28.000",
            emoji="🛒",
        ),
        discord.SelectOption(
            label="3 Akun / Slot",
            value="3",
            description="Total: Rp 42.000",
            emoji="🛒",
        ),
        discord.SelectOption(
            label="4 Akun / Slot",
            value="4",
            description="Total: Rp 56.000",
            emoji="🛒",
        ),
        discord.SelectOption(
            label="5 Akun / Slot",
            value="5",
            description="Total: Rp 70.000",
            emoji="🛒",
        ),
    ]
    super().__init__(
        placeholder="👉 Klik di sini untuk memilih jumlah akun...",
        min_values=1,
        max_values=1,
        options=options,
    )

  async def callback(self, interaction: discord.Interaction):
    total_slot = int(self.values[0])
    harga_per_slot = 14000
    total_harga = total_slot * harga_per_slot

    active_view = ActiveTicketView()
    await interaction.response.edit_message(
        content=(
            f"✅ {interaction.user.mention} memilih **{total_slot} Akun /"
            f" Slot**.\n\n📋 **Rincian Pemesanan:**\n• Jumlah Akun:"
            f" **{total_slot} Slot**\n• Harga per Slot: **Rp"
            f" 14.000**\n• **TOTAL TAGIHAN: Rp {total_harga:,}**\n\n👉 *Silakan"
            " kirimkan Username / Nick Roblox kamu di chat ini sesuai jumlah"
            f" akun yang dipesan.*\n👉 *Lalu klik tombol **Pilih Metode"
            " Pembayaran** di bawah untuk melunasi transaksi.*"
        ),
        view=active_view,
    )


class SlotSelectView(discord.ui.View):

  def __init__(self):
    super().__init__(timeout=None)
    self.add_item(SlotSelect())


# View untuk Tombol Panel Utama (Create Ticket) di channel publik
class TicketCreateView(discord.ui.View):

  def __init__(self):
    super().__init__(timeout=None)

  @discord.ui.button(
      label="📩 Create Ticket",
      style=discord.ButtonStyle.green,
      custom_id="create_ticket_btn",
  )
  async def create_ticket(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    await interaction.response.defer(ephemeral=True)

    guild = interaction.guild
    member = interaction.user

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        member: discord.PermissionOverwrite(
            view_channel=True, send_messages=True, read_message_history=True
        ),
        guild.me: discord.PermissionOverwrite(
            view_channel=True, send_messages=True
        ),
    }

    target_category = interaction.channel.category
    channel_name = f"ticket-{member.name}"

    try:
      ticket_channel = await guild.create_text_channel(
          name=channel_name, overwrites=overwrites, category=target_category
      )
    except Exception as e:
      await interaction.followup.send(
          f"⚠️ Gagal membuat channel tiket: {e}", ephemeral=True
      )
      return

    select_view = SlotSelectView()
    await ticket_channel.send(
        f"Halo {member.mention}! Terima kasih sudah membuka tiket.\n\nSilakan"
        " tentukan **berapa banyak akun / slot** yang ingin kamu beli melalui"
        " menu pilihan di bawah ini:",
        view=select_view,
    )

    await interaction.followup.send(
        f"✅ Tiket kamu berhasil dibuat! Silakan cek channel"
        f" {ticket_channel.mention}",
        ephemeral=True,
    )


# ==========================================
# 5. SLASH COMMANDS
# ==========================================


@bot.tree.command(
    name="setuplist",
    description=(
        "Mengirim pesan list rekap Fish It X8 otomatis ke channel ini"
    ),
)
async def setuplist(interaction: discord.Interaction):
  await interaction.response.defer(ephemeral=True)

  if interaction.channel.name != "ptpt-x8":
    await interaction.followup.send(
        "⚠️ Perintah ini hanya bisa digunakan di channel **#ptpt-x8**!",
        ephemeral=True,
    )
    return

  format_list = (
      "LIST BOOST SERVER FISH IT X8 By <@617248535913693194>"
      " <@785872264100446210>\n\n14k/SLOT\n\nKLOTER 23 ( 24 JAM"
      " )\n\nLIST MENGGUNAKAN Usn & Nick ROBLOX\nContoh : zens1907\n\n1."
      " -\n2. -\n3. -\n4. -\n5. -\n6. -\n7. -\n8. -\n9. -\n10. -\n11."
      " -\n12. -\n13. -\n14. -\n15. -\n16. -\n17. -\n18. -\n19. dmin 2\n20."
      " Admin 1"
  )

  sent_message = await interaction.channel.send(format_list)

  await interaction.followup.send(
      f"✅ Berhasil membuat pesan list Kloter 23!\n\nSalin Message ID di bawah"
      f" ini dan masukkan ke variabel `LIST_MESSAGE_ID` di kodingan"
      f" bot:\n`{sent_message.id}`",
      ephemeral=True,
  )


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
  await interaction.response.defer(ephemeral=True)

  target_channel_name = "ptpt-x8"
  rekap_channel = discord.utils.get(
      interaction.guild.text_channels, name=target_channel_name
  )

  if not rekap_channel:
    await interaction.followup.send(
        f"⚠️ Channel dengan nama **#{target_channel_name}** tidak ditemukan di"
        " server ini!",
        ephemeral=True,
    )
    return

  try:
    msg = await rekap_channel.fetch_message(LIST_MESSAGE_ID)
  except discord.NotFound:
    await interaction.followup.send(
        f"⚠️ Pesan list utama tidak ditemukan di channel #{target_channel_name}!"
        " Pastikan LIST_MESSAGE_ID benar.",
        ephemeral=True,
    )
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
    await interaction.followup.send(
        f"✅ Slot nomor **{slot_number}** berhasil diisi oleh **{roblox_usn}**"
        f" di channel **#{target_channel_name}**!",
        ephemeral=True,
    )
  else:
    await interaction.followup.send(
        f"⚠️ Slot nomor {slot_number} tidak ditemukan dalam format list!",
        ephemeral=True,
    )


@bot.tree.command(
    name="setup-ticket",
    description="Memunculkan panel tombol untuk membuat tiket transaksi",
)
async def setup_ticket(interaction: discord.Interaction):
  await interaction.response.defer(ephemeral=True)

  view = TicketCreateView()
  await interaction.channel.send(
      "🛒 **SILAKAN BUAT TIKET TRANSAKSI**\nKlik tombol di bawah ini untuk"
      " memulai pembelian slot:",
      view=view,
  )
  await interaction.followup.send(
      "✅ Panel Create Ticket berhasil dikirim ke channel ini!", ephemeral=True
  )


# ==========================================
# 6. MENJALANKAN BOT
# ==========================================
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not TOKEN:
  print("⚠️ ERROR: Token bot Discord tidak ditemukan!")
else:
  bot.run(TOKEN)
