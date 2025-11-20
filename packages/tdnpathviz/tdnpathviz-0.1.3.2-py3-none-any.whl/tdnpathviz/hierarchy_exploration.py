import ipywidgets as widgets
from IPython.display import display
from functools import reduce
import plotly.express as px
import plotly.io as pio


class ProductHierarchySelector:
    def __init__(self, dataset, product_hierarchy, max_depth=3, figure_height=800, figure_width=600):
        """
        Initialize the ProductHierarchySelector.

        Args:
            dataset (DataFrame): The dataset containing the product hierarchy.
            product_hierarchy (list): A list of column names representing the product hierarchy.
            max_depth (int): The maximum depth of the hierarchy to display.
            figure_height (int, optional): The height of the figure in pixels. Defaults to 800.
            figure_width (int, optional): The width of the figure in pixels. Defaults to 600.
        """
        self.dataset = dataset
        self.unfiltered_dataset = dataset
        self.product_hierarchy = product_hierarchy
        self.max_depth = max_depth
        self.figure_height = figure_height
        self.figure_width = figure_width

        # Output widget to display which tile was clicked
        self.output = widgets.Output()

        # Generate the initial hierarchical levels
        hierarchical_levels = self.create_hierarchy(self.dataset, self.product_hierarchy[0:max_depth])

        # Create initial tiles based on the hierarchical levels
        self.columns = self.create_tiles(hierarchical_levels, 0, self.figure_height, self.figure_width)

        # Create the initial grid layout
        self.grid_layout = widgets.HBox(self.columns)

        # Display the initial hierarchical tiles and the output widget
        display(self.grid_layout)
        display(self.output)

    def create_hierarchy(self, df, product_hierarchy):
        """
        Create hierarchical levels based on the product hierarchy.

        Args:
            df (DataFrame): The dataset containing the product hierarchy.
            product_hierarchy (list): A list of column names representing the product hierarchy.

        Returns:
            dict: A dictionary representing the hierarchical levels with conditions and weights.
        """
        df_hier_loc = df.groupby(product_hierarchy).count()
        additional_column = [c for c in df_hier_loc.columns if c not in product_hierarchy][0]
        df_hier_loc = df_hier_loc[product_hierarchy + [additional_column]].to_pandas()
        df_hier_loc['N'] = df_hier_loc[additional_column] / sum(df_hier_loc[additional_column])

        levels = {i: {} for i in range(len(product_hierarchy))}

        for i, p in enumerate(product_hierarchy):
            res = df_hier_loc[product_hierarchy[0:(i + 1)] + ['N']].groupby(product_hierarchy[0:(i + 1)]).sum()
            res = res.sort_values(product_hierarchy[0:(i + 1)]).reset_index()
            for j, row in res.iterrows():
                filter_condition = [df[p] == row[p] for p in product_hierarchy[0:(i + 1)]]
                filter_condition_str = ' > '.join([str(row[p]) for p in product_hierarchy[0:(i + 1)]])
                levels[i][row[product_hierarchy[i]]] = {
                    'weight': float(row['N']),
                    'condition': reduce(lambda x, y: x & y, filter_condition),
                    'condition_str': filter_condition_str
                }
        return levels

    def create_tiles(self, levels, base_level, figure_height, figure_width, tile_margin=1):
        """
        Create tiles for the hierarchical levels.

        Args:
            levels (dict): The hierarchical levels with conditions and weights.
            base_level (int): The base level of the hierarchy.
            figure_height (int): The height of the figure in pixels.
            tile_margin (int): The margin between the tiles in pixels.

        Returns:
            list: A list of VBox columns containing the tiles.
        """
        columns = []
        max_depth = max(list(levels.keys())) + 1
        button_width = figure_width // max_depth
        for depth in range(max_depth):
            column = []
            total_items = sum([item['weight'] for item in levels[depth].values()])
            for value, content in levels[depth].items():
                height = (figure_height) * float(content['weight']) / total_items - 2*0  # Normalize the height
                font_size = 20
                if height < 1.1 * font_size:
                    font_size = int(height * 0.5)  # Adjust font size based on height
                button = widgets.Button(
                    description=value,
                    layout=widgets.Layout(
                        height=f'{height}px',
                        width=f'{button_width}px',
                        margin=f'{tile_margin*0}px 0px 0px',
                        border='1px solid black',
                        display='flex',
                        align_items='center',
                        justify_content='center',
                        padding='0px',
                        overflow='hidden'
                    ),
                    style={'font_size': f'{font_size}px'}
                )
                button.level = base_level + depth  # Adjust the level relative to the base level
                button.value = value  # Store the value in the button
                button.condition_str = content['condition_str']
                button.condition = content['condition']
                button.on_click(self.on_tile_click)
                column.append(button)
            columns.append(widgets.VBox(column))
        return columns

    def on_tile_click(self, tile):
        """
        Handle button clicks and update the dataset and hierarchy.

        Args:
            tile (Button): The clicked button widget.
        """
        with self.output:
            self.output.clear_output()
            print(f"Clicked: {tile.description}, Level: {tile.level}, Value: {tile.condition_str}")

            # Update the dataset
            self.dataset = self.dataset[tile.condition]

            # Determine the new hierarchy range
            start_level = tile.level
            end_level = min(tile.level + self.max_depth, len(self.product_hierarchy))
            new_hierarchy = self.product_hierarchy[start_level:end_level]

            if not new_hierarchy:
                print("No further hierarchy levels to display.")
                return

            # Recreate the hierarchy
            hierarchical_levels = self.create_hierarchy(self.dataset, new_hierarchy)

            # Create new tiles based on the updated hierarchy
            self.columns = self.create_tiles(hierarchical_levels, start_level, self.figure_height, self.figure_width)

            # Update the display
            self.grid_layout.children = self.columns

    def get_filtered_dataset(self):
        """
        Get the filtered dataset after user selection.

        Returns:
            DataFrame: The filtered dataset.
        """
        return self.dataset

    def visualize_only(self, filename=None):
        """
        Visualize the product hierarchy using an icicle chart.

        Args:
            filename (str, optional): The filename to save the HTML visualization. Defaults to None.
        """
        df_hierarchy = self.unfiltered_dataset[self.product_hierarchy].dropna().drop_duplicate().to_pandas()

        # Create the icicle chart
        fig = px.icicle(df_hierarchy, path=self.product_hierarchy, maxdepth=self.max_depth)
        fig.update_layout(height=self.figure_height)  # Set the height to the specified pixels

        # Display the chart
        fig.show()

        if filename is not None:
            if not filename.lower().endswith('.html'):
                filename += '.html'
            pio.write_html(fig, filename)