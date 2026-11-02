# Rencana Pengembangan

Rencana berikut merupakan usulan tahapan lanjutan. Status setiap pekerjaan perlu diperbarui setelah bukti pengerjaan tersedia.

| Tahap | Pekerjaan | Bukti yang diharapkan |
|---|---|---|
| 1 | Melengkapi serta memverifikasi knowledge base | Daftar sumber, DOI/URL, catatan ringkas dan status verifikasi |
| 2 | Menguji sepuluh pertanyaan retrieval | CSV/JSON, catatan target hit, false positive/negative |
| 3 | Menguji skema keluaran dan kalkulator | Hasil unit test dan perhitungan pembanding manual |
| 4 | Mengaktifkan LLM opsional | Catatan konfigurasi provider tanpa membagikan API key, contoh keluaran dan validasi ID sumber |
| 5 | Menguji pertanyaan lintas dokumen dan negatif | Log jawaban, status abstain, dan evaluasi sumber |
| 6 | Perbaikan retrieval | Perbandingan sebelum-sesudah dengan pertanyaan yang sama |
| 7 | Finalisasi demo dan dokumentasi | Screenshot, langkah instalasi, batasan dan presentasi |

## Indikator penyelesaian

- Aplikasi dapat dijalankan dengan instruksi README.
- Unit test lulus pada lingkungan yang dicatat.
- Hasil evaluasi retrieval dapat direproduksi.
- LLM hanya dinyatakan aktif jika konfigurasi dan panggilan berhasil diuji.
- Jawaban menampilkan sumber valid atau menyatakan informasi tidak ditemukan/data belum cukup.
- Batasan sistem dan penggunaan sumber dijelaskan secara terbuka.
