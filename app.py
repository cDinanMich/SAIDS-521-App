import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

st.set_page_config(page_title="2025 Fantasy Football Dashboard", layout="wide")
st.title("2025 Fantasy Football Exploration Dashboard")

POSITION_COLORS = {"RB": '#d62728', 'QB': '#1f77b4', 'WR': '#ff7f0e', 'TE': '#2ca02c'}

# --- 1. Load Data & Pre-calculate Full-Season Player Percentiles ---
@st.cache_data
def load_and_prep_data():
    df = pd.read_csv("data/clean_weekly_data.csv")
    
    # Aggregate raw PPR points across all 17 weeks per player and position
    season_totals = (
        df.groupby(['player_id', 'position'], as_index=False)['fantasy_points_ppr']
        .sum()
        .rename(columns={'fantasy_points_ppr': 'season_raw_ppr'})
    )
    season_totals['pos_percentile'] = (
        season_totals.groupby('position')['season_raw_ppr']
        .rank(pct=True) * 100
    )
    return df.merge(
        season_totals[['player_id', 'position', 'pos_percentile']],
        on=['player_id', 'position'],
        how='left'
    )

dashboard_df = load_and_prep_data()

# --- 2. Sidebar Filters ---
st.sidebar.header("Dashboard Filters")

all_divisions = sorted(dashboard_df['division'].dropna().unique().tolist())
all_teams = sorted(dashboard_df['team'].dropna().unique().tolist())

selected_divisions = st.sidebar.multiselect("Divisions", options=all_divisions, default=all_divisions)
selected_teams = st.sidebar.multiselect("Teams", options=all_teams, default=all_teams)

min_week, max_week = int(dashboard_df['week'].min()), int(dashboard_df['week'].max())
week_range = st.sidebar.slider("Weeks Included", min_value=min_week, max_value=max_week, value=(min_week, max_week))

pct_range = st.sidebar.slider("Player Season Percentile (by Position)", min_value=0, max_value=100, value=(0, 100))

# Filter dataset
mask = (
    dashboard_df['division'].isin(selected_divisions) &
    dashboard_df['team'].isin(selected_teams) &
    dashboard_df['week'].between(week_range[0], week_range[1]) &
    dashboard_df['pos_percentile'].between(pct_range[0], pct_range[1])
)
df = dashboard_df[mask].copy()

if df.empty:
    st.warning("No data matches your current filter selections.")
    st.stop()

# --- 3. Build the 4 Visualizations ---
def make_lollipop(data):
    idx_max_raw = data.groupby('week')['fantasy_points_ppr'].idxmax()
    df_top_raw = data.loc[idx_max_raw].sort_values('week').reset_index(drop=True)

    idx_max_norm = data.groupby('week')['normalized_ppr'].idxmax()
    df_top_norm = data.loc[idx_max_norm].sort_values('week').reset_index(drop=True)

    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=("Weekly Top PPR Scorer", "Weekly Top Normalized Scorer"),
        vertical_spacing=0.25
    )

    def _add_lollipops(row_idx, target_df, val_col, val_label, is_norm=False):
        fmt = ":.2f" if is_norm else ":.1f"
        for pos in target_df['position'].unique():
            pos_df = target_df[target_df['position'] == pos]
            color = POSITION_COLORS.get(pos, '#333333')

            for _, row in pos_df.iterrows():
                fig.add_trace(
                    go.Scatter(
                        x=[row['week'], row['week']], y=[0, row[val_col]],
                        mode='lines', line=dict(color='lightgray', width=2),
                        showlegend=False, hoverinfo='skip'
                    ),
                    row=row_idx, col=1
                )

            custom_data = list(zip(pos_df['player_name'], pos_df['position'], pos_df['team']))
            fig.add_trace(
                go.Scatter(
                    x=pos_df['week'], y=pos_df[val_col],
                    mode='markers', marker=dict(size=11, color=color),
                    name=pos, legendgroup=pos, showlegend=(row_idx == 1),
                    customdata=custom_data,
                    hovertemplate=(
                        "<b>Name:</b> %{customdata[0]} (%{customdata[2]})<br>"
                        f"<b>{val_label}:</b> %{{y{fmt}}}<br>"
                        "<b>Week:</b> %{x}<extra></extra>"
                    )
                ),
                row=row_idx, col=1
            )

    _add_lollipops(1, df_top_raw, 'fantasy_points_ppr', 'PPR Fantasy Points', is_norm=False)
    _add_lollipops(2, df_top_norm, 'normalized_ppr', 'Normalized Fantasy Points', is_norm=True)

    fig.update_layout(
        height=480, template="simple_white",
        margin=dict(l=40, r=20, t=40, b=40),
        legend=dict(title="<b>Position</b>", orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1)
    )
    fig.update_xaxes(title_text="Week", row=2, col=1)
    fig.update_yaxes(title_text="PPR Points", row=1, col=1, rangemode="tozero")
    fig.update_yaxes(title_text="Norm Points", row=2, col=1, rangemode="tozero")
    return fig

def make_treemap(data):
    season_data = (
        data.groupby(['position', 'player_id', 'player_name'], as_index=False)
        .agg(normalized_ppr=('normalized_ppr', 'sum'), fantasy_points_ppr=('fantasy_points_ppr', 'sum'))
    )
    season_data = season_data[season_data['normalized_ppr'] > 0]
    if season_data.empty:
        return None

    treemap_colors = {"(?)": "lightgrey", **POSITION_COLORS}
    fig = px.treemap(
        season_data,
        path=[px.Constant('Selected Range Points (Normalized)'), 'position', 'player_name'],
        values='normalized_ppr',
        color='position',
        color_discrete_map=treemap_colors,
        hover_name='player_name',
        hover_data=['fantasy_points_ppr']
    )
    fig.update_traces(
        hovertemplate=(
            '<b>%{label}</b><br>'
            'Raw Points: %{customdata[0]:.1f}<br>'
            'Normalized Points: %{value:.1f}<extra></extra>'
        ),
        root_color="lightgrey",
        insidetextfont=dict(color="white"),
        marker=dict(line=dict(width=1.5, color="grey"))
    )
    fig.update_layout(height=480, margin=dict(l=10, r=10, t=20, b=10))
    return fig

def make_timeseries(data):
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    sns.lineplot(data=data, x='week', y='fantasy_points_ppr', hue='position', palette=POSITION_COLORS, ax=ax)
    ax.set_xlabel("Week")
    ax.set_ylabel("Fantasy Points (PPR)")
    ax.legend(title="Position")
    sns.despine(ax=ax)
    fig.tight_layout()
    return fig

def make_pairplot(data):
    g = sns.pairplot(
        data=data,
        x_vars=['fantasy_points_ppr', 'normalized_ppr'],
        y_vars=[
            'passing_yards', 'passing_tds', 'passing_interceptions',
            'rushing_yards', 'rushing_tds', 'receiving_yards',
            'receiving_tds', 'receptions'
        ],
        hue='position',
        palette=POSITION_COLORS,
        height=2.2,
        aspect=1.4,
        plot_kws={'alpha': 0.6, 's': 22}
    )
    sns.move_legend(g, "upper center", bbox_to_anchor=(0.5, 1.02), ncol=4, title=None, frameon=False)
    g.figure.tight_layout(rect=[0, 0, 1, 0.98])
    return g.figure

# --- 4. Render 2x2 Grid ---
row1_col1, row1_col2 = st.columns(2)
with row1_col1:
    st.subheader("1. Weekly Top Performers")
    st.plotly_chart(make_lollipop(df), use_container_width=True)

with row1_col2:
    st.subheader("2. Cumulative Positional Value")
    treemap_fig = make_treemap(df)
    if treemap_fig:
        st.plotly_chart(treemap_fig, use_container_width=True)
    else:
        st.info("No players with positive normalized points in this filter range.")

row2_col1, row2_col2 = st.columns(2)
with row2_col1:
    st.subheader("3. Weekly Scoring Trends")
    ts_fig = make_timeseries(df)
    st.pyplot(ts_fig)
    plt.close(ts_fig)

with row2_col2:
    st.subheader("4. Stat-to-Point Relationships")
    with st.container(height=640):
        pp_fig = make_pairplot(df)
        st.pyplot(pp_fig)
        plt.close(pp_fig)