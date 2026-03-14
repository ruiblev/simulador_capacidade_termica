import tkinter as tk
from tkinter import ttk, messagebox
import time

class ThermalCapacitySimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Capacidade Térmica Mássica")
        self.root.geometry("600x450")
        self.root.resizable(False, False)

        # Propriedades dos materiais (c em J/(kg.K))
        self.materiais = {
            "Alumínio": 897,
            "Cobre": 385,
            "Chumbo": 130,
            "Latão": 380,
            "Ferro": 450
        }

        # Variáveis de estado
        self.running = False
        self.time_elapsed = 0.0      # Tempo em simulação (s)
        self.energy_supplied = 0.0   # Energia em simulação (J)
        self.current_temp = 20.0     # Temperatura atual (°C)
        self.last_update_time = 0.0  # Tempo real da última atualização
        self.delay_ms = 50           # Intervalo de atualização (ms)

        self.setup_ui()

    def setup_ui(self):
        # --- Frame Configurações ---
        config_frame = ttk.LabelFrame(self.root, text="Configurações da Montagem", padding=(10, 10))
        config_frame.grid(row=0, column=0, padx=15, pady=10, sticky="ew")

        # Material
        ttk.Label(config_frame, text="Bloco Calorimétrico:").grid(row=0, column=0, sticky="w", pady=5)
        self.material_var = tk.StringVar(value="Alumínio")
        material_combo = ttk.Combobox(config_frame, textvariable=self.material_var, values=list(self.materiais.keys()), state="readonly", width=15)
        material_combo.grid(row=0, column=1, padx=10, pady=5)

        # Massa
        ttk.Label(config_frame, text="Massa do Bloco (kg):").grid(row=1, column=0, sticky="w", pady=5)
        self.massa_var = tk.DoubleVar(value=1.0)
        ttk.Entry(config_frame, textvariable=self.massa_var, width=18).grid(row=1, column=1, padx=10, pady=5)

        # Voltagem/Corrente
        ttk.Label(config_frame, text="Tensão (V):").grid(row=2, column=0, sticky="w", pady=5)
        self.tensao_var = tk.DoubleVar(value=12.0)
        ttk.Entry(config_frame, textvariable=self.tensao_var, width=18).grid(row=2, column=1, padx=10, pady=5)

        ttk.Label(config_frame, text="Corrente (A):").grid(row=3, column=0, sticky="w", pady=5)
        self.corrente_var = tk.DoubleVar(value=5.5)
        ttk.Entry(config_frame, textvariable=self.corrente_var, width=18).grid(row=3, column=1, padx=10, pady=5)

        # Temperatura Inicial
        ttk.Label(config_frame, text="Temperatura Inicial (°C):").grid(row=4, column=0, sticky="w", pady=5)
        self.temp_inicial_var = tk.DoubleVar(value=20.0)
        ttk.Entry(config_frame, textvariable=self.temp_inicial_var, width=18).grid(row=4, column=1, padx=10, pady=5)

        # Velocidade da Simulação
        ttk.Label(config_frame, text="Velocidade da Simulação:").grid(row=5, column=0, sticky="w", pady=5)
        self.velocidade_var = tk.IntVar(value=10)
        velocidade_combo = ttk.Combobox(config_frame, textvariable=self.velocidade_var, values=[1, 5, 10, 20, 60], state="readonly", width=15)
        velocidade_combo.grid(row=5, column=1, padx=10, pady=5)
        ttk.Label(config_frame, text="x").grid(row=5, column=2, sticky="w")

        # --- Frame Informações (Leituras) ---
        info_frame = ttk.LabelFrame(self.root, text="Leituras (Multímetro, Termómetro e Cronómetro)", padding=(10, 10))
        info_frame.grid(row=0, column=1, padx=15, pady=10, sticky="ns")

        # Estilo para os mostradores
        display_font = ("Courier", 18, "bold")

        # Tempo (Cronómetro)
        ttk.Label(info_frame, text="Tempo (s):").grid(row=0, column=0, sticky="w", pady=10)
        self.lbl_tempo = ttk.Label(info_frame, text="0.0", font=display_font, foreground="blue")
        self.lbl_tempo.grid(row=0, column=1, sticky="w", padx=10)

        # Temperatura
        ttk.Label(info_frame, text="Temperatura (°C):").grid(row=1, column=0, sticky="w", pady=10)
        self.lbl_temp = ttk.Label(info_frame, text="20.0", font=display_font, foreground="red")
        self.lbl_temp.grid(row=1, column=1, sticky="w", padx=10)

        # Energia (Joules)
        ttk.Label(info_frame, text="Energia Fornecida (J):").grid(row=2, column=0, sticky="w", pady=10)
        self.lbl_energia = ttk.Label(info_frame, text="0.0", font=display_font, foreground="green")
        self.lbl_energia.grid(row=2, column=1, sticky="w", padx=10)

        # --- Frame Controlos ---
        control_frame = ttk.Frame(self.root)
        control_frame.grid(row=1, column=0, columnspan=2, pady=20)

        self.btn_iniciar = ttk.Button(control_frame, text="Ligar Circuito (Iniciar)", command=self.iniciar_simulacao, width=25)
        self.btn_iniciar.grid(row=0, column=0, padx=10)

        self.btn_parar = ttk.Button(control_frame, text="Desligar Circuito (Parar)", command=self.parar_simulacao, width=25, state="disabled")
        self.btn_parar.grid(row=0, column=1, padx=10)

        self.btn_repor = ttk.Button(control_frame, text="Repor / Limpar", command=self.repor_simulacao, width=20)
        self.btn_repor.grid(row=0, column=2, padx=10)

        self.update_displays()

    def iniciar_simulacao(self):
        try:
            # Validações básicas
            m = self.massa_var.get()
            u = self.tensao_var.get()
            i = self.corrente_var.get()
            t0 = self.temp_inicial_var.get()

            if m <= 0 or u < 0 or i < 0:
                raise ValueError("Os valores devem ser positivos.")
                
            if self.time_elapsed == 0.0:
                self.current_temp = t0

            self.running = True
            self.last_update_time = time.time()
            self.btn_iniciar.config(state="disabled")
            self.btn_parar.config(state="normal")
            
            # Desativar configurações enquanto corre
            self.lock_configs(True)
            self.update_loop()
        except Exception as e:
            messagebox.showerror("Erro de Configuração", f"Verifique os valores introduzidos:\n{str(e)}")

    def parar_simulacao(self):
        self.running = False
        self.btn_iniciar.config(state="normal")
        self.btn_parar.config(state="disabled")

    def repor_simulacao(self):
        self.parar_simulacao()
        self.time_elapsed = 0.0
        self.energy_supplied = 0.0
        self.current_temp = self.temp_inicial_var.get()
        self.update_displays()
        self.lock_configs(False)

    def lock_configs(self, locked):
        state = "disabled" if locked else "normal"
        readonly_state = "disabled" if locked else "readonly"
        
        # Desativar botões para não permitir mudanças durante a simulação
        for child in self.root.winfo_children():
            if isinstance(child, ttk.LabelFrame) and child.cget("text") == "Configurações da Montagem":
                for widget in child.winfo_children():
                    if isinstance(widget, ttk.Entry):
                        widget.config(state=state)
                    elif isinstance(widget, ttk.Combobox):
                        widget.config(state=readonly_state)

    def update_loop(self):
        if not self.running:
            return

        now = time.time()
        real_dt = now - self.last_update_time
        self.last_update_time = now

        # Calculos
        velocidade = self.velocidade_var.get()
        sim_dt = real_dt * velocidade
        
        # Incrementar tempo
        self.time_elapsed += sim_dt

        # P = U * I
        potencia = self.tensao_var.get() * self.corrente_var.get()
        
        # E = P * t
        dE = potencia * sim_dt
        self.energy_supplied += dE

        # dE = m * c * dT => dT = dE / (m * c)
        material = self.material_var.get()
        c = self.materiais[material]
        massa = self.massa_var.get()
        
        dT = dE / (massa * c)
        self.current_temp += dT

        # Atualizar Ecrã
        self.update_displays()

        # Agendar próxima atualização
        self.root.after(self.delay_ms, self.update_loop)

    def update_displays(self):
        self.lbl_tempo.config(text=f"{self.time_elapsed:.1f}")
        self.lbl_temp.config(text=f"{self.current_temp:.1f}")
        self.lbl_energia.config(text=f"{self.energy_supplied:.1f}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ThermalCapacitySimulator(root)
    root.mainloop()
