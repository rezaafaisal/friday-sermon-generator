# Friday Sermon Generator

Generator PDF **naskah khutbah Jum'at** siap cetak / siap baca di mimbar.
Ambil transkrip ceramah (mis. dari YouTube), rapikan dengan AI memakai template
prompt yang disediakan, lalu script ini menyusunnya
menjadi PDF A4 lengkap dengan bacaan pembuka, penutup, dan khutbah kedua
berbahasa Arab berharakat.

## Struktur PDF yang dihasilkan

| Bagian | Isi | Sumber |
|---|---|---|
| 1. **Khutbah Pertama** (الْخُطْبَةُ الأُولَى) | Khutbatul hajah: hamdalah, syahadat, 3 ayat takwa, *amma ba'du* | Tetap (di `main.py`) |
| 2. **Isi Khutbah** | Judul, nama khatib, materi khutbah beserta dalil (ayat/hadits) | **File input** |
| 3. **Penutup Khutbah Pertama** | *Aqulu qauli hadza wa astaghfirullaha li wa lakum…* — tampil tepat setelah isi khutbah | Tetap (di `main.py`) |
| 4. **Khutbah Kedua** (الْخُطْبَةُ الثَّانِيَةُ) | Hamdalah, shalawat, doa, dan penutup | Tetap (di `main.py`) |

Setiap bagian 1, 2–3, dan 4 dimulai di halaman baru. Nomor halaman ditampilkan
dalam bahasa Arab di bagian bawah.

## Instalasi

Butuh **Python 3.10+** dan [WeasyPrint](https://weasyprint.org/).
WeasyPrint memerlukan library sistem Pango:

```bash
# macOS
brew install pango

# Ubuntu / Debian
sudo apt install libpango-1.0-0 libpangoft2-1.0-0
```

Lalu install dependensi Python:

```bash
git clone https://github.com/rezaafaisal/friday-sermon-generator.git
cd friday-sermon-generator

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> Font **Amiri** dan **Scheherazade New** diambil dari Google Fonts saat
> generate, jadi perlu koneksi internet. Jika offline, install font tersebut di
> sistem agar teks Arab tetap tampil rapi.

## Alur kerja

```
Video YouTube / rekaman ──► Transkrip mentah ──► (AI + template prompt) ──► inputs/*.txt ──► main.py ──► PDF
         langkah 1                                      langkah 2                         langkah 3
```

### Langkah 1 — Siapkan transkrip

Ambil teks dari video ceramah/khutbah. Pilih salah satu cara:

- **YouTube (manual):** buka video → `...` di bawah video → **Tampilkan transkrip**
  → salin semua teksnya.
- **YouTube (otomatis, pakai [yt-dlp](https://github.com/yt-dlp/yt-dlp)):**

  ```bash
  pip install yt-dlp
  yt-dlp --skip-download --write-auto-subs --sub-langs id --convert-subs srt \
    -o "transcripts/%(title)s.%(ext)s" "https://www.youtube.com/watch?v=XXXX"
  ```

  Hasilnya file `.srt` di folder `transcripts/` (timestamp tidak masalah, nanti
  dibersihkan AI). Ganti `--sub-langs id` sesuai bahasa video.
- **Rekaman audio / video lain:** gunakan layanan speech-to-text
  (mis. Whisper, fitur transkrip Google Docs/Recorder, dll).

### Langkah 2 — Rapikan transkrip ke format input

Transkrip mentah **belum** sesuai format yang dibutuhkan (masih ada timestamp,
kata pengisi, pembuka/penutup khutbah, dan ayat belum ditulis dalam huruf Arab).

Gunakan template prompt di
[`prompts/transcript-to-khutbah.md`](prompts/transcript-to-khutbah.md):

1. Salin prompt, isi `{{JUDUL}}`, `{{KHATIB}}`, dan tempel transkrip ke
   `{{TRANSKRIP}}`.
2. Kirim ke AI chat (Claude, ChatGPT, Gemini, dll).
3. Simpan jawabannya sebagai `inputs/<nama>.txt`.

Sebelum lanjut, **pastikan file sudah sesuai format**:

- [ ] Baris pertama `Judul: ...`, lalu `Khatib: ...`, lalu `---`
- [ ] Tidak ada muqaddimah, *aqulu qauli hadza…*, atau khutbah kedua
  (sudah otomatis ditambahkan aplikasi)
- [ ] Setiap dalil berada di baris berawalan `>`: teks Arab, lalu
  `"terjemahan" (QS./HR. ...)`
- [ ] Satu paragraf per baris, tanpa timestamp atau markdown (`#`, `**`)
- [ ] **Teks Arab dan nomor ayat/hadits sudah dicek** dengan mushaf /
  sumber terpercaya — AI bisa keliru

Detail format ada di bagian [Input](#input).

### Langkah 3 — Generate PDF

Lihat [Cara pakai](#cara-pakai) di bawah.

## Cara pakai

```bash
# Pakai contoh bawaan (inputs/example.txt)
python main.py

# Pakai file isi sendiri
python main.py inputs/khutbah_saya.txt

# Pakai file isi sendiri + folder output lain
python main.py inputs/khutbah_saya.txt hasil/
```

Output:

```
PDF berhasil dibuat: outputs/Judul Khutbah.pdf
```

## Input

File teks UTF-8 (`.txt`), sebaiknya disimpan di folder `inputs/`.

### Format

```text
Judul: Nikmat Allah Tak Terhingga
Khatib: Ustadz Fulan
---
Paragraf biasa, satu paragraf per baris.

Allah berfirman:

> إِنَّ فِي ذَلِكَ لَآيَاتٍ لِكُلِّ صَبَّارٍ شَكُورٍ
> "Sungguh pada demikian itu ada tanda-tanda bagi setiap orang yang sabar dan bersyukur." (QS. Luqman: 31)

***

Paragraf setelah garis pemisah.
```

### Aturan

| Sintaks | Hasil |
|---|---|
| `Judul: ...` | Judul khutbah (wajib, di awal file). Juga dipakai sebagai nama file PDF |
| `Khatib: ...` | Nama khatib (opsional) |
| `---` | Pemisah header dan isi (opsional) |
| Baris biasa | Satu paragraf |
| Baris berawalan `>` | Kotak dalil. Baris `>` yang berurutan digabung jadi satu kotak |
| Teks Arab di dalam dalil | Ditampilkan besar, rata tengah, kanan-ke-kiri |
| `"Bacaan latin" (Terjemahan)` | Latin dicetak tebal-miring, terjemahan miring |
| `"Terjemahan."` | Terjemahan dicetak miring |
| `(QS. ...)`, `(HR. ...)`, `(Muttafaq ...)`, `(Riwayat ...)` di akhir baris | Sumber dalil, rata kanan |
| `***` | Garis pemisah |
| `ﷺ` / `ﷻ` | Dicetak dengan font Arab agar terbaca jelas |

Catatan:
- Teks Arab yang ditulis **tanpa** `>` juga otomatis dijadikan kotak dalil,
  dan baris terjemahan / sumber tepat di bawahnya ikut digabung.
- Header yang tergabung dalam satu baris (mis. hasil salin dari markdown:
  `## Judul: ... Khatib: ...`) juga dikenali.

Lihat contoh lengkap di [`inputs/example.txt`](inputs/example.txt).

## Output

- Format: **PDF A4**, margin 20 × 15 mm.
- Lokasi: folder `outputs/` (atau folder yang diberikan sebagai argumen kedua).
- Nama file: sesuai judul khutbah, mis. `outputs/Nikmat Allah Tak Terhingga.pdf`.
  Karakter yang tidak valid untuk nama file (`\ / : * ? " < > |`) dibuang.
- Footer tiap bagian: `Khutbah Jum'at: <Khatib> | <Judul>`.

## Kustomisasi

Semua ada di `main.py`:

| Yang ingin diubah | Variabel |
|---|---|
| Bacaan khutbah pertama | `khutbah_1_arab` |
| Penutup khutbah pertama | `penutup_khutbah_1_arab` |
| Bacaan khutbah kedua & doa | `khutbah_2_arab` |
| Ukuran font Arab (bacaan khutbah) | `UKURAN_ARAB_KHUTBAH` (default 26pt) |
| Ukuran font Arab (dalil di isi) | `UKURAN_ARAB_ISI` (default 24pt) |
| Ukuran font Indonesia | `UKURAN_INDO` (default 15pt) |
| Warna, margin, tata letak | `CSS` |
| Lokasi input / output default | `FILE_ISI_DEFAULT`, `FOLDER_OUTPUT_DEFAULT` |

Pada teks bacaan Arab, baris kosong memisahkan paragraf.

## Struktur projek

```
friday-sermon-generator/
├── main.py            # script generator
├── requirements.txt
├── prompts/
│   └── transcript-to-khutbah.md  # template prompt transkrip → input
├── transcripts/       # transkrip mentah (opsional, diabaikan git)
├── inputs/
│   └── example.txt    # contoh isi khutbah
└── outputs/           # hasil PDF
```
