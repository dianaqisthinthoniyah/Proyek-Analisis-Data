import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Load data
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
day_df = pd.read_csv(os.path.join(DATA_DIR, "day.csv"))
hour_df = pd.read_csv(os.path.join(DATA_DIR, "hour.csv"))

# Preprocessing
day_df["dteday"] = pd.to_datetime(day_df["dteday"])
hour_df["dteday"] = pd.to_datetime(hour_df["dteday"])

st.title("Bike Sharing Dashboard")
st.markdown("Analisis data penyewaan sepeda berdasarkan data harian dan per jam.")

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "Faktor Lonjakan Penyewaan 2011",
        "Pola Penyewaan per Jam",
        "Casual vs Registered 2012",
        "Korelasi Variabel",
    ]
)

# Tab 1: Faktor Lonjakan Penyewaan 2011
with tab1:
    st.header("Faktor Lonjakan Penyewaan Sepeda Tahun 2011")
    day_2011 = day_df[day_df["yr"] == 0]
    rerata_harian = day_2011["cnt"].mean()
    season_avg = day_2011.groupby("season")["cnt"].mean()
    weather_avg = day_2011.groupby("weathersit")["cnt"].mean()
    workingday_avg = day_2011.groupby("workingday")["cnt"].mean()
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle("Faktor Lonjakan Penyewaan Sepeda Tahun 2011", fontsize=14)
    axes[0].bar(["Spring", "Summer", "Fall", "Winter"], season_avg, color="steelblue")
    axes[0].axhline(y=rerata_harian, color="red", linestyle="--", label="Rerata Harian")
    axes[0].set_title("Rerata per Musim")
    axes[0].legend()
    axes[1].bar(["Cerah", "Berawan", "Hujan/Salju"], weather_avg, color="steelblue")
    axes[1].axhline(y=rerata_harian, color="red", linestyle="--", label="Rerata Harian")
    axes[1].set_title("Rerata per Cuaca")
    axes[1].legend()
    axes[2].bar(["Libur", "Hari Kerja"], workingday_avg, color="steelblue")
    axes[2].axhline(y=rerata_harian, color="red", linestyle="--", label="Rerata Harian")
    axes[2].set_title("Rerata Hari Kerja vs Libur")
    axes[2].legend()
    st.pyplot(fig)

# Tab 2: Pola Penyewaan per Jam
with tab2:
    st.header("Pola Penyewaan Sepeda per Jam")
    workingday_labels = {0: "Hari Libur", 1: "Hari Kerja"}
    colors = {0: "steelblue", 1: "darkorange"}
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("Pola Penyewaan Sepeda per Jam", fontsize=14)
    for wd in [0, 1]:
        data = hour_df[hour_df["workingday"] == wd].groupby("hr")["cnt"].mean()
        axes[wd].plot(
            data.index, data.values, color=colors[wd], marker="o", markersize=4
        )
        axes[wd].set_title(workingday_labels[wd])
        axes[wd].set_xlabel("Jam")
        axes[wd].set_ylabel("Rerata Penyewaan")
        axes[wd].set_xticks(range(0, 24))
    st.pyplot(fig)

# Tab 3: Casual vs Registered 2012
with tab3:
    st.header("Perbandingan Casual vs Registered per Musim 2012")
    day_2012 = day_df[day_df["yr"] == 1]
    season_labels = ["Spring", "Summer", "Fall", "Winter"]
    day_2012_season = day_2012.groupby("season")[["casual", "registered"]].mean()
    x = np.arange(len(season_labels))
    width = 0.35
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(
        x - width / 2,
        day_2012_season["casual"],
        width,
        label="Casual",
        color="steelblue",
    )
    ax.bar(
        x + width / 2,
        day_2012_season["registered"],
        width,
        label="Registered",
        color="darkorange",
    )
    ax.set_title("Rerata Penyewaan Casual vs Registered per Musim 2012")
    ax.set_xlabel("Musim")
    ax.set_ylabel("Rerata Penyewaan")
    ax.set_xticks(x)
    ax.set_xticklabels(season_labels)
    ax.legend()
    st.pyplot(fig)

# Tab 4: Korelasi Variabel
with tab4:
    st.header("Korelasi Antar Variabel (day.csv)")
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(day_df.corr(), annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
    ax.set_title("Korelasi Antar Variabel")
    st.pyplot(fig)
