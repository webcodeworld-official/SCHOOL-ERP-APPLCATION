from st_aggrid import (
    AgGrid,
    GridOptionsBuilder,
    GridUpdateMode
)


def show_student_grid(df):
    """
    Displays the student data in an AG Grid and
    returns the selected row(s).
    """

    gb = GridOptionsBuilder.from_dataframe(df)

    gb.configure_default_column(
        sortable=True,
        filter=True,
        resizable=True,
    )

    gb.configure_selection(
        selection_mode="single",
        use_checkbox=True
    )

    gb.configure_pagination(
        paginationAutoPageSize=False,
        paginationPageSize=15
    )

    grid = AgGrid(
        df,
        gridOptions=gb.build(),
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        fit_columns_on_grid_load=True,
        height=500,
        theme="streamlit"
    )

    return grid["selected_rows"]