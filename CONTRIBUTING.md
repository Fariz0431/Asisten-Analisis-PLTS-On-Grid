# Panduan kontribusi

1. Buat perubahan pada cabang terpisah.
2. Jelaskan tujuan perubahan dan file yang terpengaruh.
3. Tambahkan atau perbarui unit test untuk perubahan fungsi.
4. Jalankan `python -m pytest -q` sebelum membuat commit.
5. Jangan memasukkan API key, data sensitif, atau materi berhak cipta tanpa izin.
6. Perbarui README/dokumentasi jika konfigurasi atau perilaku aplikasi berubah.

Setiap perubahan retrieval perlu dievaluasi menggunakan sepuluh pertanyaan pada `tests/test_cases.json` agar perbandingan sebelum-sesudah dapat dilakukan.
