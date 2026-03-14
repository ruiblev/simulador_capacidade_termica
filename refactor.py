import sys

with open("app.py", "r") as f:
    lines = f.readlines()

start_idx = 0
for i, line in enumerate(lines):
    if line.startswith("col1, col2 = st.columns([1, 2])"):
        start_idx = i
        break

new_lines = lines[:start_idx]
new_lines.append("def run_simulation(is_manual=False):\n")
for line in lines[start_idx:]:
    if line == "\n":
        new_lines.append("\n")
    else:
        new_lines.append("    " + line)

new_lines.append("\n")
new_lines.append("tab_auto, tab_manual = st.tabs(['Modo Automático', 'Modo Manual'])\n")
new_lines.append("with tab_auto:\n")
new_lines.append("    run_simulation(is_manual=False)\n")
new_lines.append("with tab_manual:\n")
new_lines.append("    run_simulation(is_manual=True)\n")

with open("app.py", "w") as f:
    f.writelines(new_lines)
