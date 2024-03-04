import matplotlib.pyplot as plt


def generate_pie_chart(keys: list, values: list, chart_title: str):
    fig, ax = plt.subplots(figsize=(6, 6))

    patches, texts, pcts = ax.pie(
        values,
        labels=keys,
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
    ax.set_title(chart_title, fontsize=18)
    plt.tight_layout()

    output_file = f"{chart_title}.png"
    plt.savefig(output_file)

    return output_file
