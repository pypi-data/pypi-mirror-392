import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# DataFrameを使わずに直接データを定義
data = [
    {"ID": 1, "Name": "Alice", "Age": 25, "City": "Tokyo"},
    {"ID": 2, "Name": "Bob", "Age": 30, "City": "Osaka"},
    {"ID": 3, "Name": "Charlie", "Age": 35, "City": "Kyoto"}
]

# GridOptionsBuilderでカラム定義
gb = GridOptionsBuilder()

# 各カラムを手動で定義
gb.configure_column("ID", type=["numericColumn"], width=80)
gb.configure_column("Name", type=["textColumn"], width=120)
gb.configure_column("Age", type=["numericColumn"], width=80)
gb.configure_column("City", type=["textColumn"], width=120)

# 選択設定
gb.configure_selection(
    selection_mode="multiple",
    use_checkbox=True,
    header_checkbox=True
)

# AgGridに直接辞書のリストを渡す
grid_response = AgGrid(
    data,  # DataFrameではなく辞書のリスト
    gridOptions=gb.build(),
    update_mode=GridUpdateMode.SELECTION_CHANGED,
    height=300
)

selected_rows = grid_response['selected_rows']
st.write("選択された行:", selected_rows)