from .widget_layout  import get_widget_store, get_npathwidget_layout
from . import widget_callables  as wc
from .utils import fetch_tables_views
from functools import partial as partial
import teradataml as tdml


def npath_widget(database = None):

    if database == None:
        database = tdml.get_context().url.username

    # set up store and dicts
    widgets_dict = get_npathwidget_layout()
    store = get_widget_store()
    store.data["database"] = database
    store.data["db"] = database
    store.data["tables"] = fetch_tables_views(database)

    widgets_dict["table_dropdown"].options = store.data["tables"]

    # assign callbacks
    def callback(func):
        return partial(func, widgets_dict=widgets_dict, store = store)
    #widgets_dict["db_dropdown"].observe(callback(wc.change_table_selection), names="value")
    widgets_dict["load_table_button"].on_click(callback(wc.load_table))
    widgets_dict["load_events_button"].on_click(callback(wc.load_events))
    widgets_dict["select_all_events_button"].on_click(callback(wc.select_all_events))
    widgets_dict["remove_all_events_button"].on_click(callback(wc.remove_all_events))
    widgets_dict["show_query_button"].on_click(callback(wc.show_npath_query))
    widgets_dict["execute_npath_button"].on_click(callback(wc.execute_npath))
    widgets_dict["charttype_toggle"].observe(callback(wc.switch_sankey_icicle_settings), names="value")
    widgets_dict["alginment_sankey_toggle"].observe(callback(wc.change_alginment_sankey_toggle), names="value")
    widgets_dict["generate_chart_button"].on_click(callback(wc.generate_chart))
    widgets_dict["save_chart_button"].on_click(callback(wc.save_chart))

    return widgets_dict["app"]
