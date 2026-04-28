import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

sns.set(style="dark")


def categorize_time(hour):
    if 5 <= hour < 10:
        return "Pagi"
    elif 10 <= hour < 15:
        return "Siang"
    elif 15 <= hour < 19:
        return "Sore"
    else:
        return "Malam"


@st.cache_data
def load_data():
    day_url = "https://drive.google.com/uc?export=download&id=1lB8FgL2ahWzxveqjrBdBuetmJR-C3A15"
    hour_url = "https://drive.google.com/uc?export=download&id=1dLPMV7fwcrDen9zNKKXgIiSTZLsPQmm_"

    day_df = pd.read_csv(day_url)
    hour_df = pd.read_csv(hour_url)

    for df in [day_df, hour_df]:
        df["dteday"] = pd.to_datetime(df["dteday"])
        if "instant" in df.columns:
            df.drop(columns=["instant"], inplace=True)

    day_df.rename(
        columns={
            "dteday": "date",
            "yr": "year",
            "mnth": "month",
            "weathersit": "weather",
            "hum": "humidity",
            "windspeed": "wind_speed",
            "cnt": "total_rentals",
        },
        inplace=True,
    )

    hour_df.rename(
        columns={
            "dteday": "date",
            "yr": "year",
            "mnth": "month",
            "hr": "hour",
            "weathersit": "weather",
            "hum": "humidity",
            "windspeed": "wind_speed",
            "cnt": "total_rentals",
        },
        inplace=True,
    )

    season_map = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
    weather_map = {1: "Clear", 2: "Mist/Cloudy", 3: "Light Rain/Snow"}

    for df in [day_df, hour_df]:
        df["season"] = df["season"].map(season_map).astype("category")
        df["weather"] = df["weather"].map(weather_map).astype("category")

    hour_df["time_category"] = hour_df["hour"].apply(categorize_time)

    return day_df, hour_df


# Load Data

day_df, hour_df = load_data()

# Sidebar

with st.sidebar:
    st.title("🚲 Bike Sharing")
    st.markdown("---")

    min_date = day_df["date"].min().date()
    max_date = day_df["date"].max().date()

    start_date, end_date = st.date_input(
        label="Rentang Waktu",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date],
    )

    st.markdown("---")

    all_weather = day_df["weather"].cat.categories.tolist()
    selected_weather = st.multiselect(
        "Kondisi Cuaca", options=all_weather, default=all_weather
    )

    all_seasons = ["Spring", "Summer", "Fall", "Winter"]
    selected_seasons = st.multiselect("Musim", options=all_seasons, default=all_seasons)

    st.markdown("---")
    st.caption("Bike Sharing Dataset Analysis\n")

# Filter Data

main_day_df = day_df[
    (day_df["date"].dt.date >= start_date)
    & (day_df["date"].dt.date <= end_date)
    & (day_df["weather"].isin(selected_weather))
    & (day_df["season"].isin(selected_seasons))
]

main_hour_df = hour_df[
    (hour_df["date"].dt.date >= start_date)
    & (hour_df["date"].dt.date <= end_date)
    & (hour_df["weather"].isin(selected_weather))
    & (hour_df["season"].isin(selected_seasons))
]

# Header

st.title("🚲 Bike Sharing Dashboard")
st.subheader("Analisis Penyewaan Sepeda Berdasarkan Faktor Musim, Cuaca, dan Waktu")
st.markdown("---")

if main_day_df.empty:
    st.warning(
        "⚠️ Tidak ada data yang sesuai dengan filter. Silakan ubah pilihan di sidebar."
    )
    st.stop()

# Metric Cards

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Penyewaan", f"{main_day_df['total_rentals'].sum():,.0f}")
col2.metric("Rerata Harian", f"{main_day_df['total_rentals'].mean():,.0f}")
col3.metric("Total Casual", f"{main_day_df['casual'].sum():,.0f}")
col4.metric("Total Registered", f"{main_day_df['registered'].sum():,.0f}")

st.markdown("---")

# Visualisasi 1:

st.subheader("Faktor yang Mempengaruhi Penyewaan Sepeda")

rerata_harian = main_day_df["total_rentals"].mean()

fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# Per Musim
season_order = ["Spring", "Summer", "Fall", "Winter"]
season_label_map = {
    "Spring": "Semi",
    "Summer": "Panas",
    "Fall": "Gugur",
    "Winter": "Dingin",
}
season_avg = (
    main_day_df.groupby("season", observed=True)["total_rentals"]
    .mean()
    .reindex([s for s in season_order if s in selected_seasons])
)
filtered_labels = [f"Musim\n{season_label_map[s]}" for s in season_avg.index]

axes[0].bar(filtered_labels, season_avg.values, color="steelblue")
axes[0].axhline(
    y=rerata_harian, color="red", linestyle="--", label=f"Rerata ({rerata_harian:.0f})"
)
axes[0].set_title("Rerata per Musim")
axes[0].set_xlabel("Musim")
axes[0].set_ylabel("Rerata Penyewaan")
axes[0].legend(fontsize=8)

# Per Cuaca
weather_label_map = {
    "Clear": "Cerah",
    "Mist/Cloudy": "Berawan",
    "Light Rain/Snow": "Hujan/Salju",
}
weather_avg = main_day_df.groupby("weather", observed=True)["total_rentals"].mean()
weather_labels_filtered = [weather_label_map.get(w, w) for w in weather_avg.index]

axes[1].bar(weather_labels_filtered, weather_avg.values, color="steelblue")
axes[1].axhline(
    y=rerata_harian, color="red", linestyle="--", label=f"Rerata ({rerata_harian:.0f})"
)
axes[1].set_title("Rerata per Cuaca")
axes[1].set_xlabel("Cuaca")
axes[1].set_ylabel("Rerata Penyewaan")
axes[1].legend(fontsize=8)
axes[1].tick_params(axis="x", rotation=15)

# Hari Kerja vs Libur
workingday_avg = main_day_df.groupby("workingday")["total_rentals"].mean()
wd_labels = ["Libur" if k == 0 else "Hari Kerja" for k in workingday_avg.index]

axes[2].bar(wd_labels, workingday_avg.values, color="steelblue")
axes[2].axhline(
    y=rerata_harian, color="red", linestyle="--", label=f"Rerata ({rerata_harian:.0f})"
)
axes[2].set_title("Rerata Hari Kerja vs Libur")
axes[2].set_xlabel("Jenis Hari")
axes[2].set_ylabel("Rerata Penyewaan")
axes[2].legend(fontsize=8)

plt.tight_layout()
st.pyplot(fig)
plt.close()

st.markdown("---")

# Visualisasi 2

st.subheader("Pola Penyewaan Sepeda per Jam")

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

workingday_labels = {0: "Hari Libur", 1: "Hari Kerja"}
colors_wd = {0: "steelblue", 1: "darkorange"}

for wd in [0, 1]:
    subset = main_hour_df[main_hour_df["workingday"] == wd]
    if not subset.empty:
        data = subset.groupby("hour")["total_rentals"].mean()
        axes[wd].plot(
            data.index, data.values, color=colors_wd[wd], marker="o", markersize=4
        )
    axes[wd].set_title(workingday_labels[wd])
    axes[wd].set_xlabel("Jam")
    axes[wd].set_ylabel("Rerata Penyewaan")
    axes[wd].set_xticks(range(0, 24, 2))
    axes[wd].tick_params(axis="x", rotation=0)

plt.tight_layout()
st.pyplot(fig)
plt.close()

st.markdown("---")

# Visualisasi 3

st.subheader("Perbandingan Pengguna Casual vs Registered per Musim")

season_order_fixed = [
    s for s in ["Spring", "Summer", "Fall", "Winter"] if s in selected_seasons
]
season_labels_fixed = [
    {
        "Spring": "Musim Semi",
        "Summer": "Musim Panas",
        "Fall": "Musim Gugur",
        "Winter": "Musim Dingin",
    }[s]
    for s in season_order_fixed
]

season_grouped = (
    main_day_df.groupby("season", observed=True)[["casual", "registered"]]
    .mean()
    .reindex(season_order_fixed)
)

fig, ax = plt.subplots(figsize=(9, 5))
x = np.arange(len(season_order_fixed))
width = 0.35

if len(x) > 0:
    ax.bar(
        x - width / 2,
        season_grouped["casual"],
        width,
        label="Casual",
        color="steelblue",
    )
    ax.bar(
        x + width / 2,
        season_grouped["registered"],
        width,
        label="Registered",
        color="darkorange",
    )

ax.set_title("Rerata Penyewaan Casual vs Registered per Musim")
ax.set_xlabel("Musim")
ax.set_ylabel("Rerata Penyewaan")
ax.set_xticks(x)
ax.set_xticklabels(season_labels_fixed)
ax.legend()

plt.tight_layout()
st.pyplot(fig)
plt.close()

st.markdown("---")

#  Visualisasi 4: Rerata Penyewaan per Kategori Waktu

st.subheader("Rerata Penyewaan Berdasarkan Kategori Waktu")

time_order = ["Pagi", "Siang", "Sore", "Malam"]
time_grouped = (
    main_hour_df.groupby("time_category")["total_rentals"]
    .mean()
    .reindex(time_order)
    .reset_index()
)

fig, ax = plt.subplots(figsize=(8, 5))
colors_time = ["#FFA500", "#87CEEB", "#FF6347", "#4B0082"]
ax.bar(time_grouped["time_category"], time_grouped["total_rentals"], color=colors_time)
ax.set_title("Rerata Penyewaan Sepeda Berdasarkan Kategori Waktu")
ax.set_xlabel("Kategori Waktu")
ax.set_ylabel("Rerata Penyewaan")

plt.tight_layout()
st.pyplot(fig)
plt.close()

st.markdown("---")
st.caption(
    "Dashboard Bike Sharing Dataset Analysis \n \n Fundamental Analisis Data 2026 "
)
