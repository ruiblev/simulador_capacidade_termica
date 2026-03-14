import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import time
import numpy as np

# --- Configuration ---
st.set_page_config(
    page_title="Simulador: Capacidade Térmica Mássica",
    page_icon="🔥",
    layout="wide"
)

st.markdown("""
<style>
    .main .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    h2 { color: #262730; border-bottom: 1px solid #d6d6d8; padding-bottom: 0.5rem; }
    .stButton>button { color: white; background-color: #ff4b4b; border-radius: 5px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- Session State ---
for key in ["running_auto", "running_manual", "stop_auto", "stop_manual",
            "done_auto", "done_manual", "anim_done_auto", "anim_done_manual"]:
    if key not in st.session_state:
        st.session_state[key] = False
if "data_manual" not in st.session_state:
    st.session_state["data_manual"] = pd.DataFrame({
        "E (J)": [None]*10,
        "ΔT (°C)": [None]*10,
    })

# --- Data ---
MATERIAIS = {"Alumínio": 897, "Cobre": 385, "Chumbo": 130, "Latão": 380, "Ferro": 450}

MATERIAIS_CORES = {
    "Alumínio": ("#d8dadd", "#a0a4a8"), "Cobre": ("#cd7f32", "#8a5a2b"),
    "Chumbo": ("#708090", "#4f5b66"),   "Latão": ("#e1c16e", "#b5a642"),
    "Ferro":  ("#606b73", "#3d454a")
}

# --- Sidebar ---
with st.sidebar:
    st.header("Configurações da Montagem")
    material = st.selectbox("Bloco Calorimétrico", list(MATERIAIS.keys()), index=0)
    massa = st.number_input("Massa do Bloco (kg)", min_value=0.1, max_value=5.0, value=1.0, step=0.1)
    st.markdown("---")
    tensao = st.number_input("Tensão (V)", min_value=0.0, max_value=30.0, value=12.0, step=0.5)
    corrente = st.number_input("Corrente (A)", min_value=0.0, max_value=10.0, value=1.0, step=0.1)
    st.markdown("---")
    temp_inicial = st.number_input("Temperatura Inicial (°C)", min_value=-20.0, max_value=100.0, value=20.0, step=0.5)
    tempo_simulacao = st.number_input("Tempo de Aquecimento (s)", min_value=10, max_value=600, value=300, step=10)
    st.markdown("---")
    st.markdown("**Sobre:** Simulador de determinação da capacidade térmica mássica.")

# --- SVG Circuit ---
def render_circuit_diagram(v_val, i_val, t_val, is_heating=False):
    v_s, i_s, t_s = f"{v_val:.1f} V", f"{i_val:.2f} A", f"{t_val:.1f} °C"
    glow_class = 'class="bh_active"' if is_heating else ""
    return f"""<div style="background:white;padding:10px;border-radius:10px;border:1px solid #ddd;margin-bottom:15px;">
<style>
@keyframes blockHeatPulse {{
  0% {{ filter: drop-shadow(0 0 2px rgba(255,50,0,0.1)); }}
  100% {{ filter: drop-shadow(0 0 12px rgba(255,20,0,0.9)); }}
}}
.bh_active {{ animation: blockHeatPulse 0.8s infinite alternate ease-in-out; }}
</style>
<svg viewBox="0 0 500 300" width="100%" height="300">
<path d="M 120 150 L 120 50 L 380 50 L 380 150" fill="none" stroke="#222" stroke-width="3"/>
<path d="M 120 180 L 120 250 L 220 250" fill="none" stroke="#222" stroke-width="3"/>
<path d="M 280 250 L 380 250 L 380 210" fill="none" stroke="#222" stroke-width="3"/>
<path d="M 220 250 L 220 200 L 280 200 L 280 250" fill="none" stroke="#222" stroke-width="2"/>
<rect x="50" y="100" width="90" height="90" fill="#f5f5f5" rx="5" stroke="#999" stroke-width="2"/>
<rect x="55" y="115" width="80" height="30" fill="#a8c199" rx="2" stroke="#555"/>
<text x="95" y="136" text-anchor="middle" font-family="monospace" font-weight="bold" font-size="16" fill="#111">{v_s}</text>
<text x="95" y="165" text-anchor="middle" font-family="sans-serif" font-weight="bold" font-size="12" fill="#666">FONTE</text>
<circle cx="80" cy="180" r="4" fill="#d32f2f"/><circle cx="110" cy="180" r="4" fill="#111"/>
<circle cx="380" cy="180" r="30" fill="#fff" stroke="#333" stroke-width="3"/>
<text x="380" y="170" text-anchor="middle" font-family="sans-serif" font-weight="bold" font-size="20" fill="#111">A</text>
<rect x="345" y="176" width="70" height="22" fill="#e0e0e0" rx="3" stroke="#888"/>
<text x="380" y="192" text-anchor="middle" font-family="monospace" font-weight="bold" font-size="14" fill="#111">{i_s}</text>
<rect x="220" y="235" width="60" height="30" fill="#cd7f32" rx="3" stroke="#8a5a2b" stroke-width="2" {glow_class}/>
<text x="250" y="278" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#666">Bloco</text>
<circle cx="250" cy="180" r="25" fill="#fff" stroke="#333" stroke-width="3"/>
<text x="250" y="170" text-anchor="middle" font-family="sans-serif" font-weight="bold" font-size="18" fill="#111">V</text>
<rect x="225" y="176" width="50" height="18" fill="#e0e0e0" rx="2" stroke="#888"/>
<text x="250" y="190" text-anchor="middle" font-family="monospace" font-weight="bold" font-size="12" fill="#111">{v_s}</text>
<rect x="265" y="100" width="8" height="135" fill="rgba(240,240,240,0.9)" rx="4" stroke="#ccc"/>
<circle cx="269" cy="235" r="5" fill="#ff2a2a"/>
<rect x="268" y="180" width="2" height="55" fill="#ff2a2a"/>
<rect x="280" y="108" width="55" height="22" fill="#e0e0e0" rx="2" stroke="#888"/>
<text x="307" y="124" text-anchor="middle" font-family="monospace" font-weight="bold" font-size="12" fill="#111">{t_s}</text>
</svg></div>"""

# --- Animation ---
def build_animation_html(cor_mat, cor_brd, mat_name, massa_v):
    return f"""<div style="position:fixed;top:0;left:0;width:100vw;height:100vh;background:rgba(0,0,0,0.8);display:flex;justify-content:center;align-items:center;z-index:10000;backdrop-filter:blur(8px);font-family:sans-serif;">
<style>
@keyframes fadeIn{{from{{opacity:0}}to{{opacity:1}}}}
@keyframes dropFall{{
  0%{{transform:translateY(-50px);opacity:0}}
  20%{{opacity:1}}
  70%{{opacity:1;transform:translateY(220px)}}
  100%{{opacity:0;transform:translateY(240px)}}
}}
@keyframes funnelShow{{
  0%{{opacity:0;transform:translateY(-20px)}}
  10%{{opacity:1;transform:translateY(0)}}
  80%{{opacity:1;transform:translateY(0)}}
  100%{{opacity:0;transform:translateY(-20px)}}
}}
@keyframes liquidGrow{{
  0%{{transform:scaleY(0);opacity:0}}
  10%{{transform:scaleY(0);opacity:0.8}}
  40%{{transform:scaleY(0.7);opacity:0.8}}
  75%{{transform:scaleY(0.7);opacity:0.8}}
  90%{{transform:scaleY(1);opacity:0.8}}
  100%{{transform:scaleY(1);opacity:0.8}}
}}
.drop {{ opacity: 0; }}
.d1 {{ animation: dropFall 1.5s linear forwards; animation-delay: 0.5s; }}
.d2 {{ animation: dropFall 1.5s linear forwards; animation-delay: 1.0s; }}
.d3 {{ animation: dropFall 1.5s linear forwards; animation-delay: 1.5s; }}
.d4 {{ animation: dropFall 1.5s linear forwards; animation-delay: 2.0s; }}
.funnel {{ opacity: 0; animation: funnelShow 3.5s ease-in-out forwards; animation-delay: 0.2s; }}
.lp {{
  transform-box: fill-box;
  transform-origin: bottom;
  transform: scaleY(0);
  opacity: 0;
  animation: liquidGrow 8.0s forwards;
  animation-delay: 0.8s;
}}
.drop-zone {{ clip-path: url(#glycerin-zone); }}
@keyframes slideDownTherm{{0%{{transform:translateY(-300px)}}100%{{transform:translateY(210px)}}}}
.therm{{transform:translateY(-300px);animation:slideDownTherm 2.0s cubic-bezier(0.25,0.46,0.45,0.94) forwards;animation-delay:4.5s}}
@keyframes slideDownRes{{0%{{transform:translateY(-300px)}}100%{{transform:translateY(210px)}}}}
@keyframes heatGlow{{0%{{filter:drop-shadow(0 0 0px rgba(255,100,0,0))}}100%{{filter:drop-shadow(0 0 15px rgba(255,50,0,0.8))}}}}
.res{{transform:translateY(-300px);animation:slideDownRes 2.0s cubic-bezier(0.25,0.46,0.45,0.94) 4.2s forwards,heatGlow 1.0s 8.5s forwards}}
@keyframes blockHeat{{0%{{filter:drop-shadow(0 0 0px rgba(255,50,0,0))}}100%{{filter:drop-shadow(0 0 25px rgba(255,50,0,0.6))}}}}
.bh{{animation:blockHeat 1.5s 8.5s forwards}}
@keyframes textChange{{
  0%{{content:"A adicionar glicerina..."}}
  48%{{content:"A adicionar glicerina..."}}
  52%{{content:"A inserir resistência e termómetro..."}}
  88%{{content:"A inserir resistência e termómetro..."}}
  95%{{content:"Circuito ligado! A aquecer..."}}
  100%{{content:"Circuito ligado! A aquecer..."}}
}}
.itxt::after{{content:"A adicionar glicerina...";animation:textChange 9.5s forwards}}
.mc{{background:linear-gradient(135deg,#fff 0%,#f0f0f0 100%);padding:40px;border-radius:24px;box-shadow:0 20px 50px rgba(0,0,0,0.6);position:relative;width:750px;height:600px;display:flex;flex-direction:column;align-items:center;justify-content:center;border:3px solid #ff4b4b;overflow:hidden}}
.ttxt{{position:absolute;top:25px;color:#444;font-weight:800;font-size:1.8rem;letter-spacing:1px;text-transform:uppercase}}
.itxt{{position:absolute;bottom:15px;color:#333;font-weight:800;font-size:1.5rem;letter-spacing:1px;text-transform:uppercase}}
</style>
<div class="mc">
<div class="ttxt">A Preparar a Montagem...</div>
<div style="position:absolute;top:80px;width:600px;height:400px;">
  <svg width="600" height="400" style="position:absolute;top:0;left:0;overflow:hidden">
    <defs>
      <clipPath id="hole1"><rect x="250" y="200" width="30" height="130"/></clipPath>
      <clipPath id="hole2"><rect x="320" y="200" width="30" height="130"/></clipPath>
      <clipPath id="glycerin-zone">
        <rect x="250" y="160" width="30" height="170"/>
        <rect x="320" y="160" width="30" height="170"/>
      </clipPath>
    </defs>
    <rect x="150" y="200" width="300" height="180" fill="{cor_mat}" rx="15" stroke="{cor_brd}" stroke-width="4" class="bh"/>
    <text x="300" y="340" text-anchor="middle" fill="#222" font-weight="bold" font-size="20">Bloco de {mat_name}</text>
    <text x="300" y="365" text-anchor="middle" fill="#444" font-weight="bold" font-size="16">{massa_v:.1f} kg</text>
    <rect x="250" y="200" width="30" height="130" fill="#111" rx="5"/>
    <rect x="320" y="200" width="30" height="130" fill="#111" rx="5"/>
    <rect x="250" y="280" width="30" height="50" fill="rgba(100,200,255,0.8)" rx="2" class="lp" clip-path="url(#hole1)"/>
    <rect x="320" y="280" width="30" height="50" fill="rgba(100,200,255,0.8)" rx="2" class="lp" clip-path="url(#hole2)"/>
    <g class="drop-zone">
      <path d="M 265 10 Q 270 20 265 30 Q 260 20 265 10" fill="rgba(100,200,255,0.8)" class="drop d1"/>
      <path d="M 280 -20 Q 285 -10 280 0 Q 275 -10 280 -20" fill="rgba(100,200,255,0.8)" class="drop d3"/>
      <path d="M 335 -10 Q 340 0 335 10 Q 330 0 335 -10" fill="rgba(100,200,255,0.8)" class="drop d2"/>
      <path d="M 330 -40 Q 335 -30 330 -20 Q 325 -30 330 -40" fill="rgba(100,200,255,0.8)" class="drop d4"/>
    </g>
    <g class="funnel"><polygon points="250,160 280,160 270,190 260,190" fill="rgba(255,255,255,0.8)" stroke="#555" stroke-width="2"/><rect x="260" y="190" width="10" height="20" fill="rgba(255,255,255,0.8)" stroke="#555" stroke-width="2"/></g>
    <g class="funnel"><polygon points="320,160 350,160 340,190 330,190" fill="rgba(255,255,255,0.8)" stroke="#555" stroke-width="2"/><rect x="330" y="190" width="10" height="20" fill="rgba(255,255,255,0.8)" stroke="#555" stroke-width="2"/></g>
    <g class="res"><rect x="255" y="0" width="20" height="120" fill="#bbb" rx="4" stroke="#444"/><path d="M 260 0 L 250 -200" stroke="#111" stroke-width="4" fill="none"/><path d="M 270 0 L 280 -200" stroke="#d32f2f" stroke-width="4" fill="none"/><line x1="255" y1="20" x2="275" y2="20" stroke="#888" stroke-width="2"/><line x1="255" y1="40" x2="275" y2="40" stroke="#888" stroke-width="2"/><line x1="255" y1="60" x2="275" y2="60" stroke="#888" stroke-width="2"/><line x1="255" y1="80" x2="275" y2="80" stroke="#888" stroke-width="2"/><line x1="255" y1="100" x2="275" y2="100" stroke="#888" stroke-width="2"/></g>
    <g class="therm"><rect x="327" y="-20" width="16" height="130" fill="rgba(240,240,240,0.9)" rx="8" stroke="#ccc"/><rect x="333" y="-10" width="4" height="100" fill="#fff"/><circle cx="335" cy="100" r="10" fill="#ff2a2a"/><rect x="333" y="40" width="4" height="60" fill="#ff2a2a"/><line x1="327" y1="80" x2="331" y2="80" stroke="#333"/><line x1="327" y1="60" x2="331" y2="60" stroke="#333"/><line x1="327" y1="40" x2="331" y2="40" stroke="#333"/><line x1="327" y1="20" x2="331" y2="20" stroke="#333"/><line x1="327" y1="0" x2="331" y2="0" stroke="#333"/></g>
  </svg>
</div>
<div class="itxt"></div>
</div>
</div>"""


# ─────────────────────────────────────
# Callbacks
# ─────────────────────────────────────
def _on_start(mode):
    st.session_state[f"running_{mode}"]   = True
    st.session_state[f"stop_{mode}"]      = False
    st.session_state[f"done_{mode}"]      = False
    st.session_state[f"anim_done_{mode}"] = False

def _on_stop(mode):
    st.session_state[f"stop_{mode}"]    = True


# ─────────────────────────────────────
# Main
# ─────────────────────────────────────
st.title("🔥 Capacidade Térmica Mássica")
st.markdown("""
Esta simulação permite determinar experimentalmente a **capacidade térmica mássica** ($c$) de diferentes materiais.
O circuito elétrico fornece energia ($E = U \\cdot I \\cdot \\Delta t$) ao bloco, provocando $\\Delta T$.
""")


def run_simulation(is_manual: bool):
    mode = "manual" if is_manual else "auto"
    rk, sk, dk = f"running_{mode}", f"stop_{mode}", f"done_{mode}"

    anim_ph = st.empty()
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Montagem")
        st.markdown(f"""
**Material:** {material} &nbsp;|&nbsp; **Massa:** {massa:.1f} kg
**Potência:** {tensao * corrente:.1f} W &nbsp;|&nbsp; **T₀:** {temp_inicial:.1f} °C
""")
        schema_ph = st.empty()
        schema_ph.markdown(render_circuit_diagram(tensao, corrente, temp_inicial), unsafe_allow_html=True)

        btn_label = "🔌 Iniciar Experiência (Tempo Real)" if is_manual else "🔌 Ligar Circuito (Acelerado)"

        st.button(
            btn_label,
            use_container_width=True,
            key=f"start_{mode}",
            disabled=st.session_state[rk],
            on_click=_on_start,
            args=(mode,)
        )

        st.button(
            "⏹️ Interromper Simulação",
            use_container_width=True,
            key=f"stop_btn_{mode}",
            disabled=not st.session_state[rk],
            on_click=_on_stop,
            args=(mode,),
            type="secondary"
        )

    with col2:
        st.subheader("Leituras e Gráficos")
        metrics_ph = st.empty()
        chart_ph   = st.empty()
        prog_bar   = st.progress(0)

    # ── Run simulation if flagged ──────────────────────────────────────────
    if st.session_state[rk]:
        potencia = tensao * corrente
        c        = MATERIAIS[material]
        cor_m, cor_b = MATERIAIS_CORES[material]

        # Animation (only on fresh start, not on stop-rerun)
        ak = f"anim_done_{mode}"
        if not st.session_state[ak] and not st.session_state[sk]:
            anim_ph.markdown(build_animation_html(cor_m, cor_b, material, massa), unsafe_allow_html=True)
            time.sleep(10.5)
            anim_ph.empty()
            st.session_state[ak] = True

        tempos, temperaturas, energias = [], [], []
        if is_manual:
            dt_sim, slp, nsteps = 1.0, 1.0, int(tempo_simulacao)
        else:
            nsteps = 50
            dt_sim = tempo_simulacao / nsteps
            slp    = max(0.02, 3.0 / nsteps)

        ct, cT, cE = 0.0, float(temp_inicial), 0.0
        tempos.append(ct); temperaturas.append(cT); energias.append(cE)
        schema_ph.markdown(render_circuit_diagram(tensao, corrente, cT, is_heating=True), unsafe_allow_html=True)
        max_T = temp_inicial + (potencia * tempo_simulacao) / (massa * c)

        stopped = False
        for step in range(1, nsteps + 1):
            if st.session_state[sk]:
                stopped = True; break
            time.sleep(slp)
            ct += dt_sim
            dE  = potencia * dt_sim; cE += dE
            dT  = dE / (massa * c);  cT += dT
            tempos.append(ct); temperaturas.append(cT); energias.append(cE)
            schema_ph.markdown(render_circuit_diagram(tensao, corrente, cT, is_heating=True), unsafe_allow_html=True)

            with metrics_ph.container():
                if is_manual:
                    m1, m2 = st.columns(2)
                    m1.metric("Cronómetro (s)", f"{ct:.0f}")
                    m2.metric("Termómetro (°C)", f"{cT:.1f}", f"+{cT - temp_inicial:.1f} °C")
                else:
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Cronómetro (s)", f"{ct:.1f}")
                    m2.metric("Termómetro (°C)", f"{cT:.1f}", f"+{cT - temp_inicial:.1f} °C")
                    m3.metric("Energia Fornecida (J)", f"{cE:.1f}")

            if is_manual:
                fig, ax = plt.subplots(figsize=(8, 4))
                ax.plot(tempos, temperaturas, 'r-', lw=2)
                ax.set(xlim=(0, tempo_simulacao), ylim=(temp_inicial-1, max_T+2),
                       xlabel="Tempo (s)", ylabel="Temperatura (°C)", title="Temperatura (Tempo Real)")
                ax.grid(True, ls='--', alpha=.7)
            else:
                fig, (ax, ax2) = plt.subplots(1, 2, figsize=(10, 4))
                ax.plot(tempos, temperaturas, 'r-', lw=2)
                ax.set(xlim=(0, tempo_simulacao), ylim=(temp_inicial-1, max_T+2),
                       xlabel="Tempo (s)", ylabel="Temperatura (°C)", title="Evolução da Temperatura")
                ax.grid(True, ls='--', alpha=.7)
                ax2.plot(energias, temperaturas, 'b-', lw=2)
                ax2.set(xlim=(0, potencia*tempo_simulacao), ylim=(temp_inicial-1, max_T+2),
                        xlabel="Energia E (J)", ylabel="Temperatura (°C)", title="T vs E")
                ax2.grid(True, ls='--', alpha=.7)
            plt.tight_layout(); chart_ph.pyplot(fig); plt.close(fig)
            prog_bar.progress(int(step / nsteps * 100))

        # End of loop
        st.session_state[rk] = False
        st.session_state[sk] = False
        st.session_state[dk] = True

        if stopped:
            st.warning(f"⏹️ Simulação interrompida aos {ct:.0f} s.")
        else:
            st.success("✅ Simulação Concluída!")

        if not is_manual and len(energias) > 2:
            _auto_analysis(tempos, temperaturas, energias, massa, c, material)

    # In Manual Mode, the table is ALWAYS visible (whether running, done or idle)
    if is_manual:
        _manual_table(massa, material)


def _auto_analysis(tempos, temperaturas, energias, massa, c, material):
    st.markdown("---")
    st.subheader("Análise de Dados")
    dT = np.array(temperaturas) - temp_inicial
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(energias, dT, 'go', alpha=.5, label='Dados')
    cf = np.polyfit(energias, dT, 1); d = cf[0]
    ax.plot(energias, np.polyval(cf, energias), 'k-', label=f'Declive = {d:.5f} °C/J')
    ax.set(xlabel="Energia (J)", ylabel=r"$\Delta T$ (°C)"); ax.legend(); ax.grid(True, ls='--', alpha=.7)
    st.pyplot(fig)
    if d > 0:
        c_e = 1/(massa*d); e_p = abs(c_e-c)/c*100
        st.info(f"**Capacidade Térmica Mássica:** ≈ **{c_e:.0f} J/(kg·°C)**")
        if e_p < 1: st.success(f"Correto! Valor tabelado {material}: {c} J/(kg·°C).")


def _manual_table(massa, material):
    st.markdown("---")
    st.subheader("📋 Registo de Dados Experimentais (Modo Manual)")
    st.write("Introduza os valores de Energia (E) e Variação de Temperatura (ΔT) na tabela abaixo.")

    df_ed = st.data_editor(
        st.session_state["data_manual"],
        num_rows="dynamic",
        use_container_width=True,
        key="data_editor_manual_simple",
        column_config={
            "E (J)": st.column_config.NumberColumn("Energia E (J)", format="%.1f"),
            "ΔT (°C)": st.column_config.NumberColumn("Variação ΔT (°C)", format="%.2f"),
        }
    )
    st.session_state["data_manual"] = df_ed

    if st.button("📊 Gerar Gráfico e Ajuste Linear", key="fit_manual_btn", use_container_width=True, type="primary"):
        df_c = df_ed.dropna(subset=["E (J)", "ΔT (°C)"])
        # Ensure values are numeric and not zero unless intentional
        ev = df_c["E (J)"].values.astype(float)
        tv = df_c["ΔT (°C)"].values.astype(float)
        
        if len(ev) >= 2:
            st.markdown("### Resultado da Análise Linear")
            cf = np.polyfit(ev, tv, 1)
            d, b = cf  # ΔT = d*E + b
            
            # Matplotlib Plot
            fig, ax = plt.subplots(figsize=(8, 5))
            ax.scatter(ev, tv, color='#ff4b4b', s=80, edgecolors='black', label='Pontos Registados', zorder=3)
            
            xf = np.linspace(min(ev)*0.9, max(ev)*1.1, 200)
            yf = np.polyval(cf, xf)
            ax.plot(xf, yf, 'k--', lw=2, label='Ajuste Linear (Mínimos Quadrados)', zorder=2)
            
            ax.set_xlabel("Energia Fornecida E (J)", fontsize=12, fontweight='bold')
            ax.set_ylabel("Variação de Temperatura ΔT (°C)", fontsize=12, fontweight='bold')
            ax.set_title(f"Ajuste Linear: ΔT em função de E ({material})", fontsize=14, fontweight='bold')
            
            # Equation text on plot
            eq_label = fr"$\Delta T = {d:.4e} \cdot E + ({b:.2f})$"
            ax.text(0.05, 0.95, eq_label, transform=ax.transAxes, fontsize=12, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.5))
            
            ax.legend()
            ax.grid(True, ls=':', alpha=0.6)
            st.pyplot(fig)
            
            # Technical Details
            c_calc = 1.0 / (massa * d) if d != 0 else 0
            c_tab = MATERIAIS[material]
            erro = abs(c_calc - c_tab) / c_tab * 100 if c_tab != 0 else 0
            
            m1, m2, m3 = st.columns(3)
            m1.metric("Pendente (m)", f"{d:.4e} °C/J")
            m2.metric("Ordenada na Origem (b)", f"{b:.2f} °C")
            m3.metric("Correlação (R)", f"{np.corrcoef(ev, tv)[0,1]:.4f}")
            
            st.success(fr"**Equação Obtida:** $ \Delta T = {d:.4e} \cdot E + {b:.2f} $")
            
            st.info(fr"""
            **Determinação da Capacidade Térmica Mássica ($c$):**
            Como $\Delta T = \frac{{1}}{{m \cdot c}} \cdot E$, o declive $m = \frac{{1}}{{m \cdot c}}$.
            Donde $c = \frac{{1}}{{m \cdot m_{{bloco}}}}$.
            
            - **$c$ calculado:** **{c_calc:.1f} J/(kg·K)**
            - **$c$ tabelado ({material}):** {c_tab} J/(kg·K)
            - **Erro Percentual:** {erro:.1f}%
            """)
        else:
            st.error("ERRO: São necessários pelo menos 2 pontos experimentais para realizar o ajuste linear.")


# ─────────────────────────────────────
# Tabs
# ─────────────────────────────────────
tab_manual, tab_auto = st.tabs(["🧪 Modo Manual", "🤖 Modo Automático"])
with tab_manual:
    run_simulation(is_manual=True)
with tab_auto:
    run_simulation(is_manual=False)
