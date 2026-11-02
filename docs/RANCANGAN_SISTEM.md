# Rancangan Sistem — Asisten Analisis Kinerja dan Gangguan PLTS On-Grid

## 1. Persoalan yang ditangani

Mahasiswa Teknik Elektro dan teknisi pemeliharaan PLTS dapat membutuhkan penelaahan data produksi, parameter kinerja, serta manual teknis untuk menyusun analisis awal. Informasi tersebut dapat tersebar di beberapa dokumen, sehingga pencarian dan perhitungan harus dilakukan secara terpisah.

Prototipe ini dirancang untuk menerima pertanyaan mengenai kinerja PLTS On-Grid, mengambil potongan dokumen yang relevan, menghitung PR/CUF atau selisih energi ketika data yang diperlukan diberikan, dan menampilkan sumber serta keterbatasan jawaban.

Sistem hanya digunakan untuk **analisis awal berbasis dokumen dan data input**. Sistem tidak menetapkan akar kerusakan, tidak memantau inverter secara real-time, tidak mengubah setelan peralatan, dan tidak menggantikan prosedur keselamatan atau pemeriksaan teknisi.

## 2. Alasan pendekatan AI generatif dan RAG

Pertanyaan pengguna dapat ditulis dengan variasi bahasa bebas. RAG dirancang agar konteks dari sejumlah dokumen dapat ditemukan tanpa mengharuskan pengguna mengetahui judul atau kata kunci yang persis. Model bahasa dapat digunakan untuk menyusun penjelasan berdasarkan konteks yang ditemukan.

Perhitungan PR, CUF, dan selisih energi tidak diserahkan kepada model bahasa. Perhitungan dilaksanakan oleh fungsi Python yang deterministik agar hasilnya dapat diuji ulang dan dibandingkan dengan perhitungan manual.

TF-IDF digunakan sebagai baseline retrieval leksikal. Model LLM merupakan komponen opsional. Saat LLM tidak dikonfigurasi, aplikasi hanya menampilkan potongan dokumen dan secara eksplisit menyebut mode retrieval-only; mode tersebut tidak disebut sebagai generasi AI.

## 3. Alur sistem

```text
Pertanyaan + data PLTS opsional
             |
             v
     Validasi input/satuan
             |
             v
  Retrieval TF-IDF pada knowledge base
             |
             v
  Pemeriksaan hasil retrieval dan threshold
        /                 \
  Tidak ditemukan       Ada kandidat
       |                    |
       v                    v
 Status tidak       Kalkulator Python bila
 ditemukan/data      input numerik tersedia
 belum cukup                |
                            v
                   LLM opsional (bila aktif)
                            |
                            v
                 Validasi schema dan ID sumber
                            |
                            v
             Jawaban + sumber + keterbatasan
```

## 4. Kendali keluaran

Keluaran mengikuti schema pada `plts_assistant/schemas.py`:

- `status`: `cukup_data`, `data_belum_cukup`, `informasi_tidak_ditemukan`, atau `perlu_verifikasi`.
- `ringkasan`: uraian singkat hasil analisis.
- `hasil_perhitungan`: nilai keluaran dari kalkulator bila tersedia.
- `temuan_dokumen`: poin yang disusun dari konteks retrieval.
- `sumber`: ID chunk, nama file, judul, cuplikan, URL, dan skor retrieval.
- `kemungkinan_penyebab`: hipotesis untuk pemeriksaan, bukan diagnosis final.
- `pemeriksaan_lanjutan`: data atau langkah verifikasi yang masih diperlukan.
- `keterbatasan`: informasi yang belum dapat dipastikan.

Setiap referensi yang diterima dari LLM diperiksa terhadap ID chunk yang benar-benar ditemukan oleh retrieval. Referensi yang tidak cocok tidak diterima sebagai sumber.

## 5. Tool yang digunakan

| Komponen | Fungsi | Batas penggunaan |
|---|---|---|
| Ekstraktor Markdown/TXT/PDF | Membaca dokumen dan mengambil teks | PDF pindai tanpa text layer tidak diproses dengan OCR |
| TF-IDF | Mengambil potongan yang mirip secara leksikal | Skor kemiripan tidak membuktikan kebenaran atau kecukupan sumber |
| Kalkulator Python | Menghitung PR, CUF, dan selisih energi | Tidak menentukan akar gangguan |
| LLM opsional | Menyusun penjelasan berdasarkan konteks | Tidak boleh mengarang data, arti alarm, atau klaim tanpa sumber |
| Pydantic | Memvalidasi struktur keluaran | Tidak menggantikan pemeriksaan teknis |

Aplikasi tidak memiliki koneksi ke logger, SCADA, API inverter, atau sistem kendali perangkat.

## 6. Keputusan desain dan alternatif

| Keputusan | Alternatif yang tidak dipilih | Alasan |
|---|---|---|
| Perhitungan menggunakan fungsi Python | Mengandalkan hitungan model bahasa | Fungsi deterministik dapat diuji dengan hitung manual dan test otomatis. |
| Menampilkan ID chunk dan cuplikan | Hanya daftar referensi umum | Pengguna dapat menelusuri bagian dokumen yang diambil. |
| Status belum cukup/tidak ditemukan | Selalu memberikan jawaban pasti | Mengurangi risiko klaim tanpa dukungan. |
| Analisis awal, bukan kontrol peralatan | Mengirim perintah ke inverter | Pengendalian fisik berada di luar ruang lingkup dan memerlukan prosedur keselamatan tersendiri. |
| TF-IDF sebagai baseline | Menganggap embedding pasti lebih baik | Kualitas retrieval harus diperiksa menggunakan pertanyaan uji. |

## 7. Rumus kalkulator

### Performance Ratio (PR)

Untuk sistem grid-connected standar tanpa penyesuaian self-consumption/storage, digunakan:

\[
PR = \frac{E_{Grid}}{GlobInc \times P_{nom,PV}}
\]

`E_Grid` dimasukkan dalam kWh, `GlobInc` dalam kWh/m², dan `PnomPV` dalam kWp. Periode ketiganya harus konsisten. Untuk sistem dengan self-consumption dan/atau storage, definisi energi efektif dapat berbeda; dokumentasi PVsyst menjelaskan penggunaan `E_Grid + E_Solar` pada kondisi tersebut.

### Capacity Utilization Factor (CUF)

\[
CUF = \frac{E_{actual}}{P_{installed}\times t}\times100\%
\]

Energi dinyatakan dalam kWh, daya dalam kW, dan durasi dalam jam untuk periode yang sama.

### Selisih energi

\[
\Delta E = E_{actual} - E_{reference}
\]

Persentase selisih dihitung relatif terhadap energi referensi. Persentase tidak didefinisikan jika energi referensi bernilai nol.

## 8. Grounding dan knowledge base

Knowledge base awal memuat delapan catatan: enam ringkasan relevansi artikel berdasarkan rancangan proyek dan dua ringkasan dokumentasi resmi PVsyst. Enam ringkasan artikel bukan salinan artikel lengkap dan tidak dapat dijadikan kutipan langsung. Artikel asli harus dibuka untuk memeriksa klaim, halaman, metode, dan hasil.

Pengaturan awal retrieval:

| Parameter | Nilai awal |
|---|---:|
| Ukuran chunk | 1.100 karakter |
| Overlap | 160 karakter |
| Top-k | 4 |
| Threshold | 0,12 |

Nilai tersebut adalah titik awal eksperimen, bukan parameter optimum yang telah dibuktikan. Detail penilaian sepuluh pertanyaan dijelaskan dalam `PROTOKOL_EVALUASI_RAG.md`.

## 9. Risiko dan mitigasi

| Risiko | Dampak | Mitigasi |
|---|---|---|
| Chunk tidak relevan terambil | Jawaban dapat menyimpang | Evaluasi top-k, threshold, dan pertanyaan negatif. |
| LLM menambah klaim tanpa sumber | Jawaban tidak dapat ditelusuri | Instruksi grounding, ID sumber, validasi, dan status abstain. |
| Input kalkulasi salah satuan/periode | Hasil numerik menyesatkan | Validasi nilai dan tampilkan satuan/periode yang harus konsisten. |
| Nilai soiling disimpulkan dari foto | Nilai tidak dapat dipertanggungjawabkan | Minta pengukuran/asumsi simulasi yang dapat ditelusuri. |
| Artikel umum dipakai untuk kode alarm | Interpretasi alarm berisiko salah | Minta manual merek dan model perangkat yang tepat. |
| Pengguna menganggap jawaban sebagai diagnosis final | Tindak lanjut dapat keliru | Tampilkan batasan dan minta pemeriksaan personel berwenang. |

## 10. Referensi teknis pendamping

- [PVsyst – Performance Ratio PR](https://www.pvsyst.com/help/project-design/results/performance-ratio-pr.html)
- [PVsyst – Soiling loss](https://www.pvsyst.com/help/project-design/array-and-system-losses/soiling-loss.html)
