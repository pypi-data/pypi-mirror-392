import teradataml as tdml
from ipywidgets import Layout
from . import sankey_chart_plotter
from . import icicle_chart_plotter
import plotly.graph_objects as go
import pandas as pd

df_db_tbl_events = None
db_names = None

my_box_layout = Layout(
        border='1px solid lightgrey',  # Bright grey border
        padding='3px',               # Optional: Add padding inside the frame
        margin='3px',                # Optional: Add margin around the frame
        width='auto'                  # Optional: Set width
    )


def fetch_tables_views(database):
    df = pd.read_sql(f"""
            SELECT DISTINCT 
                    TRIM(TRAILING FROM TableName) TableName
            FROM dbc.tablesV 
                    WHERE DatabaseName = '{database}' 
                    AND TableKind IS IN ('V','T')
""", con=tdml.get_connection()
                ).sort_values(["TableName"])
    all_tables_views = list(df["TableName"].values)
    return all_tables_views

def get_db_events():
    global db_names
    return db_names

def get_tbl_events(db:str):
    global df_db_tbl_events
    if df_db_tbl_events is not None:
        tbl_names = list(df_db_tbl_events.loc[df_db_tbl_events.DatabaseName == db].TableName.drop_duplicates().values)
        return tbl_names
    else:
        return []




def get_go_figure(df_npath_result,db,tbl,charttype ,
                  alginment_sankey, centernode_sankey,shownode,padding,chartheight,
                  alginment_icicle,min_node_size,displayed_depth):
    df_paths = df_npath_result.copy(deep=True)
    df_paths.columns = ["path", "count_path"]

    fig = None

    if charttype =="Sankey":
        if alginment_sankey =="center":
            (l, x_pos, y_pos, colors_normal, colors_low, colors_high, s, t, v, margin_b) = \
                sankey_chart_plotter.create_params_for_sankey_centre(df_paths, centernode_sankey,
                                                                     PLOT_HEIGHT=chartheight, PADDING_WIDTH=padding)
        else:
            left_aligned = False
            if alginment_sankey=="left":
                left_aligned = True
            (l, x_pos, y_pos, colors_normal, colors_low, colors_high, s, t, v, margin_b) = \
                sankey_chart_plotter.create_params_for_sankey_lr(df_paths, left_aligned=left_aligned, PLOT_HEIGHT=chartheight,
                                                             PADDING_WIDTH=padding)

        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=0,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=l,
                x=x_pos,
                y=y_pos,
                color=colors_normal
            ),
            arrangement="fixed",
            link=dict(
                source=s,  # indices correspond to labels, eg A1, A2, A1, B1, ...
                target=t,
                value=v
            ))])

        fig.update_layout(title_text=f"Sankey Diagram for {db}.{tbl}", font_size=10)
        # node_labels, padding, height
        fig.update_layout(
            height=chartheight,
            margin_b=margin_b
        )
        if shownode == False:
            fig.update_traces(textfont=dict(color="rgba(0,0,0,0)", size=1))


    elif charttype =="Icicle":
        left_alignment = False
        if alginment_icicle == "left":
            left_alignment= True
        ids, labels, parents, values, colors = \
            icicle_chart_plotter.create_params_for_icicle(df_paths, left_alignment= left_alignment, min_node_size=min_node_size)

        fig = go.Figure(go.Icicle(
            ids=ids,
            labels=labels,
            parents=parents,
            values=values,
            branchvalues="total",
            root_color="lightgrey",
            maxdepth=displayed_depth
        ))
        fig.update_traces(marker_colors=colors)
        if not left_alignment:
            fig.update_traces(
                tiling=dict(orientation='h', flip='x'))
        fig.update_layout(title_text=f"Icicle Diagram for {db}.{tbl}", font_size=10)
        fig.update_layout(margin=dict(t=50, l=25, r=25, b=25))

    return fig


