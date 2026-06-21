import csv
import os
from collections import deque
import random

# ==========================================
# KONFIGURASI DAN STRUKTUR DATA
# ==========================================
CSV_FILE = 'KATALOG_KONSER.CSV'
HARGA_PER_TIKET = 6000000  # Set harga rata Rp 6.000.000 per tiket

# Katalog Tampilan Konser (NJ001 - NJ010)
KATALOG_KONSER = {
    "NJ001": "Zayn Malik",
    "NJ002": "LANY",
    "NJ003": "Olivia Rodrigo",
    "NJ004": "Niall Horan",
    "NJ005": "Taylor Swift",
    "NJ006": "The Weeknd",
    "NJ007": "Billie Eilish",
    "NJ008": "Harry Styles",
    "NJ009": "Ed Sheeran",
    "NJ010": "Justin Bieber"
}

# Kolom CSV yang disesuaikan (Ditambah Harga_Total)
FIELDNAMES = ["ID_Pesanan", "ID_Konser", "Artis", "Nama_Pemesan", "Jumlah_Tiket", "Harga_Total"]

# 1. QUEUE: Untuk antrean pemrosesan tiket (FIFO)
antrean_pesanan = deque()

# 2. STACK: Untuk fitur Undo pembatalan (LIFO)
stack_undo = []

# ==========================================
# FUNGSI UTILITAS & DATABASE
# ==========================================
def pastikan_file_ada():
    """Memastikan file CSV tersedia beserta headernya."""
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(FIELDNAMES)

def baca_semua_tiket():
    """Membaca semua data dari file CSV (READ)."""
    tiket_list = []
    with open(CSV_FILE, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            tiket_list.append(row)
    return tiket_list

def tulis_semua_tiket(tiket_list):
    """Menulis ulang seluruh data ke file CSV (Untuk Update & Delete)."""
    with open(CSV_FILE, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(tiket_list)

# ==========================================
# FUNGSI CRUD
# ==========================================
def lihat_katalog():
    print("\n--- KATALOG NANA CONCERT FAIR 2026 ---")
    print(f"Harga Tiket: Rp {HARGA_PER_TIKET:,} / tiket")
    print("---------------------------------")
    for id_konser, artis in KATALOG_KONSER.items():
        print(f"[{id_konser}] - {artis}")
    print("---------------------------------")

def tambah_tiket():
    """CREATE: Menambah tiket melalui Queue."""
    lihat_katalog()
    id_konser = input("Masukkan ID Konser (contoh: NJ001): ").strip().upper()
    
    if id_konser not in KATALOG_KONSER:
        print("❌ ID Konser tidak ditemukan!")
        return

    nama = input("Masukkan Nama Pemesan: ").strip()
    
    try:
        jumlah = int(input("Masukkan Jumlah Tiket: ").strip())
        if jumlah <= 0:
            print("❌ Jumlah tiket harus lebih dari 0!")
            return
    except ValueError:
        print("❌ Masukkan angka yang valid untuk jumlah tiket!")
        return
    
    # Hitung total harga otomatis
    total_harga = jumlah * HARGA_PER_TIKET
    id_pesanan = f"TKT-{random.randint(1000, 9999)}"
    artis = KATALOG_KONSER[id_konser]
    
    data_baru = {
        "ID_Pesanan": id_pesanan,
        "ID_Konser": id_konser,
        "Artis": artis,
        "Nama_Pemesan": nama,
        "Jumlah_Tiket": str(jumlah),
        "Harga_Total": f"Rp {total_harga:,}"  # Format mata uang rapi pake koma
    }
    
    # Masukkan ke Queue (Enqueue)
    antrean_pesanan.append(data_baru)
    print("⏳ Pesanan sedang diproses...")
    
    # Proses Queue ke Database CSV (Dequeue)
    proses_pesanan = antrean_pesanan.popleft()
    
    with open(CSV_FILE, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writerow(proses_pesanan)
    
    print(f"✅ Tiket berhasil dipesan dengan ID: {id_pesanan}")
    print(f"💰 Total Harga: {data_baru['Harga_Total']}")

def lihat_tiket():
    """READ: Menampilkan tiket dari file CSV."""
    tiket_list = baca_semua_tiket()
    print("\n--- DAFTAR TIKET SAYA ---")
    if not tiket_list:
        print("Belum ada tiket yang dipesan.")
    else:
        for t in tiket_list:
            # Handle kalau ada data lama yang belum punya kolom Harga_Total
            harga = t.get('Harga_Total', 'Rp 0')
            print(f"ID: {t['ID_Pesanan']} | {t['Artis']} ({t['ID_Konser']}) | Pemesan: {t['Nama_Pemesan']} | Jml: {t['Jumlah_Tiket']} | Total: {harga}")
    print("-------------------------")

def update_tiket():
    """UPDATE: Mengubah data tiket di CSV berdasarkan ID Pesanan."""
    lihat_tiket()
    id_pesanan = input("Masukkan ID Pesanan yang ingin diubah: ").strip().upper()
    tiket_list = baca_semua_tiket()
    ditemukan = False
    
    for t in tiket_list:
        if t['ID_Pesanan'] == id_pesanan:
            print(f"Data saat ini: Pemesan ({t['Nama_Pemesan']}), Jumlah ({t['Jumlah_Tiket']})")
            t['Nama_Pemesan'] = input("Nama Pemesan baru: ").strip()
            
            try:
                baru_jumlah = int(input("Jumlah Tiket baru: ").strip())
                if baru_jumlah > 0:
                    t['Jumlah_Tiket'] = str(baru_jumlah)
                    # Hitung ulang total harganya juga pas di-update
                    t['Harga_Total'] = f"Rp {baru_jumlah * HARGA_PER_TIKET:,}"
            except ValueError:
                print("❌ Jumlah tidak valid, jumlah lama tetap digunakan.")
                
            ditemukan = True
            break
            
    if ditemukan:
        tulis_semua_tiket(tiket_list)
        print("✅ Data tiket berhasil diperbarui!")
    else:
        print("❌ ID Pesanan tidak ditemukan.")

def hapus_tiket():
    """DELETE: Menghapus tiket dan memasukkannya ke Stack untuk Undo."""
    lihat_tiket()
    id_pesanan = input("Masukkan ID Pesanan yang ingin dibatalkan: ").strip().upper()
    tiket_list = baca_semua_tiket()
    tiket_baru = []
    dihapus = None
    
    for t in tiket_list:
        if t['ID_Pesanan'] == id_pesanan:
            dihapus = t
        else:
            tiket_baru.append(t)
            
    if dihapus:
        # Masukkan data ke Stack (Push)
        stack_undo.append(dihapus)
        tulis_semua_tiket(tiket_baru)
        print(f"✅ Tiket {id_pesanan} berhasil dibatalkan.")
    else:
        print("❌ ID Pesanan tidak ditemukan.")

def undo_hapus():
    """Mengambil data dari Stack untuk mengembalikan data (LIFO)."""
    if not stack_undo:
        print("❌ Tidak ada histori pembatalan tiket yang bisa di-undo.")
        return
        
    # Ambil data terakhir dari Stack (Pop)
    tiket_dipulihkan = stack_undo.pop()
    
    with open(CSV_FILE, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writerow(tiket_dipulihkan)
        
    print(f"🔄 Undo berhasil! Tiket {tiket_dipulihkan['ID_Pesanan']} telah dikembalikan ke database.")

# ==========================================
# MENU UTAMA
# ==========================================
def main():
    pastikan_file_ada()
    while True:
        print("\n=================================")
        print("       NANA CONCERT FAIR 2026      ")
        print("===================================")
        print("1. Lihat Daftar Konser")
        print("2. Pesan Tiket Konser")
        print("3. Lihat Daftar Pesanan")
        print("4. Ubah Data Tiket")
        print("5. Batalkan Tiket")
        print("6. Urungkan Batal Tiket")
        print("7. Keluar")
        print("===================================")
        pilihan = input("Pilih menu (1-7): ")
        
        if pilihan == '1':
            lihat_katalog()
        elif pilihan == '2':
            tambah_tiket()
        elif pilihan == '3':
            lihat_tiket()
        elif pilihan == '4':
            update_tiket()
        elif pilihan == '5':
            hapus_tiket()
        elif pilihan == '6':
            undo_hapus()
        elif pilihan == '7':
            print("Terima kasih telah menggunakan layanan Nana Concert Fair!")
            break
        else:
            print("❌ Pilihan tidak valid.")

if __name__ == "__main__":
    main()