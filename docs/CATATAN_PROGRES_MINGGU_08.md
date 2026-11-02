# Catatan Proses — Minggu 8

> Catatan ini disusun ulang dari dokumen progres yang diberikan. Isinya merekam klaim dan temuan pada catatan awal; hasilnya belum otomatis menjadi bukti bahwa versi repository ini telah menjalankan seluruh pengujian yang sama.

## 1. Pekerjaan yang dicatat

Pada catatan Minggu 8, paket proyek dinyatakan telah memiliki rancangan sistem, rancangan RAG, aplikasi Streamlit, enam ringkasan bacaan jurnal, skrip retrieval, tabel hasil uji, dan unit test awal. Arsip pembaruan yang menjadi dasar pembuatan repository ini hanya memuat dua dokumen Markdown rancangan dan catatan proses. Oleh karena itu, file implementasi yang disebutkan pada catatan lama tidak dianggap tersedia sebelum dibuat ulang dan diuji pada repository ini.

## 2. Temuan retrieval awal yang dicatat

Baseline TF-IDF pada enam ringkasan artikel dilaporkan menggunakan `top-k = 4` dan threshold `0,12`, dengan 12 chunk. Catatan sumber menyebut empat pertanyaan mengambil sumber target pada top-k:

| Kasus | Target yang diharapkan | Hasil yang dicatat |
|---|---|---|
| Metode AI untuk diagnosis gangguan PV grid-connected | D1 | D1 menjadi top hit, skor tercatat 0,3598 |
| Validasi dan kalibrasi model deteksi gangguan | D3 | D3 menjadi top hit, skor tercatat 0,2485 |
| Metode estimasi soiling | D5 | D5 menjadi top hit, skor tercatat 0,2876 |
| Analisis data kinerja untuk diagnosis | D4 | D4 menjadi top hit, skor tercatat 0,2314 |
| Persentase soiling aktual tanpa pengukuran | Tidak boleh menghasilkan angka aktual | D5 dan D6 terambil; perilaku abstain LLM belum diuji |
| Arti alarm A999 tanpa manual/model perangkat | Tidak ditemukan | D4 skor 0,1846 dan D2 skor 0,1525; dicatat sebagai false positive |

Nilai tersebut merupakan angka yang tertulis pada catatan proses terdahulu, bukan hasil pengujian ulang pada repository ini. Pengujian ulang perlu dilakukan melalui `scripts/run_retrieval_evaluation.py`.

## 3. Kesimpulan sementara

TF-IDF dapat mengembalikan potongan yang memiliki kemiripan kata dengan query, tetapi kecocokan leksikal tidak selalu berarti isi chunk menjawab pertanyaan. Kasus alarm A999 dicatat sebagai contoh false positive. Threshold yang dinaikkan dapat mengurangi kandidat tidak relevan, tetapi juga berpotensi menghilangkan hasil yang sebenarnya relevan.

## 4. Pekerjaan yang masih perlu dilakukan

- Menjalankan ulang aplikasi dan unit test pada lingkungan pengembangan.
- Memverifikasi isi enam artikel pada naskah asli.
- Menguji sepuluh pertanyaan sesuai protokol.
- Membandingkan threshold dan/atau retrieval semantik secara terukur.
- Menguji LLM secara end-to-end bila provider tersedia.
- Membuktikan perilaku abstain pada pertanyaan yang tidak mempunyai sumber.
- Menambahkan screenshot dan hasil eksperimen yang benar-benar dihasilkan.
