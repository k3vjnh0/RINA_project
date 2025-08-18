import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load Excel file
file_path = "Input_data_visualization.xlsx"
xls = pd.ExcelFile(file_path)


# ==============================
# SHEET 1: Box Plot
# ==============================
df1 = pd.read_excel(xls, "Sheet1")

# Format Date column -> keep only DD-MM-YYYY
df1["Date"] = pd.to_datetime(df1["Date"]).dt.strftime("%d-%m-%Y")

#Box plot with date and CIF%
plt.figure(figsize=(10,6))
sns.boxplot(
    data=df1,
    x="Date",
    y="CIF%_average"
)
plt.title("CIF% Average Distribution by Date", fontsize=14)
plt.xlabel("Date")
plt.ylabel("CIF% Average")
#Mean
means = df1.groupby("Date")["CIF%_average"].mean()
for i, (date, mean) in enumerate(means.items()):
    plt.text(i, mean, f"{mean:.2f}", ha='center', va='bottom', fontsize=10, color='black', fontweight='bold')
plt.tight_layout()
plt.show()


#Box plot with date and LAI_average 
plt.figure(figsize=(10,6))
sns.boxplot(
    data=df1,
    x="Treatment",
    y="LAI_average"
)
plt.title("LAI Average Distribution by Treatment", fontsize=14)
plt.xlabel("Treatment")
plt.ylabel("LAI Average")
#Mean
means = df1.groupby("Treatment")["LAI_average"].mean()
for i, (treatment, mean) in enumerate(means.items()):
    plt.text(i, mean, f"{mean:.2f}", ha='center', va='bottom', fontsize=10, color='black', fontweight='bold')
plt.tight_layout()
plt.show()


#Box plot with Planted ,treatment and CIF%_average
plt.figure(figsize=(10,6))
sns.boxplot(
    data=df1,
    x="Treatment",
    y="CIF%_average",
    hue="Planted"   
)
plt.title("CIF% Average Distribution by Treatment and Planted Position", fontsize=14)
plt.xlabel("Treatment")
plt.ylabel("CIF% Average")
#Mean
means = df1.groupby(["Treatment", "Planted"])["CIF%_average"].mean()
positions = list(df1["Planted"].unique())
for i, treatment in enumerate(df1["Treatment"].unique()):
    for j, position in enumerate(positions):
        mean = means.get((treatment, position), None)
        if mean is not None:
            # Offset for text position
            offset = -0.2 if j == 0 else 0.2
            plt.text(i + offset, mean, f"{mean:.2f}", ha='center', va='bottom', fontsize=10, color='black', fontweight='bold')
plt.tight_layout()
plt.show()


#Box plot with Planted ,treatment and LAI_average
plt.figure(figsize=(10,6))
sns.boxplot(
    data=df1,
    x="Treatment",
    y="LAI_average",
    hue="Planted"
)
plt.title("LAI Average Distribution by Treatment and Planted Position", fontsize=14)
plt.xlabel("Treatment")
plt.ylabel("LAI Average")
#Mean
means = df1.groupby(["Treatment", "Planted"])["LAI_average"].mean()
positions = list(df1["Planted"].unique())
for i, treatment in enumerate(df1["Treatment"].unique()):
    for j, position in enumerate(positions):
        mean = means.get((treatment, position), None)
        if mean is not None:
            # Offset for text position
            offset = -0.2 if j == 0 else 0.2
            plt.text(i + offset, mean, f"{mean:.2f}", ha='center', va='bottom', fontsize=10, color='black', fontweight='bold')
plt.tight_layout()
plt.show()



# ==============================
# SHEET 2:
# ==============================
df2 = pd.read_excel(xls, "Sheet2")

# Format Date column -> keep only DD-MM-YYYY
df2["Date"] = pd.to_datetime(df2["Date"]).dt.strftime("%d-%m-%Y")

#Line chart for CIF%
plt.figure(figsize=(10,6))
sns.lineplot(
    data=df2,
    x="Date",
    y="CIF%_average",
    hue="Treatment",
    marker="o",
    palette="tab10",  # tab10 does not use green for first colors
    ci=None # Remove the confidence interval area
)

# Calculate mean and std for each (Date, Treatment)
grouped = df2.groupby(["Date", "Treatment"])["CIF%_average"].agg(['mean', 'std']).reset_index()

# Get the color palette used by seaborn
palette = sns.color_palette("tab10", n_colors=len(df2["Treatment"].unique()))
treatment_list = list(df2["Treatment"].unique())
color_map = {treatment: palette[i] for i, treatment in enumerate(treatment_list)}

# Draw std as error bars
for _, row in grouped.iterrows():
    plt.errorbar(
        row["Date"], row["mean"],
        yerr=row["std"] if not pd.isna(row["std"]) else 0,
        fmt='none', ecolor=color_map[row["Treatment"]], elinewidth=1.5, capsize=4, alpha=0.8
    )

plt.title("Average CIF% by Treatment at Each Timepoint", fontsize=14)
plt.ylabel("Average CIF%")
plt.xlabel("Date")
plt.legend(title="Treatment")
plt.tight_layout()
plt.show()


#Line chart for LAI average
plt.figure(figsize=(10,6))
sns.lineplot(
    data=df2,
    x="Date",
    y="LAI_average",
    hue="Treatment",
    marker="o",
    palette="tab10",  # tab10 does not use green for first colors
    ci=None # Remove the confidence interval area
)

# Calculate mean and std for each (Date, Treatment)
grouped = df2.groupby(["Date", "Treatment"])["LAI_average"].agg(['mean', 'std']).reset_index()

# Get the color palette used by seaborn
palette = sns.color_palette("tab10", n_colors=len(df2["Treatment"].unique()))
treatment_list = list(df2["Treatment"].unique())
color_map = {treatment: palette[i] for i, treatment in enumerate(treatment_list)}

# Draw std as error bars
for _, row in grouped.iterrows():
    plt.errorbar(
        row["Date"], row["mean"],
        yerr=row["std"] if not pd.isna(row["std"]) else 0,
        fmt='none', ecolor=color_map[row["Treatment"]], elinewidth=1.5, capsize=4, alpha=0.8
    )

plt.title("Average LAI by Treatment at Each Timepoint", fontsize=14)
plt.ylabel("Average LAI")
plt.xlabel("Date")
plt.legend(title="Treatment")
plt.tight_layout()
plt.show()



