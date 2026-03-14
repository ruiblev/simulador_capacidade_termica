# 🔥 Simulador de Capacidade Térmica Mássica

Este é um simulador interativo desenvolvido em **Python** (utilizando **Streamlit**) para o ensino de Física e Química (10.º ano). O objetivo é permitir a determinação experimental da capacidade térmica mássica ($c$) de diferentes materiais através de um circuito elétrico de aquecimento.

## 🚀 Funcionalidades

O simulador está dividido em dois modos principais para facilitar a aprendizagem:

### 🧪 Modo Manual (Prioritário)
- **Tabela Experimental**: Introdução manual de valores de Energia ($E$) e Variação de Temperatura ($\Delta T$).
- **Gráfico de Ajuste Linear**: Geração automática de gráficos com a equação da reta ($y = mx + b$).
- **Análise Física**: Determinação do valor de $c$ a partir do declive da reta e comparação com valores tabelados (erro percentual).
- **Esquema de Montagem Dinâmico**: Diagrama do circuito com animação de aquecimento pulsante.

### 🤖 Modo Automático
- **Simulação Acelerada**: O sistema realiza as medições automaticamente.
- **Visualização em Tempo Real**: Gráficos de evolução temporal e $T$ vs $E$.
- **Cálculos Imediatos**: Apresentação dos resultados e verificação científica.

## 🛠️ Configurações Disponíveis
O utilizador pode configurar:
- **Material do Bloco**: Alumínio, Cobre, Chumbo, Ferro ou Latão.
- **Massa do Bloco**: De 0.1 a 5.0 kg.
- **Parâmetros Elétricos**: Tensão (V) e Corrente (A) da fonte.
- **Condições Iniciais**: Temperatura inicial e tempo total de aquecimento.

## 📦 Como Instalar e Correr

1. Certifique-se de que tem o Python instalado.
2. Instale as dependências necessárias:
   ```bash
   pip install -r requirements.txt
   ```
3. Execute o simulador:
   ```bash
   streamlit run app.py
   ```

## 📐 Fundamento Físico
O simulador baseia-se na lei do aquecimento:
$$E = m \cdot c \cdot \Delta T$$
Transformando na equação da reta para o gráfico:
$$\Delta T = \frac{1}{m \cdot c} \cdot E$$
Onde o declive ($m$) do gráfico $\Delta T = f(E)$ permite isolar e calcular a capacidade térmica mássica.

---
*Desenvolvido para apoio escolar e demonstrações laboratoriais virtuais.*
