# Perencanaan Stok dan Pembelian

**Prakiraan Permintaan dan Stok Pengaman untuk Toko Grosir** (*Demand Forecasting and Inventory Planning Dashboard*)

Dashboard interaktif yang menjawab: **berapa yang akan laku dalam 5 minggu ke depan, dan berapa stok yang perlu disiapkan agar kecil kemungkinan kehabisan, tanpa menumpuk modal di gudang.**

**[Buka dashboard](https://demand-forecasting-and-inventory-planning-dashboard-6vagug5ybx.streamlit.app/)**

## Ringkasan singkat (untuk pembaca non-teknis)

- **Masalah:** toko grosir harus memesan barang sebelum tahu berapa yang akan laku. Terlalu sedikit membuat pembeli kecewa karena kehabisan; terlalu banyak membuat uang tertahan di gudang.
- **Yang dibuat:** perkiraan penjualan 5 minggu ke depan per kategori dan per barang, beserta jumlah stok yang perlu disiapkan agar kemungkinan kehabisan hanya 5%.
- **Hasil:** angka per kategori lebih akurat daripada angka per barang (selisihnya ada di dashboard); angka per barang sulit ditebak, sehingga tiap barang diberi stok cadangan. Dibanding aturan umum "simpan stok setara 8 minggu penjualan", cara ini 17% lebih murah pada simulasi ulang dan lebih jarang kehabisan (94% vs 86% permintaan terpenuhi).

## Yang bisa dilakukan di dashboard

- **Ringkasan:** jawaban dalam satu kalimat, perbandingan per kategori (tahun lalu, terakhir, prakiraan), dan barang yang paling perlu disiapkan.
- **Prakiraan kategori** dan **Detail barang:** grafik mingguan dengan prakiraan, perbandingan dengan periode lain, dan stok yang aman pada 90%, 95%, dan 99%.
- **Rencana pembelian:** isi atau unggah posisi stok, dapatkan daftar pesanan yang bisa diunduh.
- **Seberapa aman stok:** berapa tambahan modal bila ingin lebih aman.
- **Bukti teknis**, **Metode dan batasan**, dan **Cara penggunaan** (langkah singkat dan cara membaca grafik).

## Hasil utama

Data: 4.700 barang, 104 minggu, sekitar 60% sel barang-minggu bernilai nol.

1. **Ramalan rata-rata sulit diperbaiki.** SES dan rata-rata bergerak 4 minggu terbaik (WAPE 0,554 dan 0,570). Gradient boosting (GBM) tidak lebih akurat (0,587).
2. **Nilai GBM ada di kuantilnya.** Pada target layanan 95%, hit rate GBM kuantil 95,1%, sedangkan normal klasik hanya 87,9%. Dibanding rasio galat SES yang juga tepat sasaran (95,7%), GBM butuh stok sekitar 40% lebih sedikit (2,4 vs 4,0 kali permintaan).
3. **Cara berbasis data mengalahkan aturan praktis.** Pada simulasi ulang 15 minggu, aturan "simpan stok setara 8 minggu penjualan" lebih mahal 20% (selang selisih £54 ribu sampai £97 ribu) dengan fill rate 85,6%, dibanding 94,3% pada GBM kuantil 95%. Aturan praktis tidak termurah di satu pun dari 27 skenario asumsi biaya.
4. **Kebijakan termurah bergantung pada asumsi.** GBM kuantil 95% termurah pada asumsi dasar (selisih dengan normal klasik £20 ribu, selang 95% £6 ribu sampai £35 ribu), tetapi normal klasik termurah di 10 dari 27 skenario, terutama saat margin tipis, namun fill rate-nya hanya 89,4%.
5. **Tingkat layanan per kelas ABC tidak terbukti lebih baik** daripada tingkat seragam, dan pilihannya tidak stabil.
6. **Biaya layanan naik tajam di ujung atas.** Nilai stok pengaman untuk barang aktif: £413 ribu (90%), £844 ribu (95%), £2,30 juta (99%).

## Data

[Online Retail II](https://archive.ics.uci.edu/dataset/502/online+retail+ii) (UCI Machine Learning Repository, lisensi CC BY 4.0): transaksi toko online grosir di Inggris, 1 Desember 2009 sampai 9 Desember 2011. Retur dan pesanan yang dibatalkan dikeluarkan; minggu libur akhir tahun ditandai tutup.

## Metode

1. Permintaan mingguan per barang pada sumbu kalender penuh. Kelas ABC dan pola permintaan (ADI dan CV²) dihitung hanya dari data sebelum titik prakiraan, tanpa kebocoran waktu.
2. Ramalan: rata-rata bergerak, SES, Croston-SBA, musiman naif, dan gradient boosting (loss Poisson), diuji mundur pada 9 titik awal bergulir dengan model dilatih ulang per lipatan.
3. Stok pengaman: normal klasik, rasio galat SES empiris, dan kuantil langsung dari gradient boosting.
4. Jumlah pesan memakai EOQ. Simulasi persediaan (s, nQ) dengan tinjau mingguan dan lead time 4 minggu.
5. Ketidakpastian: bootstrap antar barang dan sensitivitas pada 27 skenario asumsi biaya.

## Asumsi (tidak ada di data)

Lead time seragam 4 minggu; biaya pokok 60% dari harga jual; biaya simpan 20% per tahun; biaya pesan £30; penjualan yang tak terpenuhi hilang. Permintaan yang terobservasi adalah penjualan, bukan permintaan murni.

## Keterbatasan

- Satu perusahaan di Inggris, dua tahun data. Pola musiman per barang tidak stabil.
- Tidak ada data stok, pemasok, atau lead time asli; hasil biaya mengikuti asumsi.
- Bootstrap memperhitungkan variasi antar barang, bukan antar waktu; simulasi hanya satu jendela yang berisi musim puncak.
- Kuantil nominal bukan jaminan; jalankan ulang rutin bila permintaan bergeser.
- Belum memodelkan diskon kuantitas, kapasitas gudang, dan barang pengganti.

## Struktur

```
app.py                       dashboard Streamlit
requirements.txt             dependensi
Stok_revisi_final.ipynb      pengolahan data, model, simulasi, ekspor hasil
.streamlit/config.toml       tema
data/hasil/                  hasil olahan yang dibaca dashboard (rencana_pembelian, riwayat_mingguan,
                             prakiraan_kategori, riwayat_kategori, ringkasan.json,
                             simulasi_bootstrap.csv, sensitivitas_biaya.csv)
```

Kategori produk tidak ada di data; dibuat dari kata kunci pada deskripsi (aturan sederhana, bukan kategori resmi). Data mentah tidak disertakan. Unduh Online Retail II, lalu jalankan notebook dari atas; sel terakhir menulis ke `data/hasil/`.

## Menjalankan

```
pip install -r requirements.txt
streamlit run app.py
```

## Sumber

Chen, D. (2019). Online Retail II [Dataset]. UCI Machine Learning Repository. CC BY 4.0.
