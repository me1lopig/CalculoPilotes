import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def _safe_filename(txt):
    txt = str(txt)
    for bad in [" ", "/", "\\", ":", "*", "?", "\"", "<", ">", "|"]:
        txt = txt.replace(bad, "_")
    return txt

def _script_dir():
    return os.path.dirname(os.path.abspath(__file__))

def plot_depth_vs_blows_png_groups(
    excel_full_path,
    out_dir_full_path,
    sheet_name=0,
    col_desc="Descripción Muestra",
    col_depth="Profundidad",
    col_blows="Número de Golpes",
    tick_step=10,
    curves_per_plot=10
):
    df = pd.read_excel(excel_full_path, sheet_name=sheet_name)
    df.columns = [str(c).strip() for c in df.columns]

    if col_desc not in df.columns:
        raise KeyError("No existe la columna " + col_desc + " en el Excel. Columnas: " + str(list(df.columns)))
    if col_depth not in df.columns:
        raise KeyError("No existe la columna " + col_depth + " en el Excel. Columnas: " + str(list(df.columns)))
    if col_blows not in df.columns:
        raise KeyError("No existe la columna " + col_blows + " en el Excel. Columnas: " + str(list(df.columns)))

    df[col_depth] = pd.to_numeric(df[col_depth], errors="coerce")
    df[col_blows] = pd.to_numeric(df[col_blows], errors="coerce")

    df_plot = df.dropna(subset=[col_desc, col_depth, col_blows]).copy()
    df_plot[col_desc] = df_plot[col_desc].astype(str)
    df_plot = df_plot.sort_values([col_desc, col_depth])

    if df_plot.shape[0] == 0:
        raise ValueError("No hay filas válidas después de filtrar. Revisa NaNs y nombres de columnas.")

    os.makedirs(out_dir_full_path, exist_ok=True)

    max_blows_val = float(np.nanmax(df_plot[col_blows].values))
    if not np.isfinite(max_blows_val):
        raise ValueError("No se pudo calcular el máximo de " + col_blows)

    max_tick = int(np.ceil(max_blows_val / float(tick_step)) * tick_step)
    if max_tick <= 0:
        max_tick = tick_step

    x_ticks = list(range(0, max_tick + 1, tick_step))

    unique_desc = sorted(df_plot[col_desc].unique())
    chunks = [unique_desc[i:i + curves_per_plot] for i in range(0, len(unique_desc), curves_per_plot)]
    total_groups = len(chunks)

    saved_paths = []

    for group_idx, desc_chunk in enumerate(chunks, start=1):
        first_desc = desc_chunk[0]
        last_desc = desc_chunk[-1]

        title_txt = "Profundidad vs Número de Golpes - " + first_desc + " a " + last_desc
        file_stub = "profundidad_vs_golpes_" + _safe_filename(first_desc) + "_a_" + _safe_filename(last_desc)
        out_path = os.path.join(out_dir_full_path, file_stub + ".png")

        cmap = plt.get_cmap("tab10")
        color_map = {desc: cmap(i % 10) for i, desc in enumerate(desc_chunk)}

        plt.figure(figsize=(9, 7))
        plt.grid(True, which="major", alpha=0.3)

        for desc in desc_chunk:
            sub = df_plot[df_plot[col_desc] == desc].sort_values(col_depth)
            plt.plot(
                sub[col_blows],
                sub[col_depth],
                marker="o",
                linewidth=1.6,
                label=desc,
                color=color_map[desc]
            )

        plt.gca().invert_yaxis()
        plt.xlabel(col_blows)
        plt.ylabel(col_depth)
        plt.title(title_txt + " (Grupo " + str(group_idx) + " de " + str(total_groups) + ")")
        plt.xticks(x_ticks)
        plt.xlim(0, max_tick)
        plt.grid(True, axis="x", alpha=0.35)
        plt.legend(title=col_desc, loc="best")
        plt.tight_layout()

        plt.savefig(out_path, dpi=220, format="png")
        plt.close()

        saved_paths.append(out_path)

    return saved_paths

if __name__ == "__main__":
    EXCEL_FILENAME = "DPRG.xlsx"

    base_dir = _script_dir()
    excel_path = os.path.join(base_dir, EXCEL_FILENAME)

    if not os.path.exists(excel_path):
        raise FileNotFoundError("No encontré el Excel en la misma carpeta del script: " + excel_path)

    # Guardar las imágenes en el mismo directorio del script
    out_dir = base_dir

    paths = plot_depth_vs_blows_png_groups(
        excel_full_path=excel_path,
        out_dir_full_path=out_dir,
        sheet_name=0,
        tick_step=10,
        curves_per_plot=10
    )

    for p in paths:
        print(p)