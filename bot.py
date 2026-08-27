import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import asyncio
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

# ID Pesan list utama yang mau diedit otomatis (untuk command /done)
LIST_MESSAGE_ID = 1542521523095740426  

@bot.event
async def on_ready():
    print(f"Bot Discord {bot.user} sudah aktif dan online!")
    try:
        synced = await bot.tree.sync()
        print(f"Berhasil mensinkronkan {len(synced)} global slash commands.")
    except Exception as e:
        print(f"Gagal sinkronisasi command: {e}")

# ==========================================
# 3. INTERACTIVE VIEWS & MODALS (TOMBOL & FORM)
# ==========================================

# View untuk Tombol Metode Pembayaran
class PaymentView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="QRIS", style=discord.ButtonStyle.green, emoji="🪪")
    async def qris_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        qris_url = os.getenv("QRIS_IMAGE_URL", "https://link-default-gambar.com")
        await interaction.response.send_message(
            f"📌 {interaction.user.mention} memilih metode pembayaran **QRIS**:\n"
            f"Silakan scan QR Code di bawah ini:\n{qris_url}\n\n"
            f"*(Harap kirimkan bukti transfer jika sudah melakukan pembayaran!)*"
        )

    @discord.ui.button(label="DANA", style=discord.ButtonStyle.primary, emoji="💳")
    async def dana_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        number = os.getenv("DANA_NUMBER", "08xxxxxxxxxx")
        name = os.getenv("DANA_NAME", "Nama Pemilik")
        await interaction.response.send_message(
            f"📌 {interaction.user.mention} memilih metode pembayaran **DANA**:\n"
            f"• Nomor: `{number}`\n"
            f"• Atas Nama: `{name}`\n\n"
            f"*(Harap kirimkan bukti transfer jika sudah melakukan pembayaran!)*"
        )

    @discord.ui.button(label="GOPAY", style=discord.ButtonStyle.blurple, emoji="💳")
    async def gopay_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        number = os.getenv("GOPAY_NUMBER", "08xxxxxxxxxx")
        name = os.getenv("GOPAY_NAME", "Nama Pemilik")
        await interaction.response.send_message(
            f"📌 {interaction.user.mention} memilih metode pembayaran **GOPAY**:\n"
            f"• Nomor: `{number}`\n"
            f"• Atas Nama: `{name}`\n\n"
            f"*(Harap kirimkan bukti transfer jika sudah melakukan pembayaran!)*"
        )

    @discord.ui.button(label="ShopeePay", style=discord.ButtonStyle.danger, emoji="💳")
    async def shopeepay_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        number = os.getenv("SHOPEEPAY_NUMBER", "08xxxxxxxxxx")
        name = os.getenv("SHOPEEPAY_NAME", "Nama Pemilik")
        await interaction.response.send_message(
            f"📌 {interaction.user.mention} memilih metode pembayaran **ShopeePay**:\n"
            f"• Nomor: `{number}`\n"
            f"• Atas Nama: `{name}`\n\n"
            f"*(Harap kirimkan bukti transfer jika sudah melakukan pembayaran!)*"
        )

# View gabungan di dalam Channel Tiket (Menu Payment + Tombol Close)
class TicketInsideView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(PaymentButtonSelect())
        self.add_item(CloseTicketButton())

class PaymentButtonSelect(discord.ui.Button):
    def __init__(self):
        super().__init__(label="💳 Pilih Metode Pembayaran", style=discord.ButtonStyle.blurple, custom_id="btn_pay_inside")

    async def callback(self, interaction: discord.Interaction):
        view = PaymentView()
        await interaction.response.send_message(
            "💳 **SILAKAN PILIH METODE PEMBAYARAN DI BAWAH INI:**",
            view=view
        )

class CloseTicketButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="🔒 Close Ticket", style=discord.ButtonStyle.red, custom_id="btn_close_ticket")

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("❌ Kamu tidak memiliki izin untuk menutup tiket ini!", ephemeral=True)
            return

        await interaction.response.send_message("🔒 Tiket dikonfirmasi ditutup. Channel akan dihapus otomatis dalam **5 detik**...")
        
        await asyncio.sleep(5)

        try:
            await interaction.channel.delete()
        except Exception as e:
            print(f"Gagal menghapus channel: {e}")

# Form Modal Dinamis Sesuai Jumlah Slot
class TicketModal(discord.ui.Modal, title="Form Pemesanan Slot Fish It X8"):
    jumlah_slot = discord.ui.TextInput(
        label="Mau beli berapa akun / slot? (1 - 5)",
        placeholder="Masukkan angka 1 sampai 5...",
        min_length=1,
        max_length=1,
        required=True
    )
    
    usn_roblox_1 = discord.ui.TextInput(
        label="Username Roblox (Akun 1)",
        placeholder="Wajib diisi untuk akun pertama...",
        required=True
    )

    usn_roblox_2 = discord.ui.TextInput(
        label="Username Roblox (Akun 2 - Opsional)",
        placeholder="Isi jika beli 2 akun...",
        required=False
    )

    usn_roblox_3 = discord.ui.TextInput(
        label="Username Roblox (Akun 3 - Opsional)",
        placeholder="Isi jika beli 3 akun...",
        required=False
    )

    usn_roblox_4 = discord.ui.TextInput(
        label="Username Roblox (Akun 4/5 - Opsional)",
        placeholder="Isi jika beli 4/5 akun...",
        required=False
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        try:
            total_slot = int(self.jumlah_slot.value)
            if not (1 <= total_slot <= 5):
                raise ValueError()
        except ValueError:
            await interaction.followup.send("⚠️ Masukkan angka yang valid antara **1 sampai 5** untuk jumlah slot!", ephemeral=True)
            return

        # Kumpulkan username Roblox sesuai jumlah slot yang dipilih
        daftar_usn = []
        if total_slot >= 1 and self.usn_roblox_1.value.strip():
            daftar_usn.append(self.usn_roblox_1.value.strip())
        if total_slot >= 2 and self.usn_roblox_2.value.strip():
            daftar_usn.append(self.usn_roblox_2.value.strip())
        if total_slot >= 3 and self.usn_roblox_3.value.strip():
            daftar_usn.append(self.usn_roblox_3.value.strip())
        if total_slot >= 4 and self.usn_roblox_4.value.strip():
            # Jika user beli 4 atau 5, ambil juga input dari field ke-4
            input_split = self.usn_roblox_4.value.strip().split(",")
            for u in input_split:
                if u.strip():
                    daftar_usn.append(u.strip())

        harga_per_slot = 14000
        total_harga = total_slot * harga_per_slot
        
        guild = interaction.guild
        member = interaction.user

        # Set permission: Hanya member ybs, bot, dan admin yang bisa lihat channel
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            member: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }

        target_category = interaction.channel.category
        channel_name = f"ticket-{member.name}"
        
        try:
            ticket_channel = await guild.create_text_channel(
                name=channel_name,
                overwrites=overwrites,
                category=target_category
            )
        except Exception as e:
            await interaction.followup.send(f"⚠️ Gagal membuat channel tiket: {e}", ephemeral=True)
            return

        # Format list username Roblox untuk ditampilkan di tiket
        formatted_usn = "\n".join([f"• Akun {i+1}: `{usn}`" for i, usn in enumerate(daftar_usn)]) if daftar_usn else "• Belum diisi / Cek manual"

        # Kirim rincian pesanan ke channel privat tiket
        ticket_view = TicketInsideView()
        await ticket_channel.send(
            f"Halo {member.mention}! Terima kasih sudah membuka tiket.\n\n"
            f"📋 **Rincian Pemesanan:**\n"
            f"• Jumlah Akun / Slot: **{total_slot} Slot**\n"
            f"• **Username Roblox:**\n{formatted_usn}\n"
            f"• Harga per Slot: **Rp 14.000**\n"
            f"• **TOTAL TAGIHAN: Rp {total_harga:,}**\n\n"
            f"Silakan klik tombol **Pilih Metode Pembayaran** di bawah untuk melanjutkan transaksi.",
            view=ticket_view
        )

        await interaction.followup.send(f"✅ Tiket kamu berhasil dibuat! Silakan cek channel {ticket_channel.mention}", ephemeral=True)

class TicketCreateView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📩 Create Ticket", style=discord.ButtonStyle.green, custom_id="create_ticket_btn")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(TicketModal())

# ==========================================
# 4. SLASH COMMANDS
# ==========================================

@bot.tree.command(name="setuplist", description="Mengirim pesan list rekap Fish It X8 otomatis ke channel ini")
async def setuplist(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)

    if interaction.channel.name != "ptpt-x8":
        await interaction.followup.send("⚠️ Perintah ini hanya bisa digunakan di channel **#ptpt-x8**!", ephemeral=True)
        return

    format_list = (
        "LIST BOOST SERVER FISH IT X8 By <@617248535913693194>  <@785872264100446210>\n\n"
        "14k/SLOT\n\n"
        "KLOTER 22 ( 24 JAM )\n\n"
        "LIST MENGGUNAKAN Usn & Nick ROBLOX\n"
        "Contoh : zens1907\n\n"
        "1. -\n2. -\n3. -\n4. -\n5. -\n"
        "6. -\n7. -\n8. -\n9. -\n10. -\n"
        "11. -\n12. -\n13. -\n14. -\n15. -\n"
        "16. -\n17. -\n18. -\n19. dmin 2\n20. Admin 1"
    )

    sent_message = await interaction.channel.send(format_list)
    
    await interaction.followup.send(
        f"✅ Berhasil membuat pesan list Kloter 22!\n\n"
        f"Salin Message ID di bawah ini dan masukkan ke variabel `LIST_MESSAGE_ID` di kodingan bot:\n"
        f"`{sent_message.id}`",
        ephemeral=True
    )

@bot.tree.command(name="done", description="Mengisi slot list rekap Fish It X8 secara otomatis")
@app_commands.describe(
    slot_number="Nomor slot yang ingin diisi (contoh: 1, 2, dst)",
    roblox_usn="Username / Nick Roblox buyer"
)
async def done(interaction: discord.Interaction, slot_number: int, roblox_usn: str):
    await interaction.response.defer(ephemeral=True)

    target_channel_name = "ptpt-x8"
    rekap_channel = discord.utils.get(interaction.guild.text_channels, name=target_channel_name)
    
    if not rekap_channel:
        await interaction.followup.send(
            f"⚠️ Channel dengan nama **#{target_channel_name}** tidak ditemukan di server ini!",
            ephemeral=True
        )
        return

    try:
        msg = await rekap_channel.fetch_message(LIST_MESSAGE_ID)
    except discord.NotFound:
        await interaction.followup.send(
            f"⚠️ Pesan list utama tidak ditemukan di channel #{target_channel_name}! Pastikan LIST_MESSAGE_ID benar.",
            ephemeral=True
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
            f"✅ Slot nomor **{slot_number}** berhasil diisi oleh **{roblox_usn}** di channel **#{target_channel_name}**!",
            ephemeral=True
        )
    else:
        await interaction.followup.send(
            f"⚠️ Slot nomor {slot_number} tidak ditemukan dalam format list!",
            ephemeral=True
        )

@bot.tree.command(name="setup-ticket", description="Memunculkan panel tombol untuk membuat tiket transaksi")
async def setup_ticket(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    
    view = TicketCreateView()
    await interaction.channel.send(
        "🛒 **SILAKAN BUAT TIKET TRANSAKSI**\n"
        "Klik tombol di bawah ini untuk memasukkan jumlah akun/slot pesanan:",
        view=view
    )
    await interaction.followup.send("✅ Panel Create Ticket berhasil dikirim ke channel ini!", ephemeral=True)

# ==========================================
# 5. MENJALANKAN BOT
# ==========================================
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not TOKEN:
    print("⚠️ ERROR: Token bot Discord tidak ditemukan!")
else:
    bot.run(TOKEN)
