import streamlit as st


def show_student_table(df):

    st.subheader("📋 Student Records")

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )
    