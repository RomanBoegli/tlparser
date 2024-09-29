import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
import plotly.graph_objects as go
import plotly.io as pio
from d3blocks import D3Blocks

from tlparser.utils import Utils
from tlparser.config import Configuration


class Viz:

    title_map = {
        "stats.agg.aps": "Atomic Propositions",
        "stats.agg.cops": "Comparison Operators",
        "stats.agg.lops": "Logical Operators",
        "stats.agg.tops": "Temporal Operators",
    }

    def __init__(self, config: Configuration, file):
        self.config = config
        self.data = pd.read_excel(file)

    def __get_file_name(self, prefix, suffix=".pdf"):
        os.makedirs(self.config.folder_data_out, exist_ok=True)
        return os.path.join(
            self.config.folder_data_out,
            f"{prefix}_{Utils.get_unique_filename()}{suffix}",
        )

    def __get_reduced_logic_order(self):
        return [
            item
            for item in self.config.logic_order
            if item in self.data["type"].unique()
        ]

    def plot_distribution_natural(self):

        reduced_order = self.__get_reduced_logic_order()
        empty_counts = (
            self.data[self.data["projection"] == "self"]
            .groupby("type")
            .size()
            .reindex(reduced_order, fill_value=0)
        )

        plt.figure(figsize=(8, 6))
        empty_counts.plot(kind="bar")

        plt.xlabel("Logic")
        plt.ylabel("Requirements")
        plt.title("Histogram of Natural Fomalizations by Logic")
        plt.xticks(rotation=0)

        out = self.__get_file_name("distnat")
        plt.savefig(out)
        plt.close()

        return out

    def plot_distribution_combined(self):

        reduced_order = self.__get_reduced_logic_order()
        projection_counts = (
            self.data.groupby(["type", "projection"])
            .size()
            .unstack(fill_value=0)
            .reindex(reduced_order, fill_value=0)
        )

        projection_colors = {
            "self": "blue",
            "yes": "green",
            "no": "red",
            "unknown": "gray",
        }

        plt.figure(figsize=(10, 6))
        projection_counts.plot(
            kind="bar",
            stacked=False,  # grouped bars
            color=[
                projection_colors.get(col, "black") for col in projection_counts.columns
            ],
        )

        plt.xlabel("Logic")
        plt.ylabel("Requirements")
        plt.title("Histogram of Natural Formalizations by Logic and Projection Status")
        plt.xticks(rotation=0)
        plt.legend(title="Projection Status")

        out = self.__get_file_name("distcomb")
        plt.savefig(out)
        plt.close()

        return out

    def plot_complexity(self):

        df_filtered = self.data[self.data["projection"] == "self"]
        agg_columns = df_filtered.filter(like=".agg.").columns.tolist()
        df_long = pd.melt(
            df_filtered,
            id_vars=["id", "type"],
            value_vars=agg_columns,
            var_name="aggregation",
            value_name="value",
        )

        # Calculate mean and median values for annotations
        stats_values = (
            df_long.groupby(["type", "aggregation"])["value"]
            .agg(["mean", "median", "count", "std"])
            .reset_index()
        )

        y_min = df_long["value"].min()
        y_max = df_long["value"].max() + 4.5

        # Create a 2x2 grid of subplots
        fig, axes = plt.subplots(
            nrows=2, ncols=2, figsize=(9, 7), sharex=True, sharey=True
        )
        axes = axes.flatten()  # Flatten the axes array for easier iteration
        plt.subplots_adjust(hspace=0.1, wspace=0.1)
        i = 1
        # Plot each aggregation in a separate subplot
        for ax, agg in zip(axes, agg_columns):
            violin = sns.violinplot(
                x="type",
                y="value",
                data=df_long[df_long["aggregation"] == agg],
                hue="type",
                palette="colorblind",
                bw_method=0.5,
                edgecolor="black",
                linewidth=1,
                linecolor="k",
                ax=ax,
                inner=None,
                legend=False,
            )
            sns.boxplot(
                x="type",
                y="value",
                hue="type",
                palette="colorblind",
                data=df_long[df_long["aggregation"] == agg],
                width=0.12,  # Adjust the box width
                showcaps=True,
                showbox=True,
                whiskerprops={"linewidth": 1.2, "color": "black"},
                medianprops={"linewidth": 1.2, "color": "black"},
                ax=ax,
                fliersize=5,
            )
            # Make violins slightly transparent
            for violin_part in violin.collections:
                violin_part.set_alpha(0.5)

            # sns.stripplot(
            #     x="type",
            #     y="value",
            #     hue="type",
            #     data=df_long[df_long["aggregation"] == agg],
            #     alpha=0.4,
            #     size=5,
            #     marker="o",
            #     edgecolor="black",
            #     linewidth=1,
            #     ax=ax,
            #     dodge=False,
            # )
            ax.set_xlabel("")
            ax.yaxis.set_minor_locator(ticker.MultipleLocator(1))

            # Annotate mean and median values on the plot above each violin
            for _, row in stats_values[stats_values["aggregation"] == agg].iterrows():
                # Position the annotations above the maximum data point with some padding
                annotation_y = y_max - 0.5

                # Prepare formatted string for annotation
                annotation_text = (
                    # f"n={row['count']}\n"
                    f"μ={row['mean']:.1f}\n"
                    f"M={row['median']:.1f}\n"
                    f"σ={row['std']:.1f}"
                )

                ax.text(
                    row["type"],
                    annotation_y,
                    annotation_text,
                    color="black",
                    ha="center",
                    va="bottom",
                    # fontfamily="monospace",
                    # size=8,
                )

            # Place the count 'n' below the x-axis tick marks
            if i > 2:
                for x_category in df_long["type"].unique():
                    # Get the specific count 'n' for this aggregation and type
                    filtered_values = stats_values.loc[
                        (stats_values["aggregation"] == agg)
                        & (stats_values["type"] == x_category),
                        "count",
                    ]

                    n_value = (
                        int(filtered_values.iloc[0]) if not filtered_values.empty else 0
                    )

                    # Find the x position of the category
                    x_position = list(df_long["type"].unique()).index(x_category)

                    # Annotate n value below the x-tick
                    ax.text(
                        x_position,
                        y_min - 8,
                        f"n={n_value}",
                        color="black",
                        ha="center",
                        va="top",
                    )

            i += 1
            ax.set_title(self.title_map.get(agg, agg))
            ax.set_ylabel("Count")
            ax.set_ylim(y_min - 5, y_max + 5)

        # Hide any unused subplots if number of agg_columns is less than 4
        for i in range(len(agg_columns), len(axes)):
            axes[i].set_visible(False)

        fig.tight_layout()

        out = self.__get_file_name("violine")
        plt.savefig(out)
        plt.close()
        return out

    def plot_pairplot(self):

        df = self.data[self.data["projection"] == "self"]
        agg_columns = df.filter(like=".agg.").columns.tolist()
        df_pairplot = df[agg_columns + ["type"]]

        unique_types = df_pairplot["type"].nunique()
        markers = ["o", "s", "D", "^", "v", "P"][:unique_types]

        g = sns.pairplot(
            df_pairplot,
            hue="type",
            palette="colorblind",
            diag_kind="kde",
            markers=markers,
        )

        for ax in g.axes.flat:
            for artist in ax.collections:
                artist.set_edgecolor("black")
                artist.set_alpha(0.6)
        g._legend.set_title("Logic")

        out = self.__get_file_name("pairplot")
        plt.savefig(out)
        plt.close()
        return out

    def plot_projection_classes(self):

        df = self.data[self.data["projection"] == "self"]

        projection_key_counts = df["projclass"].value_counts().reset_index()
        projection_key_counts.columns = ["projclass", "count"]

        plt.figure(figsize=(10, 6))
        sns.barplot(data=projection_key_counts, x="projclass", y="count")
        plt.xlabel("Projection Key")
        plt.ylabel("Count")
        plt.title("Counts per Projection Class")
        plt.tight_layout()

        out = self.__get_file_name("projclass")
        plt.savefig(out)
        plt.close()
        return out

    def plot_sankey(self):

        df = self.data

        flow_counts = {"yes": {}, "no": {}, "unknown": {}}
        for id_value, group in df.groupby("id"):
            source_type = group[group["projection"] == "self"]["type"].values[0]
            for _, row in group.iterrows():
                target_type = row["type"]
                projection_type = row["projection"]
                if projection_type in ["yes", "no", "unknown"]:
                    if (source_type, target_type) not in flow_counts[projection_type]:
                        flow_counts[projection_type][(source_type, target_type)] = set()
                    flow_counts[projection_type][(source_type, target_type)].add(
                        id_value
                    )

        labels = df["type"].unique().tolist()
        source = []
        target = []
        value = []
        link_labels = []
        link_colors = []

        projection_colors = {
            "yes": "rgba(0, 128, 0, 0.7)",
            "no": "rgba(255, 0, 0, 0.7)",
            "unknown": "rgba(128, 128, 128, 0.7)",
        }

        label_to_index = {label: idx for idx, label in enumerate(labels)}
        for projection_type, flows in flow_counts.items():
            for (src, tgt), ids_set in flows.items():
                source.append(label_to_index[src])
                target.append(label_to_index[tgt])
                value.append(len(ids_set))
                link_labels.append(f"{len(ids_set)} ids ({projection_type})")
                link_colors.append(projection_colors[projection_type])

        fig = go.Figure(
            data=[
                go.Sankey(
                    node=dict(
                        pad=15,
                        thickness=20,
                        line=dict(color="black", width=0.5),
                        label=labels,
                    ),
                    link=dict(
                        source=source,
                        target=target,
                        value=value,
                        label=link_labels,  # Add labels to links
                        color=link_colors,  # Color the links based on projection type
                    ),
                )
            ]
        )

        fig.update_layout(
            title_text="Sankey Diagram of Projections with Unique ID Counts",
            font_size=10,
        )
        out = self.__get_file_name("sankey")
        pio.write_image(fig, out, format="pdf")
        return out

    def plot_chord(self):

        outs = []
        for target in ["yes", "no", "unknown"]:

            df = self.data
            d3 = D3Blocks(chart="chord", frame=True, verbose="critical")
            links = []

            for _, group in df.groupby("id"):
                source_type_row = group[group["projection"] == "self"]
                if not source_type_row.empty:
                    source_type = source_type_row["type"].values[0]
                    yes_targets = group[
                        (group["projection"] == target) & (group["type"] != source_type)
                    ]
                    for _, row in yes_targets.iterrows():
                        target_type = row["type"]
                        links.append(
                            {"source": source_type, "target": target_type, "weight": 1}
                        )
            if len(links) > 0:
                links_df = pd.DataFrame(links)
                links_df = (
                    links_df.groupby(["source", "target"])
                    .size()
                    .reset_index(name="weight")
                )

                out = self.__get_file_name(f"chord_{target}", ".html")
                d3.chord(
                    links_df,
                    title=f"Chord Diagram (self -> {target})",
                    filepath=out,
                    save_button=True,
                    ordering=self.__get_reduced_logic_order(),
                    cmap="tab10",
                    figsize=[500, 500],
                    reset_properties=True,
                    arrowhead=30,
                    fontsize=13,
                )
                outs.append(out)
        return "\n".join(outs)
