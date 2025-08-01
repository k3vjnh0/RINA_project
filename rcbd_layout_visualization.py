import random

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import pandas as pd

# Define parameters
blocks = 4
treatments = ["Mulch", "Water Absorbent", "Soil Amendment", "Control"]
mulch_types = ["Natural Grass", "Cowpea", "Sunnhemp"]

# Color settings
treatment_colors = {
    "Mulch": "#a1d99b",  # light green
    "Water Absorbent": "#9ecae1",  # blue
    "Soil Amendment": "#fdae6b",  # orange
    "Control": "#f0f0f0",  # grey
}
mulch_shades = {"Natural Grass": "#41ab5d", "Cowpea": "#238b45", "Sunnhemp": "#006d2c"}

# Prepare randomized layout
layout_data = []
for block in range(1, blocks + 1):
    random.shuffle(treatments)
    for plot_num, treatment in enumerate(treatments, start=1):
        mulch_type = None
        if treatment == "Mulch":
            mulch_type = random.choice(mulch_types)
            label = f"{treatment} – {mulch_type}"
        else:
            label = treatment
        layout_data.append(
            {
                "Block": block,
                "Plot": plot_num,
                "Treatment": treatment,
                "Mulch Type": mulch_type,
                "Label": f"Block {block}\n{label}",
            }
        )

df = pd.DataFrame(layout_data)

# Export layout to CSV
df.to_csv("rcbd_layout.csv", index=False)

# Create plot
fig, ax = plt.subplots(figsize=(12, 8))
for idx, row in df.iterrows():
    x = row["Plot"] - 1
    y = blocks - row["Block"]
    color = treatment_colors[row["Treatment"]]

    # For mulch, override color based on mulch type
    if row["Treatment"] == "Mulch":
        color = mulch_shades[row["Mulch Type"]]

    # Draw plot rectangle
    rect = plt.Rectangle((x, y), 1, 1, facecolor=color, edgecolor="black")
    ax.add_patch(rect)
    ax.text(x + 0.5, y + 0.5, row["Label"], ha="center", va="center", fontsize=8)

# Axis settings
ax.set_xlim(0, 4)
ax.set_ylim(0, 4)
ax.set_xticks([])
ax.set_yticks([])
ax.set_title("RCBD Layout – Cotton Soil Treatment Trial", fontsize=14, weight="bold")
ax.set_aspect("equal")

# Build legend
legend_handles = [
    mpatches.Patch(color=treatment_colors["Water Absorbent"], label="Water Absorbent"),
    mpatches.Patch(color=treatment_colors["Soil Amendment"], label="Soil Amendment"),
    mpatches.Patch(color=treatment_colors["Control"], label="Control"),
    mpatches.Patch(color=mulch_shades["Natural Grass"], label="Mulch – Natural Grass"),
    mpatches.Patch(color=mulch_shades["Cowpea"], label="Mulch – Cowpea"),
    mpatches.Patch(color=mulch_shades["Sunnhemp"], label="Mulch – Sunnhemp"),
]
ax.legend(
    handles=legend_handles, loc="upper center", bbox_to_anchor=(0.5, -0.05), ncol=3
)

# Save output
plt.tight_layout()
plt.savefig("rcbd_layout.png", dpi=300)
plt.show()
