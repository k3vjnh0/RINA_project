import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load Excel file
file_path = "input data.xlsx"
xls = pd.ExcelFile(file_path)

# ==============================
# SHEET 1: Grouped Bar Chart
# ==============================
df1 = pd.read_excel(xls, "Sheet1")

# Format Date column -> keep only DD-MM-YYYY
df1["Date"] = pd.to_datetime(df1["Date"]).dt.strftime("%d-%m-%Y")

plt.figure(figsize=(10,6))
sns.barplot(
    data=df1,
    x="Treatment",
    y="Height_Total_Average",
    hue="Date",
    errorbar="sd"   # show standard deviation error bars
)
plt.title("Average Height by Treatment at Each Timepoint", fontsize=14)
plt.ylabel("Average Height")
plt.xlabel("Treatment")
plt.legend(title="Date")
plt.tight_layout()
plt.show()


#Line chart for treatment
plt.figure(figsize=(10,6))
sns.lineplot(
    data=df1,
    x="Date",
    y="Height_Total_Average",
    hue="Treatment",
    marker="o",
    palette="tab10",  # tab10 does not use green for first colors
    ci=None # Remove the confidence interval area
)

# Calculate mean and std for each (Date, Treatment)
grouped = df1.groupby(["Date", "Treatment"])["Height_Total_Average"].agg(['mean', 'std']).reset_index()

# Get the color palette used by seaborn
palette = sns.color_palette("tab10", n_colors=len(df1["Treatment"].unique()))
treatment_list = list(df1["Treatment"].unique())
color_map = {treatment: palette[i] for i, treatment in enumerate(treatment_list)}

# Draw std as error bars
for _, row in grouped.iterrows():
    plt.errorbar(
        row["Date"], row["mean"],
        yerr=row["std"] if not pd.isna(row["std"]) else 0,
        fmt='none', ecolor=color_map[row["Treatment"]], elinewidth=1.5, capsize=4, alpha=0.8
    )

plt.title("Average Height by Treatment at Each Timepoint", fontsize=14)
plt.ylabel("Average Height")
plt.xlabel("Date")
plt.legend(title="Treatment")
plt.tight_layout()
plt.show()


# ==============================
# SHEET 2: Interaction Plot
# ==============================
df2 = pd.read_excel(xls, "Sheet2")

# Format Date column -> keep only DD-MM-YYYY
df2["Date"] = pd.to_datetime(df2["Date"]).dt.strftime("%d-%m-%Y")

g = sns.FacetGrid(df2, col="Date", height=5, aspect=1.2)
g.map_dataframe(
    sns.lineplot,
    x="Position",
    y="SPAD_Average",
    hue="Treatment",
    marker="o",
    ci=None
)
g.add_legend()
# Move the legend to the bottom
if g._legend is not None:
    g._legend.set_bbox_to_anchor((0.98, 0.2), transform=g.fig.transFigure)
g.set_axis_labels("Position (Top vs Bottom)", "SPAD Average")
plt.subplots_adjust(top=0.8)
g.fig.suptitle("Treatment × Position × Date Interaction Plot")
plt.show()

#Box plot with date and SPAD
plt.figure(figsize=(10,6))
sns.boxplot(
    data=df2,
    x="Date",
    y="SPAD_Average"
)
plt.title("SPAD Average Distribution by Date", fontsize=14)
plt.xlabel("Date")
plt.ylabel("SPAD Average")
#Mean
means = df2.groupby("Date")["SPAD_Average"].mean()
for i, (date, mean) in enumerate(means.items()):
    plt.text(i, mean, f"{mean:.2f}", ha='center', va='bottom', fontsize=10, color='black', fontweight='bold')
plt.tight_layout()
plt.show()


#Box plot with date and SPAD
plt.figure(figsize=(10,6))
sns.boxplot(
    data=df2,
    x="Treatment",
    y="SPAD_Average"
)
plt.title("SPAD Average Distribution by Treatment", fontsize=14)
plt.xlabel("Treatment")
plt.ylabel("SPAD Average")
#Mean
means = df2.groupby("Treatment")["SPAD_Average"].mean()
for i, (treatment, mean) in enumerate(means.items()):
    plt.text(i, mean, f"{mean:.2f}", ha='center', va='bottom', fontsize=10, color='black', fontweight='bold')
plt.tight_layout()
plt.show()


#Box plot with position ,treatment and SPAD
plt.figure(figsize=(10,6))
sns.boxplot(
    data=df2,
    x="Treatment",
    y="SPAD_Average",
    hue="Position"   
)
plt.title("SPAD Average Distribution by Treatment and Position", fontsize=14)
plt.xlabel("Treatment")
plt.ylabel("SPAD Average")
#Mean
means = df2.groupby(["Treatment", "Position"])["SPAD_Average"].mean()
positions = list(df2["Position"].unique())
for i, treatment in enumerate(df2["Treatment"].unique()):
    for j, position in enumerate(positions):
        mean = means.get((treatment, position), None)
        if mean is not None:
            # Offset for text position
            offset = -0.2 if j == 0 else 0.2
            plt.text(i + offset, mean, f"{mean:.2f}", ha='center', va='bottom', fontsize=10, color='black', fontweight='bold')
plt.tight_layout()
plt.show()


# ==============================
# SHEET 3: Box Plots
# ==============================
df3 = pd.read_excel(xls, "Sheet3")
df3.columns = df3.columns.str.strip()  # remove hidden spaces

# Format Date column -> keep only DD-MM-YYYY
df3["Date"] = pd.to_datetime(df3["Date"]).dt.strftime("%d-%m-%Y")

# Reshape to long format
df3_long = df3.melt(
    id_vars=["Date", "Treatment"],
    value_vars=["Predawn_Total_Average", "Postdawn_Total_Average"],
    var_name="Time",
    value_name="Water_Potential"
)

# Rename Time values for cleaner labels
df3_long["Time"] = df3_long["Time"].replace({
    "Predawn_Total_Average": "Predawn",
    "Postdawn_Total_Average": "Postdawn"
})

fig, axes = plt.subplots(1, 2, figsize=(14,6), sharey=True)

# Predawn
sns.boxplot(
    data=df3_long[df3_long["Time"]=="Predawn"],
    x="Treatment",
    y="Water_Potential",
    ax=axes[0]
)
axes[0].set_title("Predawn Water Potential")

# Add mean labelss
predawn_means = df3_long[df3_long["Time"]=="Predawn"].groupby("Treatment")["Water_Potential"].mean()
for i, (treatment, mean) in enumerate(predawn_means.items()):
    axes[0].text(i, mean, f"{mean:.2f}", ha='center', va='bottom', fontsize=10, color='black', fontweight='bold')


# Postdawn
sns.boxplot(
    data=df3_long[df3_long["Time"]=="Postdawn"],
    x="Treatment",
    y="Water_Potential",
    ax=axes[1]
)
axes[1].set_title("Postdawn Water Potential")

postdawn_means = df3_long[df3_long["Time"]=="Postdawn"].groupby("Treatment")["Water_Potential"].mean()
for i, (treatment, mean) in enumerate(postdawn_means.items()):
    axes[1].text(i, mean, f"{mean:.2f}", ha='center', va='bottom', fontsize=10, color='black', fontweight='bold')
    
fig.suptitle("Distribution of Water Potential by Treatment", fontsize=14)
plt.tight_layout()
plt.show()
