# Protokol Evaluasi Retrieval RAG

## Tujuan

Evaluasi dilakukan untuk mengukur apakah baseline TF-IDF dapat mengambil sumber yang ditargetkan dan apakah pertanyaan tanpa jawaban berpotensi memunculkan hasil yang tidak relevan.

## Komposisi pertanyaan

Sepuluh pertanyaan disediakan pada `tests/test_cases.json`:

- 6 pertanyaan dengan sumber jawaban yang diharapkan tersedia.
- 2 pertanyaan yang memerlukan informasi dari lebih dari satu sumber.
- 2 pertanyaan yang nilai jawabannya tidak tersedia: satu kasus identifier spesifik yang seharusnya tidak menghasilkan sumber generik, dan satu kasus nilai soiling aktual yang masih boleh mengambil konteks umum untuk mendukung penjelasan bahwa data lokasi belum tersedia.

## Metrik dan interpretasi

- **Target hit@k:** apakah salah satu dokumen target muncul pada top-k.
- **Top score:** skor cosine similarity tertinggi.
- **Jumlah hasil:** banyaknya chunk yang lolos threshold.
- **Negative query hit:** apakah retrieval tetap mengembalikan chunk untuk pertanyaan yang sengaja tidak tersedia. Hasil ini perlu ditinjau sebagai kandidat false positive. Pada pertanyaan nilai aktual, sumber umum dapat relevan untuk menjelaskan keterbatasan, tetapi tidak boleh dipakai untuk mengarang nilai aktual.

Evaluasi retrieval tidak sama dengan evaluasi kebenaran jawaban LLM. Kualitas jawaban generatif, ketepatan kutipan, dan abstain perlu diuji terpisah.

## Prosedur

1. Jalankan `python scripts/run_retrieval_evaluation.py`.
2. Buka `outputs/retrieval_evaluation.csv` dan `outputs/retrieval_evaluation.json`.
3. Periksa setiap sumber yang muncul pada sepuluh pertanyaan.
4. Catat false positive dan false negative beserta bukti dari teks sumber.
5. Ubah satu variabel pada satu waktu (misalnya threshold atau top-k), lalu ulangi evaluasi.
6. Jangan menyatakan konfigurasi terbaik sebelum hasilnya dibandingkan dengan seluruh pertanyaan.

## Pertanyaan negatif

Salah satu kasus adalah kode alarm perangkat yang manual/merek/modelnya tidak terdapat di knowledge base. Hasil retrieval bertema gangguan umum tidak boleh digunakan untuk menafsirkan kode alarm spesifik.

Kasus lainnya meminta nilai soiling aktual suatu instalasi tanpa data pengukuran. Artikel umum tentang soiling tidak menyediakan nilai aktual untuk instalasi tersebut.
