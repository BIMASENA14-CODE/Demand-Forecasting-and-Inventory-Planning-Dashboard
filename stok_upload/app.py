import html
import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Perencanaan Stok dan Pembelian", layout="wide")

QG = [0.5, 0.8, 0.9, 0.95, 0.975, 0.99]
HIJAU, EMAS, KREM, TEKS = "#33504a", "#c9971c", "#e8eeeb", "#1f3a35"
SALMON, H2, H3, ABU, BIRU = "#f2a07b", "#4f8f3a", "#8bbf5a", "#c4cac8", "#cfe2f3"
NAMA_KEBIJAKAN = {"0": "Aturan praktis (8 minggu)", "1": "Tanpa stok pengaman", "2": "Normal klasik 95%",
                  "3": "Rasio SES empiris 95%", "4": "GBM kuantil 95% seragam", "5": "GBM per kelas (fill rate)",
                  "6": "GBM per kelas (biaya min.)"}
BULAN = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
IK = {
    "kotak": '<path d="M3 7l9-4 9 4v10l-9 4-9-4V7z"/><path d="M3 7l9 4 9-4M12 11v10"/>',
    "perisai": '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6l8-3z"/><path d="M8.5 12l2.5 2.5L16 9.5"/>',
    "label": '<path d="M4 12L12 4h8v8l-8 8-8-8z"/><circle cx="16" cy="8" r="1.3"/>',
    "koin": '<ellipse cx="12" cy="6" rx="7" ry="3"/><path d="M5 6v6c0 1.7 3.1 3 7 3s7-1.3 7-3V6M5 12v6c0 1.7 3.1 3 7 3s7-1.3 7-3v-6"/>',
    "target": '<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="4"/><circle cx="12" cy="12" r="1"/>',
}

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');
html, body, .stApp, [data-testid="stMarkdownContainer"], label, p, li, td, th, input, button {font-family: 'Poppins', sans-serif;}
.stApp {background: #e8eeeb;}
[data-testid="stHeader"] {background: transparent;}
.block-container {padding-top: 1.6rem; max-width: 1320px;}
[data-testid="stSidebar"] {background: #2f4a45;}
[data-testid="stSidebar"] * {color: #e8eeeb;}
[data-testid="stSidebarNav"] a[aria-current="page"] {background: rgba(255,255,255,.14); border-radius: 10px;}
[class*="st-key-kartu"] {background: #fff; border-radius: 22px; padding: 18px 22px; box-shadow: 0 2px 10px rgba(31,58,53,.08);}
[class*="st-key-gelap"] {background: #33504a; border-radius: 22px; padding: 18px 22px; box-shadow: 0 2px 10px rgba(31,58,53,.15);}
[class*="st-key-gelap"] p, [class*="st-key-gelap"] label {color: #fff;}
.kepala {background: #33504a; border-radius: 22px; padding: 20px 30px; display: flex; align-items: center; gap: 34px; margin-bottom: 14px;}
.kepala .per span {display: block; color: #e0b23c; font-weight: 600; font-size: .95rem;}
.kepala .per b {color: #fff; font-size: 1.15rem; font-weight: 600;}
.kepala .jud {border-left: 2px solid rgba(255,255,255,.7); padding-left: 26px;}
.kepala .jud div {color: #fff; font-size: 1.7rem; font-weight: 700; letter-spacing: .5px; line-height: 1.15;}
.kepala .jud p {color: #e0b23c; margin: 2px 0 0 0; font-size: .95rem; font-weight: 500;}
.kpi {background: #fff; border-radius: 20px; padding: 16px 18px; display: flex; gap: 14px; align-items: center; box-shadow: 0 2px 10px rgba(31,58,53,.08); min-height: 104px;}
.kpi .ik {width: 46px; height: 46px; border-radius: 12px; background: #f5ecd2; display: flex; align-items: center; justify-content: center; flex: none;}
.kpi svg {width: 26px; height: 26px; fill: none; stroke: #c9971c; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round;}
.kpi .kl {font-weight: 600; font-size: .86rem; color: #33504a;}
.kpi .kv {font-weight: 700; font-size: 1.55rem; color: #1f3a35; line-height: 1.2;}
.kpi .kk {font-size: .72rem; color: #7b8c88;}
.jk {font-weight: 600; font-size: .98rem; color: #1f3a35; margin-bottom: 6px;}
.jk:before {content: ""; display: inline-block; width: 9px; height: 9px; border-radius: 50%; background: #c9971c; margin-right: 8px;}
.gelap-j {color: #fff;}
.sub {color: #c9971c; font-weight: 600; font-size: 1.05rem; margin: 8px 0 4px 0;}
.baris {display: flex; justify-content: space-between; align-items: center; margin: 6px 0; font-size: .9rem; color: #1f3a35;}
.pil {background: #cfe2f3; border-radius: 8px; padding: 2px 12px; font-weight: 600; min-width: 74px; text-align: center; color: #1f3a35;}
.hero {color: #fff; font-size: 1.12rem; line-height: 1.7;}
.hero b {color: #e0b23c; font-weight: 700;}
.info {font-size: .88rem; line-height: 1.6; color: #1f3a35;}
.info b.t {display: block; color: #c9971c; font-weight: 700; margin-bottom: 2px; font-size: .95rem;}
.temu {border-left: 3px solid #c9971c; padding: 2px 0 2px 14px; margin: 9px 0; line-height: 1.6; font-size: .93rem;}
h2, h3 {font-weight: 600 !important; color: #1f3a35;}
</style>""", unsafe_allow_html=True)


def tema(fig, h=None, gelap=False):
    w = "#ffffff" if gelap else TEKS
    g = "rgba(255,255,255,.16)" if gelap else "rgba(31,58,53,.10)"
    fig.update_layout(template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font=dict(color=w, size=12, family="Poppins, sans-serif"), margin=dict(l=6, r=6, t=14, b=6),
                      legend=dict(title=None, bgcolor="rgba(0,0,0,0)"))
    fig.update_xaxes(gridcolor=g, zerolinecolor=g, linecolor=g)
    fig.update_yaxes(gridcolor=g, zerolinecolor=g, linecolor=g)
    if h:
        fig.update_layout(height=h)
    return fig


def bulan(t):
    t = pd.Timestamp(t)
    return f"{BULAN[t.month - 1]} {t.year}"


def kepala(judul, sub):
    p = f"{bulan(D['periode'][0])} - {bulan(D['periode'][1])}"
    st.markdown(f'<div class="kepala"><div class="per"><span>Periode data</span><b>{p}</b></div>'
                f'<div class="jud"><div>{html.escape(judul)}</div><p>{html.escape(sub)}</p></div></div>', unsafe_allow_html=True)


def jk(teks, gelap=False):
    st.markdown(f'<div class="jk {"gelap-j" if gelap else ""}">{html.escape(teks)}</div>', unsafe_allow_html=True)


def kpi_baris(items):
    for c, (ik, jud, nilai, ket) in zip(st.columns(len(items)), items):
        c.markdown(f'<div class="kpi"><div class="ik"><svg viewBox="0 0 24 24">{IK[ik]}</svg></div><div>'
                   f'<div class="kl">{html.escape(jud)}</div><div class="kv">{html.escape(str(nilai))}</div>'
                   f'<div class="kk">{html.escape(ket)}</div></div></div>', unsafe_allow_html=True)


def temuan(t):
    st.markdown(f'<div class="temu">{t}</div>', unsafe_allow_html=True)


def cari(nama):
    for p in [Path("data/hasil"), Path(__file__).parent / "data/hasil", Path(__file__).parent.parent / "data/hasil"]:
        if (p / nama).exists():
            return p / nama
    return None


@st.cache_data
def muat():
    rencana = pd.read_parquet(cari("rencana_pembelian.parquet"))
    riw = pd.read_parquet(cari("riwayat_mingguan.parquet"))
    R = json.load(open(cari("ringkasan.json"), encoding="utf-8"))
    boot = pd.read_csv(cari("simulasi_bootstrap.csv"), index_col=0)
    sens = pd.read_csv(cari("sensitivitas_biaya.csv"))
    pk = pd.read_parquet(cari("prakiraan_kategori.parquet"))
    rk = pd.read_parquet(cari("riwayat_kategori.parquet"))
    return rencana, riw, R, boot, sens, pk, rk


if any(cari(f) is None for f in ["rencana_pembelian.parquet", "riwayat_mingguan.parquet", "ringkasan.json",
                                 "simulasi_bootstrap.csv", "sensitivitas_biaya.csv", "prakiraan_kategori.parquet", "riwayat_kategori.parquet"]):
    st.error("File hasil belum lengkap di data/hasil. Jalankan notebook sampai sel terakhir (bagian 11).")
    st.stop()
rencana, riw, R, boot, sens, pk, rk = muat()
P, D = R["parameter"], R["data"]
K, FW = R["kategori"], R["minggu_depan"]
kurva = pd.DataFrame(R["kurva_layanan"])


def nama_k(idx):
    return NAMA_KEBIJAKAN.get(str(idx).split(".")[0], str(idx))


def rp(x):
    return f"£{x / 1e6:.2f} jt" if abs(x) >= 1e6 else f"£{x / 1e3:,.0f} rb" if abs(x) >= 1e4 else f"£{x:,.0f}"


def ringkas_pilihan():
    ref = boot["selisih_vs_terbaik"].abs().idxmin()
    prak = boot.index[boot.index.str.startswith("0.")][0]
    return ref, prak


def pct(a, b):
    return (a / b - 1) * 100 if b and b > 0 else float("nan")


def fpct(x):
    return "-" if pd.isna(x) else f"{x:+.0f}%"


def tanggal(t):
    t = pd.Timestamp(t)
    return f"{t.day} {BULAN[t.month - 1]} {t.year}"


def periode_depan():
    a, b = pd.Timestamp(FW[0]["minggu"]), pd.Timestamp(FW[-1]["minggu"]) + pd.Timedelta(days=6)
    return f"{tanggal(a)} sampai {tanggal(b)}"


def grafik_mingguan(hist, prak_total, tinggi=330):
    h = hist.sort_values("minggu").tail(52)
    buka = [w for w in FW if w["buka"]]
    rata = prak_total / max(len(buka), 1)
    fig = go.Figure()
    fig.add_bar(x=h["minggu"], y=h["unit"], marker_color=HIJAU, name="Penjualan nyata")
    fig.add_bar(x=[w["minggu"] for w in FW], y=[rata if w["buka"] else 0 for w in FW], marker_color=EMAS, name="Prakiraan")
    fig.update_xaxes(type="date")
    fig.update_layout(yaxis_title="unit per minggu", xaxis_title=None, legend=dict(orientation="h", y=1.12), bargap=.15)
    return tema(fig, tinggi)


def tiga_batang(tl, tr, pr, wape=None, tinggi=330):
    err = [0, 0, pr * wape if wape is not None and not pd.isna(wape) else 0]
    fig = go.Figure(go.Bar(x=["Periode sama<br>tahun lalu", f"{H_} minggu<br>terakhir", f"Prakiraan {H_} minggu<br>ke depan"], y=[tl, tr, pr],
                           marker_color=[ABU, HIJAU, EMAS], text=[f"{v:,.0f}" for v in (tl, tr, pr)], textposition="outside",
                           error_y=dict(type="data", array=err, visible=True, color=TEKS, thickness=1.5), cliponaxis=False))
    fig.update_yaxes(range=[0, max(tl, tr, pr + err[2]) * 1.25 + 1], title="unit")
    return tema(fig, tinggi)


H_ = P["H"]


# ================= halaman 1: ringkasan =================
def hal_ringkasan():
    kepala("Rencana Stok dan Pembelian", f"Apa yang perlu disiapkan untuk {H_} minggu ke depan")
    k1, k2, k3 = st.columns(3)
    with k1:
        with st.container(key="kartu_masalah"):
            st.markdown('<div class="info"><b class="t">Masalahnya</b>Toko grosir harus memesan barang sebelum tahu berapa yang akan laku. '
                        'Terlalu sedikit: pembeli kecewa karena kehabisan. Terlalu banyak: uang tertahan di gudang.</div>', unsafe_allow_html=True)
    with k2:
        with st.container(key="kartu_data_info"):
            st.markdown(f'<div class="info"><b class="t">Datanya</b>Transaksi nyata sebuah toko grosir online di Inggris, {bulan(D["periode"][0])} sampai '
                        f'{bulan(D["periode"][1])}: {D["jumlah_barang"]:,} jenis barang, dikelompokkan ke {K["jumlah_kategori"]} kategori.</div>', unsafe_allow_html=True)
    with k3:
        with st.container(key="kartu_hasil_info"):
            st.markdown(f'<div class="info"><b class="t">Hasilnya</b>Perkiraan penjualan {H_} minggu ke depan per kategori dan per barang, '
                        'beserta jumlah stok yang perlu disiapkan agar kecil kemungkinan kehabisan.</div>', unsafe_allow_html=True)
    st.write("")
    t_prak, t_akhir, t_tl = pk["prakiraan_unit"].sum(), pk["terakhir_unit"].sum(), pk["tahun_lalu_unit"].sum()
    nilai, sasaran, biaya = pk["prakiraan_nilai"].sum(), pk["sasaran_unit"].sum(), pk["sasaran_biaya"].sum()
    with st.container(key="gelap_hero"):
        st.markdown(f'<div class="hero">Untuk <b>{periode_depan()}</b>, toko diperkirakan menjual sekitar <b>{t_prak:,.0f} unit</b> '
                    f'senilai <b>{rp(nilai)}</b>. Agar peluang kehabisan stok hanya 5%, siapkan sekitar <b>{sasaran:,.0f} unit</b> '
                    f'(modal sekitar <b>{rp(biaya)}</b>) untuk barang-barang yang masih laku.</div>', unsafe_allow_html=True)
    st.write("")
    besar = pk.sort_values("prakiraan_unit", ascending=False).iloc[0]
    kpi_baris([("kotak", f"Prakiraan penjualan {H_} minggu", f"{t_prak:,.0f} unit", f"senilai {rp(nilai)}"),
               ("label", f"Dibanding {H_} minggu terakhir", fpct(pct(t_prak, t_akhir)), f"{t_akhir:,.0f} unit"),
               ("target", "Dibanding periode sama tahun lalu", fpct(pct(t_prak, t_tl)), f"{t_tl:,.0f} unit"),
               ("koin", "Kategori terbesar", besar["kategori"], f"{besar['prakiraan_unit'] / t_prak * 100:.0f}% dari total")])
    st.write("")
    kiri, kanan = st.columns([3, 2])
    with kiri:
        with st.container(key="kartu_kategori"):
            jk("Penjualan per kategori: tahun lalu, terakhir, dan prakiraan")
            s = pk.sort_values("prakiraan_unit")
            fig = go.Figure()
            for kol, nama, w in [("tahun_lalu_unit", "Periode sama tahun lalu", ABU), ("terakhir_unit", f"{H_} minggu terakhir", HIJAU),
                                 ("prakiraan_unit", f"Prakiraan {H_} minggu ke depan", EMAS)]:
                fig.add_bar(y=s["kategori"], x=s[kol], name=nama, orientation="h", marker_color=w)
            fig.update_layout(barmode="group", xaxis_title="unit", legend=dict(orientation="h", y=1.1), bargap=.25)
            st.plotly_chart(tema(fig, 470), width="stretch")
            st.caption("Cara membaca: tiap kategori punya tiga batang. Batang emas adalah perkiraan untuk beberapa minggu ke depan. "
                       "Bandingkan dengan batang hijau (baru saja terjadi) dan abu-abu (periode yang sama tahun lalu).")
    with kanan:
        with st.container(key="kartu_top"):
            jk("Barang yang paling perlu disiapkan")
            t = rencana.nlargest(10, "prak_nilai")
            st.dataframe(pd.DataFrame({"Barang": t["deskripsi"].str.title().str[:32], "Kategori": t["kategori"],
                                       "Prakiraan (unit)": t["prak_unit"].round(0).astype(int),
                                       "Siapkan (unit)": t["sasaran_unit"].round(0).astype(int)}), hide_index=True, width="stretch", height=420)
            st.caption("Diurutkan menurut nilai penjualan yang diperkirakan. 'Siapkan' = stok sasaran agar 95% aman dari kehabisan.")
    a1, a2 = st.columns([2, 3])
    with a1:
        with st.container(key="kartu_akurasi_sederhana"):
            jk("Seberapa dekat prakiraan dengan kenyataan?")
            m = K["metode"]
            wi, wk = K["wape_item"][m] * 100, K["wape_kategori"][m] * 100
            fig = go.Figure(go.Bar(x=["Per barang", "Per kategori"], y=[wi, wk], marker_color=[ABU, EMAS],
                                   text=[f"{wi:.0f}%", f"{wk:.0f}%"], textposition="outside", cliponaxis=False))
            fig.update_yaxes(range=[0, wi * 1.3], title="rata-rata meleset (%)")
            st.plotly_chart(tema(fig, 280), width="stretch")
            st.caption("Diuji pada beberapa periode lampau. Makin pendek batang, makin akurat.")
    with a2:
        with st.container(key="kartu_arti"):
            jk("Artinya apa?")
            ref, prak = ringkas_pilihan()
            b = boot
            hemat = b.loc[prak, "selisih_vs_terbaik"] / b.loc[prak, "biaya_total"] * 100
            if wk <= 30:
                temuan(f"<b>Angka per kategori bisa dipakai untuk perencanaan.</b> Rata-rata meleset sekitar {wk:.0f}%.")
            else:
                temuan(f"<b>Angka per kategori lebih akurat daripada per barang, tetapi masih kasar</b> (rata-rata meleset sekitar {wk:.0f}%). Pakai sebagai arah, bukan angka pasti.")
            temuan(f"<b>Angka per barang sulit ditebak</b> (meleset sekitar {wi:.0f}%), karena pembeli grosir memesan dalam jumlah besar dan tidak teratur. "
                   "Karena itu tiap barang diberi stok cadangan, bukan hanya angka perkiraan.")
            temuan(f"<b>Cara ini lebih hemat.</b> Pada simulasi ulang, dibanding aturan umum 'simpan stok setara 8 minggu penjualan', "
                   f"biaya total {hemat:.0f}% lebih rendah dan permintaan yang terpenuhi {b.loc[ref, 'fill_rate'] * 100:.0f}% (aturan umum: {b.loc[prak, 'fill_rate'] * 100:.0f}%).")


# ================= halaman 2: cara penggunaan =================
def hal_cara():
    kepala("Cara Penggunaan", "Lima langkah singkat memakai dashboard ini")
    with st.container(key="kartu_langkah"):
        jk("Langkah")
        st.markdown(f"""
1. Mulai dari **Ringkasan**. Kalimat di kotak hijau tua adalah jawabannya: berapa yang diperkirakan terjual dan berapa yang perlu disiapkan.
2. Buka **Prakiraan kategori** untuk melihat satu kategori lebih dekat.
3. Buka **Detail barang** untuk satu barang tertentu: berapa perkiraannya dan berapa stok yang aman.
4. Punya data stok? Buka **Rencana pembelian**, isi posisi stok, dan dapatkan daftar barang yang perlu dipesan.
5. **Seberapa aman stok** dan **Bukti teknis** untuk yang ingin tahu biayanya dan seberapa kuat hasilnya.
""")
    with st.container(key="kartu_baca"):
        jk("Cara membaca grafik")
        st.markdown(f"""
- **Batang tiga warna** (abu-abu, hijau, emas): periode yang sama tahun lalu, {H_} minggu terakhir, dan prakiraan {H_} minggu ke depan. Garis kecil di batang emas adalah rentang ketidakpastian.
- **Grafik mingguan**: batang hijau adalah penjualan nyata tiap minggu, batang emas di ujung kanan adalah prakiraan per minggu. Minggu libur akhir tahun diasumsikan tutup.
- **Batang 'Perkiraan, Aman 90%, 95%, 99%'**: makin tinggi rasa aman yang diinginkan, makin banyak stok yang harus disiapkan.
""")
    with st.container(key="kartu_istilah"):
        jk("Istilah singkat")
        st.dataframe(pd.DataFrame({
            "Istilah": ["Prakiraan", "Stok sasaran (Siapkan)", "Stok pengaman", "Fill rate", "Kelas ABC", "Batas pesan ulang (ROP)"],
            "Artinya": ["Perkiraan jumlah yang akan terjual dalam periode ke depan",
                        "Jumlah yang disiapkan agar kemungkinan kehabisan hanya 5% (aman 95%)",
                        "Cadangan di atas perkiraan, untuk jaga-jaga permintaan lebih tinggi",
                        "Persen permintaan yang bisa dipenuhi dari stok",
                        "A = barang penyumbang 80% omzet, B = 15% berikutnya, C = sisanya",
                        "Pesan barang bila posisi stok sudah di bawah angka ini"]}), hide_index=True, width="stretch")
        st.markdown("Contoh CSV posisi stok:")
        st.code("kode,posisi_stok\n85123A,120\n22423,40", language="text")


# ================= halaman 3: prakiraan kategori =================
def hal_kategori():
    kepala("Prakiraan per Kategori", f"Satu kategori lebih dekat, {H_} minggu ke depan")
    urut = pk.sort_values("prakiraan_unit", ascending=False)["kategori"].tolist()
    with st.container(key="kartu_pilihkat"):
        kat = st.selectbox("Pilih kategori", urut)
    r = pk[pk["kategori"] == kat].iloc[0]
    st.write("")
    kpi_baris([("kotak", f"Prakiraan {H_} minggu", f"{r['prakiraan_unit']:,.0f} unit", f"senilai {rp(r['prakiraan_nilai'])}"),
               ("label", f"Dibanding {H_} minggu terakhir", fpct(pct(r["prakiraan_unit"], r["terakhir_unit"])), f"{r['terakhir_unit']:,.0f} unit"),
               ("target", "Dibanding tahun lalu", fpct(pct(r["prakiraan_unit"], r["tahun_lalu_unit"])), f"{r['tahun_lalu_unit']:,.0f} unit"),
               ("perisai", "Rata-rata meleset", f"{r['wape'] * 100:.0f}%", "pada uji mundur kategori ini"),
               ("koin", "Stok yang disiapkan (aman 95%)", f"{r['sasaran_unit']:,.0f} unit", f"modal {rp(r['sasaran_biaya'])}")])
    st.write("")
    c1, c2 = st.columns([3, 2])
    with c1:
        with st.container(key="kartu_mingguan_kat"):
            jk("Penjualan mingguan dan prakiraan")
            st.plotly_chart(grafik_mingguan(rk[rk["kategori"] == kat], r["prakiraan_unit"]), width="stretch")
    with c2:
        with st.container(key="kartu_tiga_kat"):
            jk("Dibanding periode lain")
            st.plotly_chart(tiga_batang(r["tahun_lalu_unit"], r["terakhir_unit"], r["prakiraan_unit"], r["wape"]), width="stretch")
    with st.container(key="kartu_barang_kat"):
        jk(f"Barang di kategori ini ({int(r['n_barang'])} barang aktif)")
        t = rencana[rencana["kategori"] == kat].nlargest(15, "prak_nilai")
        st.dataframe(pd.DataFrame({"Kode": t["kode"], "Barang": t["deskripsi"].str.title().str[:44], "Prakiraan (unit)": t["prak_unit"].round(0).astype(int),
                                   "Siapkan (unit)": t["sasaran_unit"].round(0).astype(int), "Harga (GBP)": t["harga"].round(2)}),
                     hide_index=True, width="stretch")
    st.caption("Garis kecil pada batang emas adalah rentang tipikal berdasarkan seberapa jauh prakiraan meleset pada uji mundur kategori ini. "
               "Perbandingan hanya untuk barang yang masih dijual. Minggu libur akhir tahun diasumsikan tutup.")


# ================= halaman 4: detail barang =================
def hal_barang():
    kepala("Detail Barang", "Perkiraan dan stok yang aman untuk satu barang")
    with st.container(key="kartu_pilih"):
        c1, c2 = st.columns([1, 2])
        kat = c1.selectbox("Kategori", ["Semua"] + sorted(rencana["kategori"].unique().tolist()))
        pool = rencana if kat == "Semua" else rencana[rencana["kategori"] == kat]
        top = pool.nlargest(300, "prak_nilai")
        lab = top["kode"] + "  " + top["deskripsi"].str.title().str[:46]
        pil = c2.selectbox("Barang (ketik untuk mencari)", lab.index, format_func=lambda i: lab[i])
    r = top.loc[pil]
    st.write("")
    kpi_baris([("kotak", f"Prakiraan {H_} minggu", f"{r['prak_unit']:,.0f}", "unit"),
               ("perisai", "Siapkan (aman 95%)", f"{r['sasaran_unit']:,.0f}", "unit"),
               ("label", f"Dibanding {H_} minggu terakhir", fpct(pct(r["prak_unit"], r["terakhir_unit"])), f"{r['terakhir_unit']:,.0f} unit"),
               ("target", "Dibanding tahun lalu", fpct(pct(r["prak_unit"], r["tahun_lalu_unit"])), f"{r['tahun_lalu_unit']:,.0f} unit"),
               ("koin", "Jumlah sekali pesan", f"{r['Q']:,.0f}", "unit")])
    st.write("")
    c1, c2 = st.columns([3, 2])
    with c1:
        with st.container(key="kartu_mingguan_brg"):
            jk("Penjualan mingguan dan prakiraan")
            st.plotly_chart(grafik_mingguan(riw[riw["kode"] == r["kode"]], r["prak_unit"]), width="stretch")
    with c2:
        with st.container(key="gelap_aman"):
            jk("Makin ingin aman, makin banyak yang disiapkan", gelap=True)
            nama = ["Perkiraan", "Aman 90%", "Aman 95%", "Aman 99%"]
            val = [r["prak_unit"], r["gq_0.9"], r["gq_0.95"], r["gq_0.99"]]
            fig = go.Figure(go.Bar(x=nama, y=val, marker_color=["#ffffff", ABU, EMAS, EMAS], text=[f"{v:,.0f}" for v in val],
                                   textposition="outside", cliponaxis=False))
            fig.update_yaxes(range=[0, max(val) * 1.25 + 1], title="unit")
            st.plotly_chart(tema(fig, 330, gelap=True), width="stretch")
    st.caption(f"Barang ini termasuk kelas {r['kelas']} dengan pola permintaan {r['jenis']}. 'Aman 95%' berarti kira-kira 95 dari 100 kali stok cukup untuk {H_} minggu.")


# ================= halaman 5: rencana pembelian =================
def hal_rencana():
    kepala("Rencana Pembelian", "Punya data stok? Isi di sini dan dapatkan daftar pesanan")
    with st.container(key="kartu_kontrol"):
        jk("Pengaturan")
        c1, c2 = st.columns(2)
        mode = c1.radio("Cara menentukan batas pesan ulang (ROP)", ["Seragam", "Per kelas, biaya minimum", "Per kelas, fill rate"])
        q = 0.95
        if mode == "Seragam":
            q = c2.select_slider("Tingkat aman", options=[0.8, 0.9, 0.95, 0.975, 0.99], value=0.95,
                                 format_func=lambda v: f"{v * 100:g}%", help="Peluang stok cukup selama menunggu barang datang.")
        unggah = st.file_uploader("Atau unggah posisi stok (CSV: kode, posisi_stok)", type="csv")
    rop = rencana[f"gq_{q}"] if mode == "Seragam" else rencana["rop_biaya"] if "biaya" in mode else rencana["rop_fill"]
    awal = pd.Series(0.0, index=rencana["kode"])
    if unggah is not None:
        up = pd.read_csv(unggah)
        awal = up.set_index(up.columns[0])[up.columns[1]].reindex(rencana["kode"]).fillna(0.0)
    tabel = pd.DataFrame({"kode": rencana["kode"], "deskripsi": rencana["deskripsi"], "kategori": rencana["kategori"],
                          "posisi_stok": awal.to_numpy(dtype=float)})
    with st.container(key="kartu_editor"):
        jk("Posisi stok (stok di tangan + pesanan yang sedang jalan)")
        edit = st.data_editor(tabel, hide_index=True, height=290, width="stretch", key="stok_editor",
                              disabled=["kode", "deskripsi", "kategori"],
                              column_config={"posisi_stok": st.column_config.NumberColumn("Posisi stok (unit)", min_value=0.0)})
    pos = edit["posisi_stok"].to_numpy(dtype=float)
    ropv, Q = rop.to_numpy(float), rencana["Q"].to_numpy(float)
    n_batch = np.where(pos <= ropv, np.floor((ropv - pos) / np.maximum(Q, 1e-9)) + 1, 0)
    out = rencana[["kode", "deskripsi", "kategori", "kelas", "gbm", "c_unit"]].copy()
    out["ROP"], out["Q"], out["posisi_stok"] = ropv.round(0), Q.round(0), pos
    out["unit_dipesan"] = np.round(n_batch * Q).astype(int)
    out["nilai_pesanan"] = out["unit_dipesan"] * out["c_unit"]
    perlu = out[out["unit_dipesan"] > 0].sort_values("nilai_pesanan", ascending=False)
    st.write("")
    kpi_baris([("kotak", "Barang perlu dipesan", f"{len(perlu):,}", f"dari {len(out):,} barang"),
               ("label", "Total unit", f"{int(perlu['unit_dipesan'].sum()):,}", "unit dipesan"),
               ("koin", "Nilai pesanan", rp(perlu["nilai_pesanan"].sum()), "pada biaya pokok"),
               ("perisai", "Nilai stok cadangan", rp(((ropv - rencana["gbm"].to_numpy()).clip(min=0) * rencana["c_unit"].to_numpy()).sum()), "untuk tingkat aman terpilih")])
    st.write("")
    with st.container(key="kartu_pesanan"):
        jk("Daftar pesanan")
        if perlu.empty:
            st.info("Dengan posisi stok saat ini belum ada barang yang perlu dipesan. Isi atau unggah posisi stok yang sebenarnya.")
        else:
            st.dataframe(perlu[["kode", "deskripsi", "kategori", "posisi_stok", "ROP", "Q", "unit_dipesan", "nilai_pesanan"]].head(200)
                         .rename(columns={"nilai_pesanan": "nilai (GBP)"}).round(0), hide_index=True, width="stretch")
            st.download_button("Unduh daftar pesanan (CSV)", perlu.drop(columns=["c_unit"]).to_csv(index=False).encode("utf-8"),
                               file_name="daftar_pesanan.csv", mime="text/csv")
        st.caption(f"Pesan bila posisi stok di bawah ROP. Waktu tunggu {P['LEAD']} minggu. Jumlah sekali pesan (Q) memakai EOQ dengan biaya pesan £{P['BIAYA_PESAN']:.0f} dan biaya simpan {P['BIAYA_SIMPAN'] * 100:.0f}% per tahun (asumsi).")


# ================= halaman 6: seberapa aman stok =================
def hal_layanan():
    kepala("Seberapa Aman Stok?", "Berapa mahal menaikkan rasa aman dari kehabisan")
    k = kurva.copy()
    with st.container(key="kartu_pilihq"):
        jk("Bandingkan dua tingkat aman")
        c1, c2 = st.columns(2)
        a = c1.select_slider("Dari", options=[0.8, 0.9, 0.95, 0.975], value=0.95, format_func=lambda v: f"{v * 100:g}%")
        opsi_b = [q for q in QG if q > a]
        b = c2.select_slider("Ke", options=opsi_b, value=opsi_b[-1], format_func=lambda v: f"{v * 100:g}%")
    va = k.loc[k["q"] == a, "nilai_pengaman_GBP"].iloc[0]
    vb = k.loc[k["q"] == b, "nilai_pengaman_GBP"].iloc[0]
    st.write("")
    kpi_baris([("perisai", f"Stok cadangan di {a * 100:g}%", rp(va), "nilai pada biaya pokok"), ("perisai", f"Stok cadangan di {b * 100:g}%", rp(vb), "nilai pada biaya pokok"),
               ("koin", "Tambahan modal", rp(vb - va), f"{(vb / va - 1) * 100:+.0f}%")])
    st.write("")
    with st.container(key="kartu_batang"):
        jk("Modal stok cadangan menurut tingkat aman")
        kk = k[k["q"] >= 0.8]
        fig = go.Figure(go.Bar(x=[f"{q * 100:g}%" for q in kk["q"]], y=kk["nilai_pengaman_GBP"],
                               marker_color=[EMAS if q in (a, b) else ABU for q in kk["q"]],
                               text=[rp(v) for v in kk["nilai_pengaman_GBP"]], textposition="outside", cliponaxis=False))
        fig.update_yaxes(visible=False, range=[0, kk["nilai_pengaman_GBP"].max() * 1.2])
        st.plotly_chart(tema(fig, 330), width="stretch")
        temuan(f"Dari {a * 100:g}% ke {b * 100:g}%, modal stok cadangan bertambah {rp(vb - va)} ({(vb / va - 1) * 100:+.0f}%). "
               "Kenaikan makin mahal di ujung atas: sedikit tambahan rasa aman membutuhkan banyak tambahan stok.")
    with st.expander("Kebijakan termurah menurut margin dan biaya (lebih teknis)"):
        pv = sens.pivot_table(index=["rasio_biaya_pokok", "biaya_simpan"], columns="biaya_pesan", values="terbaik", aggfunc="first")
        pv = pv.apply(lambda s: s.map(nama_k))
        pv.index = [f"biaya pokok {i * 100:.0f}%, simpan {j * 100:.0f}%" for i, j in pv.index]
        pv.columns = [f"pesan £{c:.0f}" for c in pv.columns]
        st.dataframe(pv, width="stretch")
        st.caption("Margin tinggi (biaya pokok rendah) mendorong tingkat aman lebih tinggi. Margin tipis dan biaya simpan tinggi mendorong stok yang ramping.")


# ================= halaman 7: bukti teknis =================
def hal_bukti():
    kepala("Bukti Teknis", "Untuk pembaca yang ingin memeriksa kekuatan hasilnya")
    b = boot.copy()
    b["nama"] = [nama_k(i) for i in b.index]
    k1, k2 = st.columns(2)
    with k1:
        with st.container(key="kartu_biaya"):
            jk("Biaya total dan selang 95%")
            f1 = go.Figure(go.Bar(x=b["nama"], y=b["biaya_total"], marker_color=EMAS,
                                  error_y=dict(type="data", symmetric=False, array=b["biaya_97.5%"] - b["biaya_total"],
                                               arrayminus=b["biaya_total"] - b["biaya_2.5%"], color=HIJAU)))
            f1.update_layout(yaxis_title="GBP")
            st.plotly_chart(tema(f1, 380), width="stretch")
    with k2:
        with st.container(key="gelap_fill"):
            jk("Permintaan yang terpenuhi (fill rate) dan selang 95%", gelap=True)
            f2 = go.Figure(go.Bar(x=b["nama"], y=b["fill_rate"] * 100, marker_color="#ffffff",
                                  error_y=dict(type="data", symmetric=False, array=(b["fill_97.5%"] - b["fill_rate"]) * 100,
                                               arrayminus=(b["fill_rate"] - b["fill_2.5%"]) * 100, color=EMAS)))
            f2.update_layout(yaxis=dict(range=[70, 100], title="%"))
            st.plotly_chart(tema(f2, 380, gelap=True), width="stretch")
    with st.container(key="kartu_tabelsim"):
        jk(f"Simulasi ulang {D['jendela_simulasi_minggu']} minggu terakhir, diuji buta")
        st.dataframe(pd.DataFrame({"Kebijakan": b["nama"], "Biaya total": b["biaya_total"].round(0),
                                   "Selisih vs termurah": b["selisih_vs_terbaik"].round(0),
                                   "Selang selisih 95%": [f"{lo:,.0f} s.d. {hi:,.0f}" for lo, hi in zip(b["selisih_2.5%"], b["selisih_97.5%"])],
                                   "Fill rate (%)": (b["fill_rate"] * 100).round(1)}), hide_index=True, width="stretch")
        st.caption("Selang dihitung dengan mengambil sampel ulang barang, bukan waktu, dan hanya satu jendela simulasi.")
    a1, a2 = st.columns(2)
    with a1:
        with st.container(key="kartu_akurasi"):
            jk("Akurasi ramalan per barang")
            ak = pd.DataFrame(R["akurasi"]).rename(columns={"rMAE_median_vs_ma4": "rMAE median"}).round(3)
            st.dataframe(ak, width="stretch")
            st.caption("WAPE makin kecil makin baik. Bias positif = meramal terlalu besar. rMAE di bawah 1 = lebih baik dari rata-rata 4 minggu.")
    with a2:
        with st.container(key="kartu_hit"):
            jk("Apakah tingkat aman yang dituju tercapai?")
            cv = pd.DataFrame(R["cakupan_rop"])
            cv["metode"] = cv["metode"].map({"normal klasik": "Normal klasik", "rasio SES empiris": "Rasio SES empiris", "GBM kuantil": "GBM kuantil"})
            cv["target"] = cv["target"].map(lambda v: f"{v * 100:g}%")
            pv = cv.pivot(index="target", columns="metode", values="hit_rate") * 100
            fig = go.Figure()
            for met, w in zip(pv.columns, [ABU, EMAS, HIJAU]):
                fig.add_bar(x=pv.index, y=pv[met], name=met, marker_color=w)
            fig.update_layout(barmode="group", yaxis=dict(range=[80, 100], title="peluang stok cukup (%)"))
            st.plotly_chart(tema(fig, 300), width="stretch")


# ================= halaman 8: metode =================
def hal_metode():
    kepala("Metode dan Batasan", "Data, langkah, asumsi, dan keterbatasan")
    with st.container(key="kartu_data"):
        jk("Data")
        st.markdown(f"""
- **Online Retail II** (UCI Machine Learning Repository, CC BY 4.0): transaksi toko grosir online di Inggris, {bulan(D['periode'][0])} sampai {bulan(D['periode'][1])}.
- {D['jumlah_barang']:,} barang, {D['jumlah_minggu']} minggu. {D['persen_sel_nol'] * 100:.0f}% sel barang-minggu bernilai nol.
- Retur dan pesanan yang dibatalkan dikeluarkan ({D['pesanan_dibatalkan_baris']:,} baris pesanan asli dicocokkan dengan faktur pembatalannya).
- **Kategori** tidak ada di data. Kategori dibuat dari kata kunci pada deskripsi barang (aturan sederhana, bukan kategori resmi); sekitar {K['persen_omzet_lainnya']:.0f}% omzet tidak terkategori.
""")
    with st.container(key="kartu_metode"):
        jk("Metode")
        st.markdown(f"""
1. **Permintaan mingguan** per barang pada sumbu kalender penuh. Kelas ABC dan pola permintaan dihitung hanya dari data sebelum titik prakiraan.
2. **Prakiraan.** Rata-rata bergerak, SES, Croston-SBA, musiman naif, dan gradient boosting diuji mundur pada {len(D['titik_awal_uji'])} titik awal bergulir. Untuk angka per kategori dipakai metode dengan galat terkecil di level kategori ({K['metode']}).
3. **Per kategori vs per barang.** Menjumlah banyak barang meredam derau, sehingga angka per kategori jauh lebih akurat daripada per barang.
4. **Stok cadangan** dari kuantil gradient boosting (hit rate diuji di luar sampel), bukan asumsi distribusi normal.
5. **Jumlah sekali pesan** memakai EOQ. **Simulasi persediaan** (s, nQ) dengan waktu tunggu {P['LEAD']} minggu membandingkan tujuh kebijakan.
6. **Ketidakpastian.** Bootstrap antar barang dan sensitivitas pada 27 skenario asumsi biaya.
""")
    c1, c2 = st.columns(2)
    with c1:
        with st.container(key="kartu_asumsi"):
            jk("Asumsi (tidak ada di data)")
            st.markdown(f"""
- Waktu tunggu pemasok seragam {P['LEAD']} minggu.
- Biaya pokok {P['RASIO_BIAYA'] * 100:.0f}% dari harga jual, biaya simpan {P['BIAYA_SIMPAN'] * 100:.0f}% per tahun, biaya pesan £{P['BIAYA_PESAN']:.0f}.
- Minggu libur akhir tahun diasumsikan tutup. Penjualan yang tak terpenuhi dianggap hilang.
- Permintaan yang terlihat adalah penjualan, bukan permintaan murni.
""")
    with c2:
        with st.container(key="kartu_batas"):
            jk("Keterbatasan")
            st.markdown("""
- Satu perusahaan di Inggris, dua tahun data. Pola musiman per barang tidak stabil.
- Tidak ada data stok, pemasok, atau waktu tunggu asli; hasil biaya mengikuti asumsi.
- Kategori hasil aturan kata kunci bisa keliru untuk sebagian barang.
- Rentang pada grafik adalah galat tipikal uji mundur, bukan jaminan statistik.
- Belum memodelkan diskon kuantitas, kapasitas gudang, dan barang pengganti.
""")


pg = st.navigation([st.Page(hal_ringkasan, title="Ringkasan", default=True), st.Page(hal_cara, title="Cara penggunaan"),
                    st.Page(hal_kategori, title="Prakiraan kategori"), st.Page(hal_barang, title="Detail barang"),
                    st.Page(hal_rencana, title="Rencana pembelian"), st.Page(hal_layanan, title="Seberapa aman stok"),
                    st.Page(hal_bukti, title="Bukti teknis"), st.Page(hal_metode, title="Metode dan batasan")])
pg.run()
