# Pemeriksaan paket source code

Catatan ini merekam pemeriksaan yang dilakukan saat paket repository disusun pada 2 November 2026. Pengembang tetap perlu mengulang pengujian pada perangkat dan lingkungan yang akan digunakan untuk demonstrasi.

## Pemeriksaan yang telah dilakukan pada paket ini

- Sintaks Python pada `app.py`, seluruh modul `plts_assistant/`, skrip, dan test berhasil dikompilasi dengan `py_compile`.
- Unit test lokal: **17 passed**.
- Skrip retrieval: **8 dokumen knowledge base**, **10 chunk**, dan **10 pertanyaan uji** terbaca.
- Seluruh target sumber yang ditetapkan pada 9 pertanyaan yang membutuhkan konteks ditemukan pada hasil top-k: **9/9 cakupan target**.
- Pertanyaan negatif kode alarm A999 tidak mengembalikan sumber generik karena identifier spesifik tersebut tidak terdapat pada teks knowledge base.
- Pertanyaan nilai soiling aktual tetap mengembalikan sumber konteks umum D5/D8. Sumber tersebut mendukung penjelasan tentang keterbatasan penentuan nilai, bukan angka soiling aktual untuk suatu lokasi.

## Pemeriksaan yang belum dilakukan

- Antarmuka Streamlit belum dijalankan dalam lingkungan penyusunan paket ini karena dependensi Streamlit tidak tersedia pada saat pemeriksaan. Jalankan instalasi sesuai README dan uji aplikasi di browser.
- Panggilan LLM end-to-end belum dilakukan. SDK/provider dan API key tidak dikonfigurasi; aplikasi diuji pada mode retrieval-only.
- Tidak ada klaim bahwa jawaban LLM, biaya provider, atau ketepatan diagnosis lapangan telah diuji.
- Enam catatan artikel D1–D6 belum diverifikasi terhadap naskah lengkap. Metadata dan ringkasan harus diperiksa oleh pengembang sebelum dikutip dalam laporan.

## Cara mengulang pemeriksaan

```bash
pip install -r requirements-dev.txt
python -m pytest -q
python scripts/run_retrieval_evaluation.py
streamlit run app.py
```

File evaluasi CSV/JSON dihasilkan pada folder `outputs/` setelah skrip dijalankan. File tersebut tidak disertakan sebagai hasil tetap agar tidak disalahartikan sebagai pengujian pada komputer pengembang.
