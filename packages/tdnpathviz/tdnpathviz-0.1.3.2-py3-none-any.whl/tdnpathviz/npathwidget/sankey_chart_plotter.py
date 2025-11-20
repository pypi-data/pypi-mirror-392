import pandas as pd
import seaborn as sns
import numpy as np
pd.options.mode.chained_assignment = None  # default='warn'


SATURATION_LOW = 0.1
SATURATION_NORMAL = 0.5
SATURATION_HIGH = 1.0


def create_params_for_sankey_centre(df_path_cnt, centre_node, PLOT_HEIGHT=450, PADDING_WIDTH=0.02):
    split_vals = df_path_cnt.path.str[1:-1].str.split(
        pat=", ", expand=True)

    n_nodes = split_vals.shape[1]

    # all paths must contain the centre node at least once -> otherwise dropped

    # get position of first_occurence. -1 if not existing

    def clean_alt_list(list_):
        list_ = list_.replace(', ', '","')
        list_ = list_.replace('[', '["')
        list_ = list_.replace(']', '"]')
        return list_

    def get_position_of_first_occurence(list_, centre_node):
        list_ = eval(clean_alt_list(list_))
        try:
            index_ = list_.index(centre_node)
        except ValueError:
            index_ = -1
        return index_

    def get_len_path(list_):
        list_ = eval(clean_alt_list(list_))
        return len(list_)

    df_path_cnt["i_first_oc"] = df_path_cnt.path.apply(get_position_of_first_occurence, centre_node=centre_node)

    df_path_cnt["len_path"] = df_path_cnt.path.apply(get_len_path)

    df_path_cnt = df_path_cnt.loc[df_path_cnt.i_first_oc >= 0]

    df_path_cnt["left_path_len"] = df_path_cnt.i_first_oc

    df_path_cnt["right_path_len"] = df_path_cnt.len_path - df_path_cnt.left_path_len - 1

    max_left, max_right = df_path_cnt.left_path_len.max(), df_path_cnt.right_path_len.max()

    def rev_list_fillna_front_and_back(list_, centre_node, max_left, max_right):
        list_ = eval(clean_alt_list(list_))
        index_ = list_.index(centre_node)
        no_missing_front = max_left - index_
        no_missing_back = (max_left + max_right + 1) - (len(list_) + no_missing_front)

        list_ = [None] * (no_missing_front) + list_ + [None] * (no_missing_back)
        return list_

    max_length = int(max_left + max_right + 1)

    df_path_cnt[[f"p{i}" for i in range(max_length)]] = df_path_cnt.path.apply(
        rev_list_fillna_front_and_back, centre_node=centre_node,
        max_left=max_left,
        max_right=max_right).apply(pd.Series)

    # determine path width between nodes: pairwise groupby between all steps

    all_dfs = []

    for i in range(max_length - 1):
        df_ = df_path_cnt.groupby([f"p{i}", f"p{i + 1}"])["count_path"].sum().to_frame().reset_index()

        df_.columns = ["source", "target", "value_"]

        df_["source"] = f"p{i}_" + df_["source"]

        df_["target"] = f"p{i + 1}_" + df_["target"]

        all_dfs += [df_]

    all_df = pd.concat(all_dfs)

    # prepare geometry of plot (x, y position)

    yh1 = all_df.groupby("source")["value_"].sum().to_frame()

    yh2 = all_df.groupby("target")["value_"].sum().to_frame()

    y_heights = pd.concat([yh1, yh2]).reset_index()

    y_heights.columns = ["label", "y_height_abs"]

    y_heights = y_heights.groupby("label")["y_height_abs"].max().to_frame().reset_index()
    # height is determined by max sum of incoming or outgoing path-widhts

    y_heights["x_pos_rel"] = y_heights.label.str.split("_").str[0].str[1:].astype(float) / max_length
    # x-coordinate only dependent of position in path

    y_heights["y_height_sum_per_x_pos"] = y_heights.groupby("x_pos_rel").y_height_abs.transform(np.sum)
    y_heights["label_display"] = y_heights.label.str.split("_").str[1]

    max_y_height = y_heights.y_height_sum_per_x_pos.max()
    y_heights["y_height_rel"] = y_heights.y_height_abs / max_y_height

    y_heights["y_pos_rel_top"] = y_heights.groupby(['x_pos_rel'])['y_height_rel'].cumsum(
        axis=0) - y_heights.y_height_rel
    y_heights["y_pos_rel_bottom"] = y_heights["y_pos_rel_top"] + y_heights.y_height_rel
    y_heights["y_pos_rel_center"] = (y_heights["y_pos_rel_top"] + y_heights["y_pos_rel_bottom"]) / 2

    y_heights["y_pos_ord_per_col"] = y_heights.groupby("x_pos_rel").cumcount()
    y_heights["y_pos_rel_center"] = y_heights["y_pos_rel_center"] + y_heights["y_pos_ord_per_col"] * PADDING_WIDTH

    # get label color

    labels = list(y_heights.label_display.unique())

    cols_normal = list(sns.hls_palette(len(labels),s=SATURATION_NORMAL).as_hex())
    color_map_normal = dict(zip(labels, cols_normal))
    y_heights["label_color_normal"] = y_heights.label_display.map(color_map_normal)

    cols_low = list(sns.hls_palette(len(labels),s=SATURATION_LOW).as_hex())
    color_map_low = dict(zip(labels, cols_low))
    y_heights["label_color_low"] = y_heights.label_display.map(color_map_low)

    cols_high = list(sns.hls_palette(len(labels),s=SATURATION_HIGH).as_hex())
    color_map_high = dict(zip(labels, cols_high))
    y_heights["label_color_high"] = y_heights.label_display.map(color_map_high)

    y_heights = y_heights.sort_values("label")

    # transform into params for plotly sankey

    l = list(y_heights.label.values)
    s = list(all_df.source.values)
    t = list(all_df.target.values)
    v = list(all_df.value_.values)

    # sankey expects indices

    index_mapper = dict(enumerate(l))
    index_mapper_r = {v: k for k, v in index_mapper.items()}

    s = [index_mapper_r[s_] for s_ in s]
    t = [index_mapper_r[t_] for t_ in t]

    label_dict = pd.Series(y_heights.label_display.values, index=y_heights.label).to_dict()

    l = [label_dict[l_] for l_ in l]

    x_pos = list(y_heights.x_pos_rel.values)

    y_pos = list(y_heights.y_pos_rel_center.values)

    colors_normal = list(y_heights.label_color_normal.values)
    colors_low = list(y_heights.label_color_low.values)
    colors_high = list(y_heights.label_color_high.values)

    # additional space for chart at the bottom due to increased size because of padding
    margin_b = PLOT_HEIGHT*(y_heights.y_pos_ord_per_col.max() * PADDING_WIDTH)

    return (l, x_pos, y_pos, colors_normal, colors_low, colors_high, s, t, v, margin_b)




def create_params_for_sankey_lr(df_path_cnt, left_aligned=True, PLOT_HEIGHT=450, PADDING_WIDTH=0.02):
    split_vals = df_path_cnt.path.str[1:-1].str.split(
        pat=", ", expand=True)

    n_nodes = split_vals.shape[1]

    # create pandas dataframe depending on alignment

    if left_aligned:
        df_path_cnt["p0"] = "Start"
        df_path_cnt[[f"p{i}" for i in range(1, n_nodes + 1)]] = split_vals
    else:
        def clean_alt_list(list_):
            list_ = list_.replace(', ', '","')
            list_ = list_.replace('[', '["')
            list_ = list_.replace(']', '"]')
            return list_

        def rev_list_fillna_front(list_, max_items):
            list_ = eval(clean_alt_list(list_))
            list_ = [None] * (max_items - len(list_) - 1) + ["-Start"] + list_
            return list_

        df_path_cnt[[f"p{i}" for i in range(n_nodes + 1)]] = df_path_cnt.path.apply(
            rev_list_fillna_front, max_items=n_nodes + 1).apply(pd.Series)

    # determine path width between nodes: pairwise groupby between all steps

    all_dfs = []

    for i in range(n_nodes):
        df_ = df_path_cnt.groupby([f"p{i}", f"p{i + 1}"])["count_path"].sum().to_frame().reset_index()

        df_.columns = ["source", "target", "value_"]

        df_["source"] = f"p{i}_" + df_["source"]

        df_["target"] = f"p{i + 1}_" + df_["target"]

        all_dfs += [df_]

    all_df = pd.concat(all_dfs)

    # prepare geometry of plot (x, y position)

    yh1 = all_df.groupby("source")["value_"].sum().to_frame()

    yh2 = all_df.groupby("target")["value_"].sum().to_frame()

    y_heights = pd.concat([yh1, yh2]).reset_index()

    y_heights.columns = ["label", "y_height_abs"]

    y_heights = y_heights.groupby("label")["y_height_abs"].max().to_frame().reset_index()
    # height is determined by max sum of incoming or outgoing path-widhts

    y_heights["x_pos_rel"] = y_heights.label.str.split("_").str[0].str[1:].astype(float) / n_nodes
    # x-coordinate only dependent of position in path

    y_heights["y_height_sum_per_x_pos"] = y_heights.groupby("x_pos_rel").y_height_abs.transform(np.sum)
    y_heights["label_display"] = y_heights.label.str.split("_").str[1]

    # y order of nodes based on position of first occurence
    if left_aligned:
        order_dict_y = {}
        all_vals = set()
        for i in reversed(range(0, n_nodes + 1)):
            vals_position = set(list(df_path_cnt[f"p{i}"].unique())) - {None}
            val_new_at_position = vals_position - all_vals
            all_vals = all_vals.union(set(list(df_path_cnt[f"p{i}"].unique())))
            for node in val_new_at_position:
                order_dict_y[node] = i
        y_heights["y_pos_ord"] = y_heights.label_display.map(order_dict_y)
        y_heights = y_heights.sort_values(["x_pos_rel", "y_pos_ord", "label_display"], ascending=[True, True, True])
    else:
        order_dict_y = {}
        all_vals = set()
        for i in range(0, n_nodes + 1):
            vals_position = set(list(df_path_cnt[f"p{i}"].unique())) - {None}
            val_new_at_position = vals_position - all_vals
            all_vals = all_vals.union(set(list(df_path_cnt[f"p{i}"].unique())))
            for node in val_new_at_position:
                order_dict_y[node] = i
        y_heights["y_pos_ord"] = y_heights.label_display.map(order_dict_y)
        y_heights = y_heights.sort_values(["x_pos_rel", "y_pos_ord", "label_display"], ascending=[True, True, True])

    # take highest sum height from all nodes to divde by
    max_y_height = y_heights.y_height_sum_per_x_pos.max()
    y_heights["y_height_rel"] = y_heights.y_height_abs / max_y_height

    y_heights["y_pos_rel_top"] = y_heights.groupby(['x_pos_rel'])['y_height_rel'].cumsum(
        axis=0) - y_heights.y_height_rel
    y_heights["y_pos_rel_bottom"] = y_heights["y_pos_rel_top"] + y_heights.y_height_rel
    y_heights["y_pos_rel_center"] = (y_heights["y_pos_rel_top"] + y_heights["y_pos_rel_bottom"]) / 2

    y_heights["y_pos_ord_per_col"] = y_heights.groupby("x_pos_rel").cumcount()
    y_heights["y_pos_rel_center"] = y_heights["y_pos_rel_center"] + y_heights["y_pos_ord_per_col"] * PADDING_WIDTH

    # get label color

    labels = list(y_heights.label_display.unique())

    cols_normal = list(sns.hls_palette(len(labels), s=SATURATION_NORMAL).as_hex())
    color_map_normal = dict(zip(labels, cols_normal))
    y_heights["label_color_normal"] = y_heights.label_display.map(color_map_normal)

    cols_low = list(sns.hls_palette(len(labels), s=SATURATION_LOW).as_hex())
    color_map_low = dict(zip(labels, cols_low))
    y_heights["label_color_low"] = y_heights.label_display.map(color_map_low)

    cols_high = list(sns.hls_palette(len(labels), s=SATURATION_HIGH).as_hex())
    color_map_high = dict(zip(labels, cols_high))
    y_heights["label_color_high"] = y_heights.label_display.map(color_map_high)

    y_heights = y_heights.sort_values("label")

    # transform into params for plotly sankey

    l = list(y_heights.label.values)
    s = list(all_df.source.values)
    t = list(all_df.target.values)
    v = list(all_df.value_.values)

    # sankey expects indices

    index_mapper = dict(enumerate(l))
    index_mapper_r = {v: k for k, v in index_mapper.items()}

    s = [index_mapper_r[s_] for s_ in s]
    t = [index_mapper_r[t_] for t_ in t]

    label_dict = pd.Series(y_heights.label_display.values, index=y_heights.label).to_dict()

    l = [label_dict[l_] for l_ in l]

    x_pos = list(y_heights.x_pos_rel.values)

    y_pos = list(y_heights.y_pos_rel_center.values)

    colors_normal = list(y_heights.label_color_normal.values)
    colors_low = list(y_heights.label_color_low.values)
    colors_high = list(y_heights.label_color_high.values)


    # additional space for chart at the bottom due to increased size because of padding
    margin_b = PLOT_HEIGHT*(y_heights.y_pos_ord_per_col.max() * PADDING_WIDTH)

    return (l, x_pos, y_pos, colors_normal, colors_low, colors_high, s, t, v, margin_b)

