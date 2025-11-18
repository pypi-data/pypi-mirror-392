import streamlit as st
import pandas as pd

# サンプルのデータ
df = pd.DataFrame({
    "名前": ["太郎", "花子", "一郎"],
    "年齢": [25, 30, 22],
    "職業": ["エンジニア", "デザイナー", "学生"]
})

# チェックボックス列を追加（Streamlitでの選択用）
df["選択"] = False

# 編集可能なテーブルを表示（checkboxを選ばせる）
edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

# 選択された行だけを抽出
selected_rows = edited_df[edited_df["選択"] == True]

st.write("✅ 選択された行:")
st.write(selected_rows)
