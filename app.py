"""Antarmuka Streamlit untuk Asisten Analisis Kinerja dan Gangguan PLTS On-Grid."""

from __future__ import annotations

import streamlit as st

from plts_assistant.calculator import (
    calculate_cuf,
    calculate_energy_difference,
    calculate_performance_ratio,
)
from plts_assistant.config import settings
from plts_assistant.documents import load_documents
from plts_assistant.pipeline import AssistantEngine

st.set_page_config(
    page_title="Asisten Analisis PLTS On-Grid",
    page_icon="☀️",
    layout="wide",
)


@st.cache_resource(show_spinner="Memuat knowledge base dan membangun indeks retrieval...")
def get_engine() -> AssistantEngine:
    return AssistantEngine(settings)


def render_calculation() -> dict | None:
    method = st.selectbox(
        "Jenis perhitungan tambahan",
        ["Tidak ada", "Performance Ratio (PR)", "Capacity Utilization Factor (CUF)", "Selisih energi"],
        help="Perhitungan dilakukan oleh fungsi Python. Pastikan satuan dan periode input konsisten.",
    )
    if method == "Tidak ada":
        return None

    try:
        if method == "Performance Ratio (PR)":
            col1, col2, col3 = st.columns(3)
            energy = col1.number_input("E_Grid (kWh)", min_value=0.0, value=1000.0, step=10.0)
            irradiation = col2.number_input("GlobInc (kWh/m²)", min_value=0.000001, value=150.0, step=1.0)
            capacity = col3.number_input("Pnom PV (kWp)", min_value=0.000001, value=100.0, step=1.0)
            return calculate_performance_ratio(energy, irradiation, capacity)

        if method == "Capacity Utilization Factor (CUF)":
            col1, col2, col3 = st.columns(3)
            energy = col1.number_input("Energi aktual (kWh)", min_value=0.0, value=1000.0, step=10.0)
            capacity = col2.number_input("Kapasitas terpasang (kW)", min_value=0.000001, value=100.0, step=1.0)
            hours = col3.number_input("Durasi periode (jam)", min_value=0.000001, value=720.0, step=1.0)
            return calculate_cuf(energy, capacity, hours)

        col1, col2 = st.columns(2)
        actual = col1.number_input("Energi aktual (kWh)", min_value=0.0, value=900.0, step=10.0)
        reference = col2.number_input("Energi referensi (kWh)", min_value=0.0, value=1000.0, step=10.0)
        return calculate_energy_difference(actual, reference)
    except ValueError as exc:
        st.error(str(exc))
        return None


def main() -> None:
    st.title("☀️ Asisten Analisis Kinerja dan Gangguan PLTS On-Grid")
    st.caption("Prototipe analisis awal berbasis dokumen, retrieval TF-IDF, kalkulator Python, dan LLM opsional.")

    with st.sidebar:
        st.header("Pengaturan retrieval")
        top_k = st.slider("Jumlah potongan dokumen (top-k)", min_value=1, max_value=10, value=settings.top_k)
        threshold = st.slider(
            "Ambang cosine similarity",
            min_value=0.0,
            max_value=1.0,
            value=float(settings.retrieval_threshold),
            step=0.01,
        )
        st.divider()
        st.write("**Status integrasi LLM**")
        if settings.llm_enabled:
            st.success(f"Konfigurasi tersedia · model: {settings.llm_model}")
            st.caption("Keberhasilan panggilan provider tetap bergantung pada jaringan, API key, model, dan endpoint.")
        else:
            st.warning("LLM belum dikonfigurasi. Aplikasi berjalan dalam mode retrieval-only.")
        st.caption("Jangan memasukkan API key pada chat atau source code. Gunakan file .env lokal.")

    try:
        engine = get_engine()
    except Exception as exc:
        st.error(f"Knowledge base gagal dimuat: {type(exc).__name__}: {exc}")
        st.stop()

    tab_assistant, tab_calculator, tab_kb, tab_about = st.tabs(
        ["Asisten", "Kalkulator PLTS", "Knowledge base", "Tentang & batasan"]
    )

    with tab_assistant:
        st.subheader("Ajukan pertanyaan")
        question = st.text_area(
            "Pertanyaan mengenai kinerja atau gangguan PLTS",
            placeholder="Contoh: Bagaimana PR dihitung dan data apa yang diperlukan untuk memeriksa penurunan kinerja?",
            height=110,
        )
        with st.expander("Tambahkan hasil perhitungan (opsional)"):
            calculation_result = render_calculation()
        if st.button("Cari sumber dan analisis", type="primary", disabled=not question.strip()):
            with st.spinner("Pertanyaan sedang dicari pada knowledge base..."):
                try:
                    answer = engine.ask(
                        question,
                        calculation_result=calculation_result,
                        top_k=top_k,
                        threshold=threshold,
                    )
                except Exception as exc:
                    st.error(f"Proses belum berhasil: {type(exc).__name__}: {exc}")
                else:
                    st.session_state["last_answer"] = answer.model_dump(exclude_none=True)

        result = st.session_state.get("last_answer")
        if result:
            status = result.get("status", "perlu_verifikasi")
            labels = {
                "cukup_data": "Cukup data menurut model; tetap verifikasi sumber",
                "data_belum_cukup": "Data belum cukup",
                "informasi_tidak_ditemukan": "Informasi tidak ditemukan pada hasil retrieval",
                "perlu_verifikasi": "Perlu verifikasi",
            }
            st.markdown(f"**Status:** `{status}` — {labels.get(status, status)}")
            st.markdown("### Ringkasan")
            st.write(result.get("ringkasan", ""))

            if result.get("hasil_perhitungan"):
                st.markdown("### Hasil perhitungan")
                st.json(result["hasil_perhitungan"])

            if result.get("temuan_dokumen"):
                st.markdown("### Temuan dokumen")
                for item in result["temuan_dokumen"]:
                    st.write(f"- {item}")

            if result.get("kemungkinan_penyebab"):
                st.markdown("### Kemungkinan yang dapat diperiksa (bukan diagnosis)")
                for item in result["kemungkinan_penyebab"]:
                    st.write(f"- {item}")

            if result.get("pemeriksaan_lanjutan"):
                st.markdown("### Pemeriksaan lanjutan")
                for item in result["pemeriksaan_lanjutan"]:
                    st.write(f"- {item}")

            if result.get("keterbatasan"):
                st.markdown("### Keterbatasan")
                for item in result["keterbatasan"]:
                    st.write(f"- {item}")

            if result.get("sumber"):
                st.markdown("### Sumber yang ditemukan")
                for source in result["sumber"]:
                    with st.expander(
                        f"{source['id_chunk']} · {source['judul']} · skor {source['skor_retrieval']:.3f}"
                    ):
                        st.caption(source["nama_file"])
                        st.write(source["kutipan"])
                        if source.get("url"):
                            st.markdown(f"[Buka sumber asli]({source['url']})")

            with st.expander("Lihat keluaran terstruktur"):
                st.json(result)

    with tab_calculator:
        st.subheader("Kalkulator parameter PLTS")
        st.info("Kalkulator tidak menarik data dari inverter. Semua nilai harus dimasukkan dan diperiksa oleh pengguna.")
        selected = st.radio(
            "Pilih perhitungan",
            ["PR", "CUF", "Selisih energi"],
            horizontal=True,
        )
        try:
            if selected == "PR":
                c1, c2, c3 = st.columns(3)
                e = c1.number_input("E_Grid (kWh)", min_value=0.0, value=1000.0, key="calc_pr_e")
                g = c2.number_input("GlobInc (kWh/m²)", min_value=0.000001, value=150.0, key="calc_pr_g")
                p = c3.number_input("Pnom PV (kWp)", min_value=0.000001, value=100.0, key="calc_pr_p")
                if st.button("Hitung PR"):
                    st.success(f"PR = {calculate_performance_ratio(e, g, p)['persen']:.2f}%")
                    st.caption("Periode E_Grid dan GlobInc harus sama. Periksa definisi energi untuk sistem dengan self-consumption/storage.")
            elif selected == "CUF":
                c1, c2, c3 = st.columns(3)
                e = c1.number_input("Energi aktual (kWh)", min_value=0.0, value=1000.0, key="calc_cuf_e")
                p = c2.number_input("Kapasitas (kW)", min_value=0.000001, value=100.0, key="calc_cuf_p")
                h = c3.number_input("Durasi (jam)", min_value=0.000001, value=720.0, key="calc_cuf_h")
                if st.button("Hitung CUF"):
                    st.success(f"CUF = {calculate_cuf(e, p, h)['persen']:.2f}%")
            else:
                c1, c2 = st.columns(2)
                a = c1.number_input("Energi aktual (kWh)", min_value=0.0, value=900.0, key="calc_delta_a")
                r = c2.number_input("Energi referensi (kWh)", min_value=0.0, value=1000.0, key="calc_delta_r")
                if st.button("Hitung selisih"):
                    delta = calculate_energy_difference(a, r)
                    st.metric("Selisih energi", f"{delta['selisih_kwh']:.2f} kWh")
                    pct = delta["persentase_terhadap_referensi"]
                    st.caption("Persentase terhadap referensi: tidak terdefinisi karena referensi = 0." if pct is None else f"Persentase: {pct:.2f}%")
        except ValueError as exc:
            st.error(str(exc))

    with tab_kb:
        st.subheader("Dokumen yang dimuat")
        st.write(f"Dokumen terbaca: **{len(engine.documents)}** · Potongan teks: **{len(engine.chunks)}**")
        for document in engine.documents:
            with st.expander(f"{document.doc_id} · {document.title}"):
                st.caption(document.path)
                if document.source_url:
                    st.markdown(f"[Sumber]({document.source_url})")
                st.write(document.text[:1200] + ("…" if len(document.text) > 1200 else ""))
        st.caption("Konten knowledge base adalah catatan ringkas dan dokumentasi teknis. Artikel lengkap harus diperiksa pada sumber aslinya.")

    with tab_about:
        st.subheader("Ruang lingkup")
        st.markdown(
            """
            Sistem digunakan untuk membantu pencarian informasi teknis dan perhitungan awal berdasarkan dokumen serta data yang dimasukkan.

            **Batasan:** sistem tidak menetapkan akar kerusakan, tidak membaca logger/SCADA secara langsung, tidak memantau inverter secara real-time, dan tidak mengendalikan perangkat. Untuk kode alarm, manual dengan merek dan model yang tepat harus tersedia. Pemeriksaan fisik mengikuti manual produsen dan prosedur keselamatan oleh personel yang berwenang.
            """
        )
        st.markdown("### Konfigurasi saat aplikasi dijalankan")
        st.json(
            {
                "top_k_default": settings.top_k,
                "threshold_default": settings.retrieval_threshold,
                "chunk_size": settings.chunk_size,
                "chunk_overlap": settings.chunk_overlap,
                "llm_configured": settings.llm_enabled,
                "llm_model": settings.llm_model or None,
            }
        )


if __name__ == "__main__":
    main()
