import streamlit as st
import base64
import os


def _photo_to_data_uri(path):
    """Converts a local image file into a base64 data URI Streamlit can always render,
    regardless of static file serving config or Streamlit version."""
    if not path or not os.path.exists(path):
        return None

    ext = path.split(".")[-1].lower()
    mime = "image/png" if ext == "png" else "image/jpeg"

    with open(path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    return f"data:{mime};base64,{encoded}"


def show_student_table(students):

    if students.empty:
        st.warning("No student records found.")
        return []

    display_df = students.copy()

    # Convert file paths into inline, always-renderable image data
    if "Photo_Path" in display_df.columns:
        display_df["Photo_Path"] = display_df["Photo_Path"].apply(_photo_to_data_uri)

    # Put Photo_Path first, then everything else in original order (minus the hidden doc path)
    other_cols = [c for c in display_df.columns if c not in ("Photo_Path", "Aadhar_Doc_Path")]
    display_cols = ["Photo_Path"] + other_cols
    
    selected = st.dataframe(
        display_df[display_cols],
        use_container_width=True,
        hide_index=True,
        selection_mode="single-row",
        on_select="rerun",
        column_config={
            "Photo_Path": st.column_config.ImageColumn("Photo", width="small"),
        },
    )

    if selected.selection.rows:
        row_index = selected.selection.rows[0]
        return students.iloc[row_index]  # return the ORIGINAL row, not the data-URI version

    return []
