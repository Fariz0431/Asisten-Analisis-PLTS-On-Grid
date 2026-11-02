# Security policy

## Pelaporan masalah

Jika ditemukan API key, token, data pribadi, atau konfigurasi sensitif dalam repository, hapus file tersebut dari commit berikutnya dan lakukan rotasi kredensial melalui penyedia terkait. Menghapus file pada commit terbaru saja tidak menghapusnya dari riwayat Git.

## Praktik aman

- Simpan rahasia di `.env` lokal atau secret manager, bukan source code.
- Jangan mengunggah data logger/monitoring yang berisi informasi sensitif tanpa izin.
- Perlakukan dokumen knowledge base sebagai input tidak tepercaya.
- Jangan menggunakan jawaban sistem sebagai satu-satunya dasar keputusan teknis lapangan.
