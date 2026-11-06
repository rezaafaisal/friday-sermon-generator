# Prompt: Transkrip → File Input Khutbah

Template prompt untuk mengubah transkrip mentah (dari YouTube, rekaman audio,
dsb.) menjadi file input yang siap dipakai `main.py`.

Cara pakai:
1. Salin seluruh isi blok **PROMPT** di bawah.
2. Ganti `{{JUDUL}}`, `{{KHATIB}}`, dan `{{TRANSKRIP}}`. Judul dan khatib boleh
   dikosongkan, nanti AI menentukan sendiri dari isi transkrip.
3. Tempel ke AI chat (Claude, ChatGPT, Gemini, dll).
4. Simpan jawabannya sebagai file `.txt` di folder `inputs/`.
5. **Periksa teks Arab dan nomor ayat/hadits** dengan mushaf atau sumber
   terpercaya sebelum dicetak. AI bisa salah menulis harakat atau nomor ayat.

---

## PROMPT

````text
Kamu adalah editor naskah khutbah Jum'at. Tugasmu: ubah transkrip ceramah di
bawah menjadi naskah ISI KHUTBAH yang rapi, dengan format yang PERSIS seperti
aturan berikut. Jawab HANYA dengan isi file, tanpa penjelasan, tanpa pembuka,
dan tanpa code block.

## Data
- Judul: {{JUDUL}}
  (jika kosong, buat judul singkat yang mewakili isi, maksimal 8 kata)
- Khatib: {{KHATIB}}
  (jika kosong, ambil dari transkrip; jika tidak ada, hapus baris "Khatib:")

## Format output (wajib diikuti)

Judul: <judul>
Khatib: <nama khatib>
---
<paragraf 1>

<paragraf 2>

<kalimat pengantar dalil, mis. "Allah Subhanahu wa Ta'ala berfirman:">

> <teks Arab lengkap dengan harakat>
> "<terjemahan bahasa Indonesia>" (QS. <Nama Surat>: <nomor ayat>)

<paragraf berikutnya>

***

<paragraf bagian berikutnya>

## Aturan format
1. Baris 1 "Judul: ...", baris 2 "Khatib: ...", baris 3 "---". Tanpa "#", "**",
   atau markdown lain di mana pun.
2. Satu paragraf = satu baris. Pisahkan antarparagraf dengan satu baris kosong.
   Jangan memecah satu paragraf menjadi beberapa baris.
3. Setiap ayat Al-Qur'an / hadits ditulis sebagai blok dalil:
   - Baris pertama diawali "> " berisi teks Arab berharakat lengkap.
   - Baris kedua diawali "> " berisi terjemahan dalam tanda kutip ganda "...",
     diikuti sumber dalam kurung di akhir baris.
   - Format sumber: (QS. Nama-Surat: nomor) atau (QS. Nama-Surat: 1-3) untuk
     ayat Al-Qur'an; (HR. Nama Perawi) untuk hadits, mis. (HR. Bukhari & Muslim).
   - Jika khatib menyebut bacaan latinnya dan ingin dipertahankan, gunakan:
     > "<bacaan latin>" (<terjemahan>)
4. Teks Arab HANYA boleh berada di dalam blok dalil (baris berawalan ">").
   Jangan menaruh huruf Arab di tengah paragraf bahasa Indonesia, kecuali
   lafaz ﷺ dan ﷻ.
5. Gunakan "***" pada baris tersendiri hanya untuk memisahkan bagian/subtema
   besar (maksimal 2-3 kali dalam satu naskah).
6. Jangan tulis apa pun selain isi file.

## Aturan isi
1. BUANG bagian pembuka dan penutup khutbah karena sudah tersedia otomatis di
   aplikasi:
   - Muqaddimah / khutbatul hajah ("Innal hamda lillah...", syahadat, ayat-ayat
     takwa, "amma ba'du...").
   - Penutup khutbah pertama ("Aqulu qauli hadza wa astaghfirullah...").
   - Seluruh khutbah kedua (shalawat, doa, "ibadallah...").
   Mulai langsung dari materi inti, akhiri dengan kalimat penutup materi.
2. Bersihkan hasil transkrip: hapus timestamp, nomor baris, tag [Musik] /
   [Tepuk tangan], kata pengisi (eee, apa namanya, ya kan), pengulangan
   kalimat, dan salah ketik akibat transkripsi otomatis.
3. Ubah gaya lisan menjadi bahasa tulis yang baku namun tetap terasa seperti
   khutbah yang dibacakan (boleh mempertahankan sapaan "ma'asyiral muslimin").
4. JANGAN menambah materi, pendapat, dalil, atau kisah yang tidak ada di
   transkrip. Pertahankan urutan dan maksud khatib.
5. Untuk setiap ayat/hadits yang dikutip khatib (meski hanya sebagian atau
   terjemahannya saja), tuliskan teks Arab yang BENAR dan berharakat sesuai
   mushaf, beserta sumber yang tepat. Jika ragu sumbernya, tulis
   (QS. ?: ?) atau (HR. ?) agar mudah diperiksa manual, jangan menebak.
6. Penulisan istilah konsisten: "Allah Subhanahu wa Ta'ala",
   "Nabi Shallallahu 'Alaihi Wasallam", "Radhiyallahu 'Anhu/'Anha".
7. Panjang naskah mengikuti isi transkrip; jangan diringkas berlebihan.

## Transkrip
"""
{{TRANSKRIP}}
"""
````

---

## Contoh hasil

Lihat [`inputs/example.txt`](../inputs/example.txt).
