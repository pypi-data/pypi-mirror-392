
def generate_npath_qu(event_column, dropdown_selected_events, dropdown_time_col, dropdown_partition_cols,
                      dropdown_startevents, dropdown_finalevents, slider_length, dropdown_mode,
                      db, tbl):
    time_col = dropdown_time_col


    selected_events = "'" + "', '".join(dropdown_selected_events) + "'"
    partition_columns = '"' + '", "'.join(dropdown_partition_cols) + '"'

    start_event_bool = (dropdown_startevents is not None) and ( len(dropdown_startevents) > 0)
    final_event_bool = (dropdown_finalevents is not None) and  ( len(dropdown_finalevents) > 0)

    centre_len_min = slider_length[0] - start_event_bool - final_event_bool
    centre_len_max = slider_length[1] - start_event_bool - final_event_bool
    symbols_expr = []
    list_of_symbols = []
    if start_event_bool:
        start_events = "'" + "', '".join(dropdown_startevents) + "'"
        symbols_expr.append(f"      {event_column} in ({start_events}) as A")
        list_of_symbols.append("A")
    list_of_symbols.append("O")
    if final_event_bool:
        end_events = "'" + "', '".join(dropdown_finalevents) + "'"
        symbols_expr.append(f"      {event_column} in ({end_events}) as B")
        symbols_expr.append(f"      {event_column} not in ({end_events}) as O")
        list_of_symbols.append("B")
    else:
        symbols_expr.append(f"      TRUE as O")
    symbols_expr = ",\n".join(symbols_expr)
    list_of_symbols = ", ".join(list_of_symbols)

    pattern = f"""{
    "^A." if start_event_bool else ""
    }O{{{centre_len_min},{centre_len_max}}}{
    ".B$" if final_event_bool else ""}"""
    mode = dropdown_mode

    npath_query = f"""SELECT 
cast( path as VARCHAR(1000)) as path, 
count(*) as cnt
FROM npath
(
  ON (SELECT *
       FROM "{db}"."{tbl}"
       WHERE 
       {event_column} in ({selected_events})
       )
  PARTITION BY {partition_columns}
  ORDER BY "{time_col}"
  USING
    Symbols
    (
{symbols_expr}
    )
    Pattern ('{pattern}')
    Result
    (
      ACCUMULATE (TRYCAST({event_column} AS VARCHAR(50) CHARACTER SET LATIN) of any({list_of_symbols}) ) AS path
    )
    Mode ({mode})
)
GROUP BY path
;

"""
    return npath_query
