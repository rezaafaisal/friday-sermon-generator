"""Generator PDF khutbah Jum'at.

Isi khutbah (judul, khatib, materi) diambil dari file teks — default
`inputs/example.txt`. Bacaan khutbah pertama & kedua di bawah ini tetap.

    python main.py                              # pakai inputs/example.txt
    python main.py inputs/file_lain.txt         # pakai file isi lain
    python main.py inputs/file_lain.txt hasil/  # + folder output lain

Hasilnya PDF di folder `outputs/` dengan nama sesuai judul,
mis. "outputs/Judul Khutbah.pdf".

Format file isi:

    Judul: Judul Khutbah
    Khatib: Nama Khatib
    ---
    Paragraf biasa, satu paragraf per baris.

    > teks Arab ayat / hadits
    > "Terjemahannya."
    > (QS. Al-'Asr: 1-3)

    ***

Baris berawalan ">" yang berurutan menjadi satu kotak dalil: Arab, bacaan
latin, terjemahan, dan sumber masing-masing di barisnya sendiri. "***" menjadi
garis pemisah.
"""

import html
import re
import sys
from pathlib import Path

import weasyprint

# Bacaan tetap khutbah pertama & kedua (tidak ikut berubah saat isi diganti)

khutbah_1_arab = """إِنَّ الحَمْدَ لِلَّهِ، نَحْمَدُهُ وَنَسْتَعِينُهُ وَنَسْتَغْفِرُهُ، وَنَعُوذُ بِاللَّهِ مِنْ شُرُورِ أَنْفُسِنَا وَمِنْ سَيِّئَاتِ أَعْمَالِنَا، مَنْ يَهْدِهِ اللَّهُ فَلَا مُضِلَّ لَهُ، وَمَنْ يُضْلِلْ فَلَا هَادِيَ لَهُ، وَأَشْهَدُ أَنْ لَا إِلَهَ إِلَّا اللَّهُ وَحْدَهُ لَا شَرِيكَ لَهُ، وَأَشْهَدُ أَنَّ مُحَمَّدًا عَبْدُهُ وَرَسُولُهُ.

يَا أَيُّهَا الَّذِينَ آمَنُوا اتَّقُوا اللَّهَ حَقَّ تُقَاتِهِ وَلَا تَمُوتُنَّ إِلَّا وَأَنْتُمْ مُسْلِمُونَ.

يَا أَيُّهَا النَّاسُ اتَّقُوا رَبَّكُمُ الَّذِي خَلَقَكُمْ مِنْ نَفْسٍ وَاحِدَةٍ وَخَلَقَ مِنْهَا زَوْجَهَا وَبَثَّ مِنْهُمَا رِجَالًا كَثِيرًا وَنِسَاءً وَاتَّقُوا اللَّهَ الَّذِي تَسَاءَلُونَ بِهِ وَالأَرْحَامَ إِنَّ اللَّهَ كَانَ عَلَيْكُمْ رَقِيبًا.

يَا أَيُّهَا الَّذِينَ آمَنُوا اتَّقُوا اللَّهَ وَقُولُوا قَوْلًا سَدِيدًا، يُصْلِحْ لَكُمْ أَعْمَالَكُمْ وَيَغْفِرْ لَكُمْ ذُنُوبَكُمْ وَمَنْ يُطِعِ اللَّهَ وَرَسُولَهُ فَقَدْ فَازَ فَوْزًا عَظِيمًا.

أَمَّا بَعْدُ: فَإِنَّ أَصْدَقَ الحَدِيثِ كِتَابُ اللَّهِ، وَخَيْرَ الهُدَى هُدَى مُحَمَّدٍ صَلَّى اللَّهُ عَلَيْهِ وَسَلَّمَ، وَشَرَّ الأُمُورِ مُحْدَثَاتُهَا، وَكُلَّ مُحْدَثَةٍ بِدْعَةٌ، وَكُلَّ بِدْعَةٍ ضَلَالَةٌ، وَكُلَّ ضَلَالَةٍ فِي النَّارِ."""

# Penutup khutbah pertama — ditampilkan tepat setelah isi khutbah
penutup_khutbah_1_arab = """أَقُولُ قَوْلِي هَذَا وَأَسْتَغْفِرُ اللَّهَ لِي وَلَكُمْ وَلِسَائِرِ المُسْلِمِينَ مِنْ كُلِّ ذَنْبٍ، فَاسْتَغْفِرُوهُ إِنَّهُ هُوَ الغَفُورُ الرَّحِيمُ."""

khutbah_2_arab = """الْحَمْدُ لِلَّهِ حَمْدًا كَثِيرًا طَيِّبًا مُبَارَكًا فِيهِ كَمَا يُحِبُّ رَبُّنَا وَيَرْضَى، وَأَشْهَدُ أَنْ لَا إِلَهَ إِلَّا اللَّهُ وَحْدَهُ لَا شَرِيكَ لَهُ، وَأَشْهَدُ أَنَّ مُحَمَّدًا عَبْدُهُ وَرَسُولُهُ، صَلَّى اللَّهُ عَلَيْهِ وَعَلَى آلِهِ وَأَصْحَابِهِ وَسَلَّمَ تَسْلِيمًا كَثِيرًا.

[الدُّعَاءُ]
إِنَّ اللَّهَ وَمَلَائِكَتَهُ يُصَلُّونَ عَلَى النَّبِيِّ يَا أَيُّهَا الَّذِينَ آمَنُوا صَلُّوا عَلَيْهِ وَسَلِّمُوا تَسْلِيمًا.

اللَّهُمَّ صَلِّ عَلَى مُحَمَّدٍ وَعَلَى آلِ مُحَمَّدٍ كَمَا صَلَّيْتَ عَلَى إِبْرَاهِيمَ وَعَلَى آلِ إِبْرَاهِيمَ إِنَّكَ حَمِيدٌ مَجِيدٌ، وَبَارِكْ عَلَى مُحَمَّدٍ وَعَلَى آلِ مُحَمَّدٍ كَمَا بَارَكْتَ عَلَى إِبْرَاهِيمَ وَعَلَى آلِ إِبْرَاهِيمَ إِنَّكَ حَمِيدٌ مَجِيدٌ.

اللَّهُمَّ اغْفِرْ لِلْمُسْلِمِينَ وَالْمُسْلِمَاتِ، وَالْمُؤْمِنِينَ وَالْمُؤْمِنَاتِ، الْأَحْيَاءِ مِنْهُمْ وَالْأَمْوَاتِ.

اللَّهُمَّ إِنَّا نَسْأَلُكَ الْهُدَى وَالتُّقَى وَالْعَفَافَ وَالْغِنَى.

اللَّهُمَّ حَاسِبْنَا حِسَابًا يَسِيرًا.

اللَّهُمَّ لَا تَجْعَلِ الدُّنْيَا أَكْبَرَ هَمِّنَا، وَلَا مَبْلَغَ عِلْمِنَا، وَلَا إِلَى النَّارِ مَصِيرَنَا.

رَبَّنَا آتِنَا فِي الدُّنْيَا حَسَنَةً وَفِي الْآخِرَةِ حَسَنَةً وَقِنَا عَذَابَ النَّارِ.

عِبَادَ اللَّهِ، إِنَّ اللَّهَ يَأْمُرُ بِالْعَدْلِ وَالْإِحْسَانِ وَإِيتَاءِ ذِي الْقُرْبَى وَيَنْهَى عَنِ الْفَحْشَاءِ وَالْمُنْكَرِ وَالْبَغْيِ يَعِظُكُمْ لَعَلَّكُمْ تَذَكَّرُونَ. فَاذْكُرُوا اللَّهَ الْعَظِيمَ يَذْكُرْكُمْ، وَاشْكُرُوهُ عَلَى نِعَمِهِ يَزِدْكُمْ، وَلَذِكْرُ اللَّهِ أَكْبَرُ، وَاللَّهُ يَعْلَمُ مَا تَصْنَعُونَ."""

FOLDER_PROJEK = Path(__file__).resolve().parent
FILE_ISI_DEFAULT = FOLDER_PROJEK / "inputs" / "example.txt"
FOLDER_OUTPUT_DEFAULT = FOLDER_PROJEK / "outputs"

# Ukuran font (pt) — ubah di sini kalau masih kurang besar / terlalu besar
UKURAN_ARAB_KHUTBAH = 26  # bacaan khutbah 1 & 2
UKURAN_ARAB_ISI = 24  # ayat / hadits di dalam isi khutbah
UKURAN_INDO = 15  # teks Indonesia

ARAB = r"[؀-ۿݐ-ݿﭐ-ﷹ﷼-﷿ﹰ-﻿]"
HONORIFIK = re.compile(r"[ﷺﷻ]")  # ﷺ ﷻ
ARAB_RUN = re.compile(rf"({ARAB}+(?:[\s:.,…\-ﷺﷻ]+{ARAB}+)*)")
# "(QS. ...)" / "(HR. ...)" di akhir baris
SUMBER_AKHIR = re.compile(r"\s*\(\s*((?:QS|Q\.S|HR|H\.R|Muttafaq|Riwayat)\b[^()]*)\)\.?\s*$")
# "Bacaan latin" (Terjemahan)
HEADER = re.compile(r"(Judul|Khatib)\s*:\s*(.*?)(?=\s*\bKhatib\s*:|$)", re.I)
LATIN_ARTI = re.compile(r'^(["“].+["”])\s*\((.+)\)\.?$')

CSS = """
  @import url('https://fonts.googleapis.com/css2?family=Amiri:ital,wght@0,400;0,700;1,400;1,700&family=Scheherazade+New:wght@400;700&display=swap');

  @page {
    size: A4;
    margin: 20mm 15mm;
    @bottom-center {
      content: "صفحة " counter(page) " من " counter(pages);
      font-family: 'Amiri', 'Scheherazade New', serif;
      font-size: 12pt;
      color: #555;
    }
  }

  body {
    font-family: 'Amiri', 'Scheherazade New', 'Traditional Arabic', serif;
    margin: 0;
    padding: 0;
    color: #1a1a1a;
    background-color: #ffffff;
    line-height: 2.0;
  }

  /* Page Break Separation */
  .page-break {
    page-break-after: always;
  }

  .header-container {
    text-align: center;
    border-bottom: 2px solid #0f5132;
    padding-bottom: 12px;
    margin-bottom: 25px;
  }

  .main-title {
    font-size: 30pt;
    font-weight: bold;
    color: #0f5132;
    margin: 0 0 8px 0;
    font-family: 'Amiri', serif;
  }

  .judul {
    font-size: 22pt;
    font-weight: bold;
    line-height: 1.4;
    color: #0f5132;
    margin: 0 0 8px 0;
    font-family: 'DejaVu Sans', 'Helvetica Neue', Arial, sans-serif;
    direction: ltr;
  }

  .sub-title {
    font-size: 14pt;
    color: #198754;
    margin: 0;
    font-family: 'DejaVu Sans', 'Helvetica Neue', Arial, sans-serif;
    direction: ltr;
  }

  .content-card {
    background-color: #fcfdfc;
    border: 1px solid #d1e7dd;
    border-right: 6px solid #0f5132;
    padding: 20px 25px;
    border-radius: 6px;
    margin-bottom: 20px;
  }

  .arabic-text {
    font-size: __ARAB_KHUTBAH__pt;
    line-height: 2.3;
    text-align: justify;
    direction: rtl;
    font-family: 'Amiri', 'Scheherazade New', serif;
  }

  .arabic-text p {
    margin: 0 0 0.5em 0;
  }

  .arabic-text p:last-child,
  .indo-text p:last-child {
    margin-bottom: 0;
  }

  /* Penutup khutbah pertama: jangan terpotong antarhalaman */
  .penutup {
    break-inside: avoid;
    text-align: center;
  }

  .indo-text {
    font-family: 'DejaVu Sans', 'Helvetica Neue', Arial, sans-serif;
    font-size: __INDO__pt;
    line-height: 1.8;
    text-align: justify;
    direction: ltr;
    color: #212529;
  }

  .indo-text p {
    margin: 0 0 0.9em 0;
    orphans: 2;
    widows: 2;
  }

  .indo-text p.pengantar {
    break-after: avoid;
  }

  /* Dalil (ayat / hadits): selalu jadi blok tersendiri */
  .dalil {
    margin: 1.1em 0 1.3em 0;
    padding: 14px 22px 12px 22px;
    background-color: #f1f8f4;
    border: 1px solid #d1e7dd;
    border-radius: 6px;
    break-inside: avoid;
  }

  .indo-text .dalil p {
    margin: 0 0 0.4em 0;
  }

  .indo-text .dalil p.arab {
    font-family: 'Amiri', 'Scheherazade New', serif;
    font-size: __ARAB_ISI__pt;
    line-height: 2.1;
    text-align: center;
    direction: rtl;
    color: #0f5132;
  }

  .dalil p.latin {
    font-weight: bold;
    font-style: italic;
  }

  .dalil p.arti {
    font-style: italic;
  }

  .indo-text .dalil p.sumber {
    text-align: right;
    font-size: 0.85em;
    font-weight: bold;
    color: #198754;
    margin-bottom: 0;
  }

  /* Lafaz seperti ﷺ di tengah kalimat Indonesia */
  .honorifik {
    font-family: 'Amiri', 'Scheherazade New', serif;
    font-size: 1.3em;
    line-height: 1;
  }

  .indo-text hr {
    border: none;
    border-top: 2px solid #d1e7dd;
    margin: 1.5em 20%;
  }

  .footer-note {
    margin-top: 30px;
    font-size: 10pt;
    color: #6c757d;
    direction: ltr;
    font-family: 'DejaVu Sans', 'Helvetica Neue', Arial, sans-serif;
    border-top: 1px solid #dee2e6;
    padding-top: 8px;
  }
"""


def baca_isi(path):
    """Baca file isi: baris 'Judul:' / 'Khatib:', lalu '---' (opsional), lalu isi khutbah.

    Juga menerima header yang rusak karena disalin dari tampilan markdown,
    mis. "## Judul: ... Khatib: ..." dalam satu baris tanpa '---'.
    """
    baris = path.read_text(encoding="utf-8").splitlines()
    info = {}
    i = 0
    while i < len(baris):
        b = baris[i].strip().lstrip("#*").strip()
        if not b:
            i += 1
            continue
        if b == "---":
            i += 1
            break
        if not HEADER.match(b):
            break
        for kunci, nilai in HEADER.findall(b):
            info[kunci.lower()] = nilai.strip().strip("*").strip()
        i += 1
    if not info.get("judul"):
        sys.exit(f"{path}: baris 'Judul: ...' tidak ditemukan di awal file.")
    return info["judul"], info.get("khatib", ""), baris[i:]


def potong_dalil(baris):
    """Pecah satu baris dalil menjadi daftar (jenis, teks): arab / latin / arti / sumber."""
    bagian = []
    sumber = SUMBER_AKHIR.search(baris)
    if sumber:
        baris = baris[: sumber.start()]
    for potongan in ARAB_RUN.split(baris):
        potongan = potongan.strip()
        if not potongan:
            continue
        if ARAB_RUN.fullmatch(potongan):
            bagian.append(("arab", potongan))
            continue
        if potongan.startswith("(") and potongan.endswith(")"):
            potongan = potongan[1:-1].strip()
        latin_arti = LATIN_ARTI.match(potongan)
        if latin_arti:
            bagian.append(("latin", latin_arti.group(1)))
            bagian.append(("arti", latin_arti.group(2).strip()))
        else:
            bagian.append(("arti", potongan))
    if sumber:
        bagian.append(("sumber", sumber.group(1).strip()))
    return bagian


def urai_isi(baris_isi):
    """Ubah baris isi menjadi blok: ("p", teks), ("hr",), atau ("dalil", bagian)."""
    baris_isi = [b.strip() for b in baris_isi]
    blok = []
    i = 0
    while i < len(baris_isi):
        b = baris_isi[i]
        i += 1
        if not b:
            continue
        if b == "***":
            blok.append(("hr",))
        elif b.startswith(">"):
            # Format standar: baris-baris berawalan ">" yang berurutan = satu dalil
            bagian = potong_dalil(b[1:])
            while i < len(baris_isi) and baris_isi[i].startswith(">"):
                bagian += potong_dalil(baris_isi[i][1:])
                i += 1
            blok.append(("dalil", bagian))
        elif ARAB_RUN.search(b):
            # Tanpa ">": teks Arab tetap dipisah jadi dalil, terjemahan di bawahnya ikut
            awal = ARAB_RUN.search(b).start()
            if b[:awal].strip():
                blok.append(("p", b[:awal].strip()))
            bagian = potong_dalil(b[awal:])
            while True:
                j = i
                while j < len(baris_isi) and not baris_isi[j]:
                    j += 1
                if j == len(baris_isi):
                    break
                jenis = {jenis for jenis, _ in bagian}
                lanjut = baris_isi[j]
                if lanjut.startswith(('"', "“")) and "arti" not in jenis:
                    pass
                elif SUMBER_AKHIR.fullmatch(lanjut) and "sumber" not in jenis:
                    pass
                else:
                    break
                bagian += potong_dalil(lanjut)
                i = j + 1
            blok.append(("dalil", bagian))
        else:
            blok.append(("p", b))
    return blok


def teks_ke_html(teks):
    teks = html.escape(teks, quote=False)
    return HONORIFIK.sub(lambda m: f'<span class="honorifik">{m.group()}</span>', teks)


def isi_ke_html(baris_isi):
    hasil = []
    blok = urai_isi(baris_isi)
    for i, (jenis, *nilai) in enumerate(blok):
        if jenis == "hr":
            hasil.append("<hr>")
        elif jenis == "p":
            # kalimat pengantar jangan terpisah halaman dari dalilnya
            pengantar = i + 1 < len(blok) and blok[i + 1][0] == "dalil"
            kelas = ' class="pengantar"' if pengantar else ""
            hasil.append(f"<p{kelas}>{teks_ke_html(nilai[0])}</p>")
        else:
            hasil.append('<div class="dalil">')
            for kelas, teks in nilai[0]:
                if kelas == "arab":
                    hasil.append(f'  <p class="arab" dir="rtl">{html.escape(teks, quote=False)}</p>')
                else:
                    hasil.append(f'  <p class="{kelas}">{teks_ke_html(teks)}</p>')
            hasil.append("</div>")
    return "\n    ".join(hasil)


def arab_ke_html(teks):
    paragraf = [p.strip().replace("\n", "<br>") for p in teks.split("\n\n")]
    return "\n    ".join(f"<p>{p}</p>" for p in paragraf if p)


def nama_file(judul):
    return re.sub(r'[\\/:*?"<>|]', "", judul).strip() or "khutbah"


def buat_html(judul, khatib, baris_isi):
    judul_html = html.escape(judul, quote=False)
    khatib_html = html.escape(khatib, quote=False)
    footer = " | ".join(x for x in (f"Khutbah Jum'at: {khatib_html}" if khatib else "Khutbah Jum'at", judul_html) if x)
    css = (
        CSS.replace("__ARAB_KHUTBAH__", str(UKURAN_ARAB_KHUTBAH))
        .replace("__ARAB_ISI__", str(UKURAN_ARAB_ISI))
        .replace("__INDO__", str(UKURAN_INDO))
    )
    khutbah_1_arab_html = arab_ke_html(khutbah_1_arab)
    penutup_khutbah_1_html = arab_ke_html(penutup_khutbah_1_arab)
    khutbah_2_arab_html = arab_ke_html(khutbah_2_arab)

    return f"""<!DOCTYPE html>
<html lang="ar">
<head>
<meta charset="UTF-8">
<title>{judul_html}</title>
<style>{css}</style>
</head>
<body>

<!-- BACAAN KHUTBAH PERTAMA -->
<div class="page-break">
  <div class="header-container">
    <div class="main-title" dir="rtl">الْخُطْبَةُ الأُولَى</div>
    <div class="sub-title">Bacaan Khutbah Pertama</div>
  </div>

  <div class="content-card arabic-text" dir="rtl">
    {khutbah_1_arab_html}
  </div>

  <div class="footer-note">{footer}</div>
</div>

<!-- ISI KHUTBAH -->
<div class="page-break">
  <div class="header-container">
    <div class="judul">{judul_html}</div>
    <div class="sub-title">{khatib_html}</div>
  </div>

  <div class="content-card indo-text">
    {isi_ke_html(baris_isi)}
  </div>

  <!-- PENUTUP KHUTBAH PERTAMA -->
  <div class="content-card arabic-text penutup" dir="rtl">
    {penutup_khutbah_1_html}
  </div>

  <div class="footer-note">{footer}</div>
</div>

<!-- BACAAN KHUTBAH KEDUA -->
<div>
  <div class="header-container">
    <div class="main-title" dir="rtl">الْخُطْبَةُ الثَّانِيَةُ</div>
    <div class="sub-title">Bacaan Khutbah Kedua &amp; Doa Penutup</div>
  </div>

  <div class="content-card arabic-text" dir="rtl">
    {khutbah_2_arab_html}
  </div>

  <div class="footer-note">{footer}</div>
</div>

</body>
</html>
"""


def main():
    file_isi = Path(sys.argv[1] if len(sys.argv) > 1 else FILE_ISI_DEFAULT)
    if not file_isi.exists():
        sys.exit(f"File isi tidak ditemukan: {file_isi}")
    folder_output = Path(sys.argv[2] if len(sys.argv) > 2 else FOLDER_OUTPUT_DEFAULT)
    folder_output.mkdir(parents=True, exist_ok=True)

    judul, khatib, baris_isi = baca_isi(file_isi)
    file_pdf = folder_output / f"{nama_file(judul)}.pdf"
    weasyprint.HTML(string=buat_html(judul, khatib, baris_isi)).write_pdf(file_pdf)
    print(f"PDF berhasil dibuat: {file_pdf}")


if __name__ == "__main__":
    main()
