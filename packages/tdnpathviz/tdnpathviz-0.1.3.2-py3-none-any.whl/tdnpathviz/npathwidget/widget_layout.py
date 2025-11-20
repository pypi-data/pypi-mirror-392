import os
from ipywidgets import (
    AppLayout, Checkbox, Button, Accordion, IntRangeSlider, IntSlider,
    Tab, HTML, Output, Label, TagsInput, Dropdown, HBox, VBox, FloatSlider,
    Image, ToggleButtons, Stack
)

from .utils import my_box_layout, get_db_events

# state
class SharedStore:
    def __init__(self):
        self.data = {}


def get_npathwidget_layout():
    # Widget Initialization
    # Low-level widgets
    loading_bar = Image(value=open(os.path.join(os.path.dirname(__file__), 'loadinbar.gif'), 'rb').read())
    #db_dropdown = Dropdown(options=get_db_events(),value=None)
    table_dropdown = Dropdown(options=[])
    load_table_button = Button(description='Load Table', button_style='primary')
    eventcol_dropdown = Dropdown(options=[])
    load_events_button = Button(description='Load Events', button_style='primary')
    time_column_dropdown = Dropdown(options=[])
    partitions_columns_tags = TagsInput(allowed_tags=[], allow_duplicates=False)
    select_all_events_button = Button(description='Select All', button_style='info')
    remove_all_events_button = Button(description='Remove All', button_style='warning')
    event_selection_tags = TagsInput(allowed_tags=[], allow_duplicates=False)
    startevent_selection_tags = TagsInput(allowed_tags=[], allow_duplicates=False)
    endevent_selection_tags = TagsInput(allowed_tags=[], allow_duplicates=False)
    numberevents_slider = IntRangeSlider(value=[2, 5], min=2, max=10, step=1, orientation='horizontal', readout=True, readout_format='d')
    overlapping_dropdown = Dropdown(options=['NONOVERLAPPING', 'OVERLAPPING'], value='NONOVERLAPPING')
    show_query_button = Button(description='Show NPath Query', button_style='primary')
    execute_npath_button = Button(description='Execute NPath', button_style='primary')
    charttype_toggle = ToggleButtons(options=['Sankey', 'Icicle'])
    alginment_sankey_toggle = ToggleButtons(options=['left', 'center', 'right'])
    centernode_sankey_dropdown = Dropdown(options=[], description="Center Node", disabled=True)
    shownodelabel = Checkbox(value=True, description='Show Node Labels', indent=False)
    padding_slider = FloatSlider(value=0.02, min=0, max=0.05, step=0.01, description='Padding')
    chartheight_slider = IntSlider(value=450, min=250, max=1050, step=50, description='Chart Height')
    alginment_icicle_toggle = ToggleButtons(options=['left', 'right'])
    min_node_size_slider = IntSlider(value=1, min=1, max=100, step=1)
    displayed_depth_slider = IntSlider(value=3, min=1, max=7, step=1)
    generate_chart_button = Button(description="Generate Chart", button_style='primary')
    save_chart_button = Button(description="Save Chart", button_style='primary')

    # Output widgets
    input_output = Output()
    query_output = Output()
    npath_output = Output()
    chart_output = Output()
    load_table_wait = Output()
    load_npath_wait = Output()

    # complex widgets

    data_source_box = VBox([
        #Label("Database"),
        #db_dropdown,
        Label("Table"),
        table_dropdown,
        HTML("<hr>"),
        load_table_button,
        HTML("<br>"),
        Label("Event Column"),
        eventcol_dropdown,
        HTML("<hr>"),
        load_events_button,
        load_table_wait
    ])

    npath_settings_box = VBox([
        VBox([
            Label("Time/Order Column(s)"),
            time_column_dropdown,
            Label("Partition Column(s)"),
            partitions_columns_tags
        ], layout=my_box_layout),
        HTML('<hr style="height:0pt; visibility:hidden;" />'),
        VBox([
            Label("Event Selection"),
            HBox([select_all_events_button, remove_all_events_button]),
            event_selection_tags,
            Label("Define Start Events"),
            startevent_selection_tags,
            Label("Define End Events"),
            endevent_selection_tags
        ], layout=my_box_layout),
        HTML('<hr style="height:0pt; visibility:hidden;" />'),
        VBox([
            Label("Path Length"),
            numberevents_slider,
            Label("NPath Mode"),
            overlapping_dropdown
        ], layout=my_box_layout),
        HTML("<hr>"),
        HBox([show_query_button, execute_npath_button])
    ])

    settingssankey = VBox([
        Label("Sankey Alignment"),
        alginment_sankey_toggle,
        centernode_sankey_dropdown,
        Label("Advanced Options"),
        shownodelabel,
        padding_slider,
        chartheight_slider
    ])

    settingsicicle = VBox([
        Label("Icicle Alignment"),
        alginment_icicle_toggle,
        Label("Minimum Node Size"),
        min_node_size_slider,
        Label("Displayed Depth"),
        displayed_depth_slider
    ])

    chartsettings_stack = Stack([
        settingssankey,
        settingsicicle
    ], selected_index=0, layout=my_box_layout)

    create_chart_box = VBox([
        Label("Chart Type"),
        charttype_toggle,
        HTML('<hr style="height:0pt; visibility:hidden;" />'),
        chartsettings_stack,
        HTML("<hr>"),
        HBox([generate_chart_button, save_chart_button])
    ])


    left_navigation = Accordion(
        children=[data_source_box, npath_settings_box, create_chart_box],
        titles=['1) Data Source', '2) NPath Settings', '3) Create Chart'],
        selected_index = 0
    )

    center_tabs = Tab(children=[input_output, query_output, npath_output, chart_output],
                      titles = ["Input", "Query", "Result","Chart"])


    # App Layout
    app = AppLayout(
        left_sidebar=left_navigation,
        center=center_tabs,
        right_sidebar=None,
        footer=None
    )



    # widgets_dict to hand over everything to the functions
    # Dictionary of widgets
    widgets_dict = {
        "loading_bar": loading_bar,
        #"db_dropdown": db_dropdown,
        "table_dropdown": table_dropdown,
        "load_table_button": load_table_button,
        "eventcol_dropdown":eventcol_dropdown,
        "load_events_button":load_events_button,
        "time_column_dropdown": time_column_dropdown,
        "partitions_columns_tags": partitions_columns_tags,
        "select_all_events_button": select_all_events_button,
        "remove_all_events_button": remove_all_events_button,
        "event_selection_tags": event_selection_tags,
        "startevent_selection_tags": startevent_selection_tags,
        "endevent_selection_tags": endevent_selection_tags,
        "numberevents_slider": numberevents_slider,
        "overlapping_dropdown": overlapping_dropdown,
        "show_query_button": show_query_button,
        "execute_npath_button": execute_npath_button,
        "charttype_toggle": charttype_toggle,
        "alginment_sankey_toggle": alginment_sankey_toggle,
        "centernode_sankey_dropdown": centernode_sankey_dropdown,
        "shownodelabel": shownodelabel,
        "padding_slider": padding_slider,
        "chartheight_slider": chartheight_slider,
        "alginment_icicle_toggle":alginment_icicle_toggle,
        "min_node_size_slider": min_node_size_slider,
        "displayed_depth_slider": displayed_depth_slider,
        "generate_chart_button": generate_chart_button,
        "save_chart_button": save_chart_button,
        "input_output": input_output,
        "query_output": query_output,
        "npath_output": npath_output,
        "chart_output": chart_output,
        "load_table_wait": load_table_wait,
        "load_npath_wait": load_npath_wait,
        "data_source_box": data_source_box,
        "npath_settings_box": npath_settings_box,
        "settingssankey": settingssankey,
        "settingsicicle": settingsicicle,
        "chartsettings_stack": chartsettings_stack,
        "create_chart_box": create_chart_box,
        "left_navigation": left_navigation,
        "center_tabs": center_tabs,
        "app": app
    }

    return widgets_dict

def get_widget_store():
    store = SharedStore()
    return store







