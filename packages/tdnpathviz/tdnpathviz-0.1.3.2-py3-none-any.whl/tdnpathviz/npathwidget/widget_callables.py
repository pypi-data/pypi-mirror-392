import teradataml as tdml
import datetime
from IPython.display import display, Markdown
import time

from . import utils
from . import npath_query

import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', 200)

"""
def change_table_selection(change, widgets_dict, store):
    #when db is changed, display other table options
    db_dropdown, table_dropdown = widgets_dict["db_dropdown"], widgets_dict["table_dropdown"]
    new_db = db_dropdown.value
    new_tbls = utils.get_tbl_events(new_db)
    table_dropdown.options = new_tbls
    table_dropdown.value = None
"""

def load_table(click, widgets_dict, store):
    # display table
    # get list of columns in event selection dropdown
    # set store tbl
    table_dropdown = widgets_dict["table_dropdown"]
    input_output, center_tabs, loading_bar = widgets_dict["input_output"], widgets_dict["center_tabs"], widgets_dict[
        "loading_bar"]
    center_tabs.selected_index = 0

    input_output.clear_output()
    if (table_dropdown.value is None):
        with input_output:
            display("Select a Table")
        return

    with input_output:
        display(loading_bar)

    db, tbl = store.data["database"], table_dropdown.value
    df_sample = pd.read_sql(f"SELECT TOP 30 * FROM {db}.{tbl}", tdml.get_connection())
    store.data["df_sample"] = df_sample
    store.data["tbl"] = tbl

    input_output.clear_output()
    with input_output:
        display(f"Table: {db}.{tbl}")
        display(df_sample)

    columns = list(df_sample.columns)

    eventcol_dropdown = widgets_dict["eventcol_dropdown"]
    time_column_dropdown = widgets_dict["time_column_dropdown"]
    partitions_columns_tags = widgets_dict["partitions_columns_tags"]


    eventcol_dropdown.options = columns
    default_eventcol = None
    if "event" in columns:
        default_eventcol = "event"
    eventcol_dropdown.value = default_eventcol

    time_column_dropdown.options = columns
    time_column_dropdown.value = columns[0]
    partitions_columns_tags.allowed_tags = columns
    partitions_columns_tags.value = []


def load_events(click, widgets_dict, store):
    # display events beneath table and populate widgets
    # get event column name
    db = store.data["database"]
    tbl = widgets_dict["table_dropdown"].value
    event_col = widgets_dict["eventcol_dropdown"].value

    input_output, center_tabs, loading_bar = widgets_dict["input_output"], widgets_dict["center_tabs"], widgets_dict[
        "loading_bar"]
    center_tabs.selected_index = 0

    if event_col is None:
        with input_output:
            display("Select a Column for Events")
        return

    with input_output:
        display(loading_bar)

    all_events = pd.read_sql(f"SEL DISTINCT({event_col}) as event FROM {db}.{tbl}", tdml.get_connection()
                             ).sort_values("event").event.to_list()

    store.data["all_events"] = all_events

    input_output.clear_output()
    with input_output:
        display(f"Table: {db}.{tbl}")
        display(store.data["df_sample"])
        display(f"Events in Column {event_col}: ", str(all_events))

    store.data["event_column"] = event_col

    event_selection_tags = widgets_dict["event_selection_tags"]
    startevent_selection_tags = widgets_dict["startevent_selection_tags"]
    endevent_selection_tags = widgets_dict["endevent_selection_tags"]
    centernode_sankey_dropdown = widgets_dict["centernode_sankey_dropdown"]

    event_selection_tags.allowed_tags = all_events
    event_selection_tags.value = []
    startevent_selection_tags.allowed_tags = all_events
    startevent_selection_tags.value = []
    endevent_selection_tags.allowed_tags = all_events
    endevent_selection_tags.value = []
    centernode_sankey_dropdown.options = all_events
    centernode_sankey_dropdown.value = all_events[0]

    # open next accordion
    left_navigation = widgets_dict["left_navigation"]
    left_navigation.selected_index = 1

def select_all_events(click, widgets_dict, store):
    all_events = store.data.get("all_events", [])
    if len(all_events) == 0:
        return

    event_selection_tags = widgets_dict["event_selection_tags"]
    event_selection_tags.value = all_events


def remove_all_events(click, widgets_dict, store):
    event_selection_tags = widgets_dict["event_selection_tags"]
    event_selection_tags.value = []

def show_npath_query(click, widgets_dict, store):
    store.data["npath_query"] = None

    #db_dropdown = widgets_dict["db_dropdown"]
    table_dropdown = widgets_dict["table_dropdown"]

    time_column_dropdown = widgets_dict["time_column_dropdown"]
    partitions_columns_tags = widgets_dict["partitions_columns_tags"]

    event_selection_tags = widgets_dict["event_selection_tags"]
    startevent_selection_tags = widgets_dict["startevent_selection_tags"]
    endevent_selection_tags = widgets_dict["endevent_selection_tags"]
    numberevents_slider = widgets_dict["numberevents_slider"]
    overlapping_dropdown = widgets_dict["overlapping_dropdown"]

    query_output = widgets_dict["query_output"]
    query_output.clear_output()

    center_tabs = widgets_dict["center_tabs"]
    center_tabs.selected_index = 1

    db,tbl = store.data.get("database",None),store.data.get("tbl",None)
    if (db is None) or (tbl is None):
        with query_output:
            display("A table must be loaded first")
        return

    selected_events = event_selection_tags.value
    if len(selected_events)==0:
        with query_output:
            display("The list of selected events must not be empty.")
        return

    time_col = time_column_dropdown.value

    partitions_cols = partitions_columns_tags.value
    if len(partitions_cols)==0:
        with query_output:
            display("You need to select at least one column for partitioning.")
        return

    start_events = startevent_selection_tags.value
    end_events = endevent_selection_tags.value
    num_events_range = numberevents_slider.value #[from,to]
    npath_mode = overlapping_dropdown.value

    event_column = store.data["event_column"]

    this_npathquery = npath_query.generate_npath_qu(event_column,selected_events, time_col, partitions_cols,
                      start_events, end_events, num_events_range, npath_mode,
                      db, tbl)

    store.data["npath_query"] = this_npathquery

    with query_output:
        query_md = Markdown(f"""```sql
{this_npathquery}
```""")
        display(query_md)



def execute_npath(click, widgets_dict, store):

    show_npath_query(None, widgets_dict, store )

    this_npathquery = store.data.get("npath_query",None)
    if this_npathquery is None:
        return

    time.sleep(0.5)

    store.data["df_npath"] = None

    center_tabs = widgets_dict["center_tabs"]
    loading_bar = widgets_dict["loading_bar"]
    npath_output = widgets_dict["npath_output"]
    npath_output.clear_output()
    center_tabs.selected_index = 2
    with npath_output:
        display(loading_bar)

    try:
        df_npath_result = pd.read_sql(this_npathquery, tdml.get_connection()).sort_values("cnt", ascending=False)
        #tdml.DataFrame.from_query(this_npathquery).to_pandas().sort_values("cnt", ascending=False)
    except Exception as e:
        npath_output.clear_output()
        with npath_output:
            display("NPath calculation failed. Error Message:")
            display(e)
            return

    if len(df_npath_result)==0:
        npath_output.clear_output()
        with npath_output:
            display("NPath calculation yields empty result")
            return

    store.data["df_npath"] = df_npath_result
    npath_output.clear_output()
    with npath_output:
        display(df_npath_result.head(30))

    # open next accordion
    left_navigation = widgets_dict["left_navigation"]
    left_navigation.selected_index = 2


def switch_sankey_icicle_settings(change, widgets_dict, store):
    # switch between sankey and icicle settings visibility
    if change['name'] == 'value':
        chartsettings_stack = widgets_dict["chartsettings_stack"]
        charttype_toggle = widgets_dict["charttype_toggle"]
        chartsettings_stack.selected_index = charttype_toggle.options.index(change['new'])

def change_alginment_sankey_toggle(change, widgets_dict, store):
    #disenabled center node if it is not switched to center
    if change['name'] == 'value':
        widgets_dict["centernode_sankey_dropdown"].disabled = (change['new'] != "center")



def generate_chart(click, widgets_dict, store):
    store.data["chart"] = None
    store.data["chart_type"] = None

    center_tabs = widgets_dict["center_tabs"]
    center_tabs.selected_index = 3

    chart_output = widgets_dict["chart_output"]

    df_npath_result = store.data.get("df_npath", None)
    if (df_npath_result is None ) or len(df_npath_result)==0:
        chart_output.clear_output()
        with chart_output:
            display("No data available. Execute NPath first")
        return

    db, tbl = store.data.get("db"), store.data.get("tbl")

    charttype = widgets_dict["charttype_toggle"].value # ['Sankey', 'Icicle']
    alginment_sankey = widgets_dict["alginment_sankey_toggle"].value
    centernode_sankey = widgets_dict["centernode_sankey_dropdown"].value
    shownode = widgets_dict["shownodelabel"].value
    padding = widgets_dict["padding_slider"].value
    chartheight = widgets_dict["chartheight_slider"].value
    alginment_icicle = widgets_dict["alginment_icicle_toggle"].value
    min_node_size = widgets_dict["min_node_size_slider"].value
    displayed_depth = widgets_dict["displayed_depth_slider"].value

    this_figure = utils.get_go_figure(df_npath_result,db, tbl,charttype,
                                      alginment_sankey,centernode_sankey,shownode,padding,chartheight,
                                      alginment_icicle, min_node_size, displayed_depth)



    if this_figure is None:
        chart_output.clear_output()
        with chart_output:
            display("Generating the figure failed")
        return

    store.data["chart"] = this_figure
    store.data["chart_type"] = charttype
    chart_output.clear_output()
    with chart_output:
        display(this_figure)



def save_chart(click, widgets_dict, store):
    this_figure = store.data.get("chart",None)
    this_chart_type = store.data.get("chart_type",None)

    center_tabs = widgets_dict["center_tabs"]
    center_tabs.selected_index = 3

    chart_output = widgets_dict["chart_output"]

    if this_figure == None:
        chart_output.clear_output()
        with chart_output:
            display("Create a chart first before you can save it.")
        return

    filename = this_chart_type+"_" + datetime.datetime.now().strftime("%m-%d-%Y_%H-%M-%S") + ".html"
    this_figure.write_html(filename)
    with chart_output:
        display(f"Chart was saved here: {filename}")



