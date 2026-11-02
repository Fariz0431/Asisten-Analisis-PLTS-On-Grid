# Asisten Analisis Kinerja dan Gangguan PLTS On-Grid

Proyek ini merupakan prototipe aplikasi berbasis Python dan Streamlit untuk membantu analisis awal kinerja PLTS On-Grid. Sistem menggabungkan pencarian dokumen menggunakan TF-IDF, kalkulator deterministik untuk PR/CUF/selisih energi, serta integrasi LLM opsional melalui endpoint yang kompatibel dengan API OpenAI.

> **Batasan penting:** aplikasi ini hanya membantu analisis awal berdasarkan dokumen dan angka yang dimasukkan. Aplikasi tidak melakukan diagnosis kerusakan definitif, pemantauan inverter secara real-time, perubahan setelan peralatan, atau pengendalian perangkat PLTS. Hasil harus diperiksa kembali terhadap sumber asli dan data lapangan.

## Fitur

- Pencarian potongan dokumen menggunakan TF-IDF sebagai baseline RAG.
- Metadata sumber, ID chunk, cuplikan, dan tautan rujukan ditampilkan bersama hasil.
- Status jawaban dibatasi menjadi `cukup_data`, `data_belum_cukup`, `informasi_tidak_ditemukan`, atau `perlu_verifikasi`.
- LLM bersifat opsional. Tanpa konfigurasi LLM, aplikasi hanya menampilkan hasil retrieval dan **tidak mengklaim sedang menghasilkan jawaban generatif**.
- Kalkulasi Performance Ratio (PR), Capacity Utilization Factor (CUF), dan selisih energi dilakukan oleh fungsi Python.
- Knowledge base awal terdiri atas enam catatan ringkas artikel dan dua catatan dokumentasi teknis PVsyst. Catatan artikel bukan salinan atau pengganti artikel asli.
- Pengujian unit dan skrip evaluasi retrieval disediakan.

## Struktur repository

```text
.
├── app.py
├── plts_assistant/
│   ├── calculator.py
│   ├── config.py
│   ├── documents.py
│   ├── llm.py
│   ├── pipeline.py
│   ├── retrieval.py
│   └── schemas.py
├── knowledge_base/       # 8 catatan sumber awal
├── tests/                # pengujian unit dan 10 pertanyaan evaluasi
├── scripts/              # skrip evaluasi retrieval
├── docs/                 # rancangan, batasan, dan catatan progres
├── outputs/              # keluaran evaluasi yang dihasilkan saat skrip dijalankan
├── .env.example
├── .gitignore
└── requirements.txt
```

## Persyaratan

- Python 3.10 atau lebih baru.
- pip dan akses internet untuk memasang dependensi serta (bila diperlukan) mengambil dokumentasi/data eksternal.
- Browser untuk membuka antarmuka Streamlit.

## Instalasi

### Windows (PowerShell)

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

## Menjalankan aplikasi

```bash
streamlit run app.py
```

Streamlit akan menampilkan alamat lokal pada terminal. Buka alamat tersebut melalui browser.

## Mengaktifkan LLM (opsional)

Aplikasi dapat dijalankan tanpa LLM. Untuk mengaktifkan generasi jawaban, isi `.env` dengan kredensial dan model dari provider yang menyediakan endpoint kompatibel:

```dotenv
LLM_API_KEY=isi_api_key_di_lingkungan_lokal
LLM_BASE_URL=
LLM_MODEL=
LLM_TIMEOUT_SECONDS=45
```

- `LLM_API_KEY` wajib diisi untuk mengaktifkan LLM.
- `LLM_MODEL` harus diisi dengan nama model yang benar-benar tersedia pada provider.
- `LLM_BASE_URL` boleh dikosongkan untuk endpoint default SDK, atau diisi dengan base URL dari provider kompatibel.
- Jangan pernah mengunggah `.env`, API key, token, atau kredensial ke repository publik.
- Provider, model, biaya, dan kebijakan retensi data perlu diperiksa sendiri sebelum digunakan.

Jika provider tidak dapat diakses, aplikasi akan menampilkan mode retrieval-only dan bukan hasil generasi LLM.

## Menjalankan pengujian

```bash
pip install -r requirements-dev.txt
python -m pytest -q
```

## Menjalankan evaluasi retrieval 10 pertanyaan

```bash
python scripts/run_retrieval_evaluation.py
```

Hasil CSV dan JSON akan ditulis ke `outputs/`. Skrip ini mengukur apakah sumber target muncul pada hasil retrieval. Untuk pertanyaan negatif, kemunculan sumber apa pun perlu ditinjau manual sebagai kandidat false positive. **Evaluasi retrieval tidak membuktikan kebenaran jawaban generatif atau diagnosis lapangan.**

## Rumus kalkulator

### Performance Ratio

Untuk sistem grid-connected tanpa penyesuaian self-consumption/storage, kalkulator menggunakan:

\[
PR = \frac{E_{Grid}}{GlobInc \times P_{nom,PV}}
\]

`E_Grid` dimasukkan dalam kWh, `GlobInc` dalam kWh/m² untuk periode yang sama, dan `P_nom,PV` dalam kWp. Hasil ditampilkan dalam persen. Pastikan definisi energi dan periode konsisten. PVsyst menjelaskan variasi energi efektif untuk sistem dengan self-consumption/storage pada dokumentasinya.

### Capacity Utilization Factor

\[
CUF = \frac{E_{actual}}{P_{installed}\times t}\times100\%
\]

Energi harus dalam kWh, kapasitas dalam kW, dan durasi dalam jam untuk periode yang sama.

### Selisih energi

\[
\Delta E = E_{actual}-E_{reference}
\]

Persentase selisih dihitung relatif terhadap energi referensi. Jika energi referensi nol, persentase tidak dihitung.

## Knowledge base dan kehati-hatian sumber

- `D1`–`D6` merupakan catatan ringkas berdasarkan metadata, abstrak/uraian relevansi dan daftar sumber yang tercantum pada dokumen rancangan proyek. Catatan tersebut bukan teks lengkap artikel dan tidak boleh dikutip sebagai kutipan langsung.
- `D7`–`D8` merupakan catatan dari dokumentasi resmi PVsyst untuk PR dan soiling loss.
- Artikel, versi dokumen, temuan, dan halaman/section harus diverifikasi pada sumber asli sebelum dijadikan dasar laporan akademik.
- PDF pindai tanpa lapisan teks tidak diproses dengan OCR. Ekstraksi PDF menggunakan `pypdf` hanya mengambil teks yang tersedia.
- Tambahkan dokumen hanya jika hak penggunaan dan sumbernya jelas. Jangan mengunggah naskah berhak cipta tanpa izin.

## Publikasi GitHub

Sebelum repository dijadikan Public:

1. Periksa `git status` dan isi file yang akan diunggah.
2. Pastikan `.env`, API key, kredensial, data monitoring pribadi, dan file sensitif tidak ikut terunggah.
3. Hindari menaruh NIM, nomor identitas, atau data pribadi pada README, screenshot, nama file, maupun log publik.
4. Periksa lisensi setiap dokumen pada `knowledge_base/`.
5. Jalankan pengujian lokal.
6. Isi README ini dengan screenshot aplikasi yang benar-benar sudah dibuat (opsional).

Contoh perintah Git:

```bash
git init
git branch -M main
git add .
git status
git commit -m "Initial commit: PLTS analysis assistant"
git remote add origin https://github.com/USERNAME/REPOSITORY.git
git push -u origin main
```

Ganti `USERNAME` dan `REPOSITORY` sesuai repository yang dibuat. Periksa kembali daftar file sebelum menjalankan `git push`.

## Status implementasi

Repository ini adalah paket awal yang dapat dijalankan dan diuji. Status provider LLM bergantung pada konfigurasi dan akses provider pengguna. Catatan knowledge base artikel masih berupa ringkasan, bukan telaah artikel lengkap. Hasil evaluasi aktual harus dibuat dengan menjalankan skrip; tidak ada angka evaluasi yang diklaim sebelum program dijalankan.

## Referensi teknis utama

- [PVsyst – Performance Ratio PR](https://www.pvsyst.com/help/project-design/results/performance-ratio-pr.html)
- [PVsyst – Soiling loss](https://www.pvsyst.com/help/project-design/array-and-system-losses/soiling-loss.html)
