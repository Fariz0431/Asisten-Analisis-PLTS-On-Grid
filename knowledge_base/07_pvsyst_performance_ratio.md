DOC_ID: D7
SOURCE_URL: https://www.pvsyst.com/help/project-design/results/performance-ratio-pr.html
# Performance Ratio (PR) menurut dokumentasi PVsyst

**Jenis sumber:** dokumentasi teknis resmi PVsyst. Halaman diakses untuk penyusunan catatan pada 2 November 2026.

Untuk sistem grid-connected standar tanpa penyesuaian self-consumption/storage, dokumentasi PVsyst mendefinisikan Performance Ratio sebagai energi efektif yang diproduksi dibandingkan energi potensial pada daya nominal STC dan iradiasi bidang modul:

`PR = E_Grid / (GlobInc × PnomPV)`

Dalam rumus tersebut, `E_Grid` adalah energi yang disalurkan ke jaringan, `GlobInc` adalah iradiasi global pada bidang kolektor, dan `PnomPV` adalah daya terpasang STC. Satuan dan rentang waktu input harus konsisten. Untuk sistem dengan self-consumption dan/atau storage, PVsyst menjelaskan bahwa energi yang efektif dapat mencakup `E_Grid + E_Solar`; definisi energi tidak boleh disamakan secara otomatis untuk semua jenis sistem.

Dokumentasi juga menjelaskan bahwa PR merangkum pengaruh rugi optik, rugi array, dan rugi sistem. Nilai PR pada langkah waktu sangat pendek, khususnya pada sistem storage, perlu ditafsirkan hati-hati.

**Batas penggunaan:** rumus di atas dalam kalkulator prototipe hanya digunakan untuk sistem grid-connected standar. Periode `E_Grid` dan `GlobInc` harus sama dan `GlobInc` harus dinyatakan dalam kWh/m². Perhitungan ini tidak menentukan penyebab perubahan PR.

**Sumber asli:** [PVsyst – Performance Ratio PR](https://www.pvsyst.com/help/project-design/results/performance-ratio-pr.html).
