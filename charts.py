import matplotlib.pyplot as plt


def generate_pie_chart(data):
    labels = ["Despensa", "Educacion", "Transporte", "Salud", "Salidas"]

    fig, ax = plt.subplots(figsize=(6, 6))

    patches, texts, pcts = ax.pie(
        data,
        labels=labels,
        autopct="%.1f%%",
        wedgeprops={"linewidth": 3.0, "edgecolor": "white"},
        textprops={"size": "x-large"},
        startangle=90,
    )

    # For each wedge, set the corresponding text label color to the wedge's
    # face color.
    for i, patch in enumerate(patches):
        texts[i].set_color(patch.get_facecolor())

    plt.setp(pcts, color="white")
    plt.setp(texts, fontweight=600)
    ax.set_title("Gastos - 2 de marzo del 2024", fontsize=18)
    plt.tight_layout()

    plt.show()
