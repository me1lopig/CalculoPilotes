import argparse
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def _safe_filename(txt):
    txt = str(txt)
    # Conservador para Windows/Mac/Linux
    for bad in [" ", "/", "\\", ":", "*", "?", "\"", "<", ">", "|"]:
        txt = txt.replace(bad, "_")
    return txt


def plot_depth_vs_blows_png_groups(
    excel_path,
    out_dir="salidas_graficas",
    sheet_name=0,
    col_desc="Descripción Muestra",
    col_depth="Profundidad",
    col_blows="Número de Golpes",
    tick_step=10,
    curves_per_plot=10
):
    df = pd.read_excel(excel_path, sheet_name=sheet_name)
    df.columns = [str(c).strip() for c in df.columns]

    df[col_depth] = pd.to_numeric(df[col_depth], errors="coerce")
    df[col_blows] = pd.to_numeric(df[col_blows], errors="coerce")

    df_plot = df.dropna(subset=[col_desc, col_depth, col_blows]).copy()
    df_plot[col_desc] = df_plot[col_desc].astype(str)
    df_plot = df_plot.sort_values([col_desc, col_depth])

    os.makedirs(out_dir, exist_ok=True)

    max_blows_val = float(np.nanmax(df_plot[col_blows].values))
    max_tick = int(np.ceil(max_blows_val / float(tick_step)) * tick_step)
    x_ticks = list(range(0, max_tick + 1, tick_step))

    unique_desc = sorted(df_plot[col_desc].unique())
    chunks = [unique_desc[i:i + curves_per_plot] for i in range(0, len(unique_desc), curves_per_plot)]

    saved_paths = []
    total_groups = len(chunks)

    for group_idx, desc_chunk in enumerate(chunks, start=1):
        first_desc = desc_chunk[0]
        last_desc = desc_chunk[-1]

        title_txt = "Profundidad vs Número de Golpes - " + first_desc + " a " + last_desc
        file_stub = "profundidad_vs_golpes_" + _safe_filename(first_desc) + "_a_" + _safe_filename(last_desc)
        out_path = os.path.join(out_dir, file_stub + ".png")

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
    parser = argparse.ArgumentParser(
        description="Genera PNGs por grupos (hasta 10 curvas por imagen) de Profundidad vs Número de Golpes."
    )
    parser.add_argument("excel_path", help="Ruta al archivo Excel (.xlsx)")
    parser.add_argument("--out_dir", default="salidas_graficas", help="Carpeta de salida")
    parser.add_argument("--sheet", default=0, help="Hoja (índice o nombre). Default 0")
    parser.add_argument("--tick_step", type=int, default=10, help="Separación de ticks del eje X. Default 10")
    parser.add_argument("--curves_per_plot", type=int, default=10, help="Curvas por imagen. Default 10")
    args = parser.parse_args()

    paths = plot_depth_vs_blows_png_groups(
        args.excel_path,
        out_dir=args.out_dir,
        sheet_name=args.sheet,
        tick_step=args.tick_step,
        curves_per_plot=args.curves_per_plot
    )

    for p in paths:
        print(p)