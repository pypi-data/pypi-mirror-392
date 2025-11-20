import pandas as pd
import seaborn as sns
pd.options.mode.chained_assignment = None  # default='warn'


def _clean_alt_list(list_):
    list_ = list_.replace(', ', '","')
    list_ = list_.replace('[', '["')
    list_ = list_.replace(']', '"]')
    return list_


def _rev_list(list_):
    list_ = eval(_clean_alt_list(list_))
    list_.reverse()
    return str(list_).replace("'", "")


def _change_list_to_str(list_, labels_dict_inv, joiner="___"):
    list_ = eval(_clean_alt_list(list_))
    list_ = [str(labels_dict_inv[x]) for x in list_]
    return "" + joiner + joiner.join(list_)


def _get_tree_vals(node_id, count_path, joiner="___"):
    list_node_id = node_id.split(joiner)
    result = []
    # print(list_node_id)

    for i in range(1, len(list_node_id)):
        result += [[
            joiner.join(list_node_id[:i]),
            joiner.join(list_node_id[:i + 1]),
            count_path]]
    df_ = pd.DataFrame(data=result, columns=["parent_node_id", "node_id", "edge_val"])
    return df_


def create_params_for_icicle(df_path_cnt, left_alignment=True, min_node_size=5):
    joiner = "___"

    # get list of unique events and respective mapper dictionaries for performance
    split_vals = df_path_cnt.path.str[1:-1].str.split(
        pat=", ", expand=True)
    all_events = set()
    for col in split_vals:
        all_events = all_events.union(set(list(split_vals[col].unique())))
    labels_dict = {str(i): l for i, l in enumerate(all_events)}
    labels_dict_inv = {v: k for k, v in labels_dict.items()}

    # concatenate all paths to single string with a separator
    if left_alignment is False:
        df_path_cnt["path_rev"] = df_path_cnt.path.apply(_rev_list)
        df_path_cnt["node_id"] = df_path_cnt.path_rev.apply(_change_list_to_str, args=(labels_dict_inv, joiner))
    else:
        df_path_cnt["node_id"] = df_path_cnt.path.apply(_change_list_to_str, args=(labels_dict_inv, joiner))
    all_dfs = []
    for i, row in df_path_cnt.iterrows():
        all_dfs += [_get_tree_vals(row.node_id, row.count_path)]
    final_df = pd.concat(all_dfs).groupby(["parent_node_id", "node_id"])["edge_val"].sum().to_frame().reset_index()
    final_df["node_label"] = final_df.node_id.str.rsplit(joiner, n=1).str.get(1).fillna("").map(labels_dict)
    final_df = final_df.loc[final_df["edge_val"] >= min_node_size]

    # define colors
    unique_labels = list(final_df.node_label.unique())
    unique_labels.sort()
    cols = list(sns.hls_palette(len(unique_labels)).as_hex())
    color_map = dict(zip(unique_labels, cols))
    final_df["color"] = final_df.node_label.map(color_map)

    ids = final_df.node_id
    labels = final_df.node_label
    parents = final_df.parent_node_id
    values = final_df.edge_val
    colors = final_df.color

    return ids, labels, parents, values, colors
