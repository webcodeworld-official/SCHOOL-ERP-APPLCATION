import streamlit as st
import pandas as pd
import io
import os
from datetime import datetime
from database.connection import get_connection, DATABASE
from utils import load_custom_css
from database.branch_queries import get_all_branches, add_branch

if not st.session_state.get("authenticated"):
    st.error("Please log in first.")
    st.stop()

# --------------------------------------------------
# THEME PRESETS (for our custom CSS classes only)
# --------------------------------------------------

THEMES = {
    "Dark Charcoal + Teal (current)": {
        "panel": "#27272A", "hairline": "#3F3F46", "accent": "#14B8A6",
        "text_hi": "#FAFAFA", "text_lo": "#A1A1AA", "bg_note": "#18181B",
    },
    "Dark Navy + Gold": {
        "panel": "#131B2E", "hairline": "#29365A", "accent": "#C9A227",
        "text_hi": "#F2F4F8", "text_lo": "#92A0BD", "bg_note": "#0B1220",
    },
    "Light Clean + Teal": {
        "panel": "#FFFFFF", "hairline": "#E2E8F0", "accent": "#0D9488",
        "text_hi": "#071C4E", "text_lo": "#64748B", "bg_note": "#F8FAFC",
    },
}

if "selected_theme" not in st.session_state:
    st.session_state["selected_theme"] = "Dark Charcoal + Teal (current)"


def apply_theme_override(theme_name):
    t = THEMES[theme_name]
    st.markdown(f"""
    <style>
    :root {{
        --panel: {t['panel']} !important;
        --hairline: {t['hairline']} !important;
        --teal: {t['accent']} !important;
        --text-hi: {t['text_hi']} !important;
        --text-lo: {t['text_lo']} !important;
    }}
    </style>
    """, unsafe_allow_html=True)


load_custom_css()
apply_theme_override(st.session_state["selected_theme"])

st.markdown("""
<div class="erp-hero">
    <div class="erp-eyebrow">System</div>
    <div class="erp-title">Settings</div>
    <div class="erp-subtitle">Database health, backups, and app appearance.</div>
</div>
""", unsafe_allow_html=True)

TABLES = ["student", "staff", "visitors", "transportation", "admission",
          "library", "attendence", "fees", "examination"]

# --------------------------------------------------
# DATABASE STATS
# --------------------------------------------------

st.markdown('<div class="section-label">Database Stats</div>', unsafe_allow_html=True)

conn = get_connection()
counts = {}
for table in TABLES:
    result = pd.read_sql(f"SELECT COUNT(*) as cnt FROM {table}", conn)
    counts[table] = int(result["cnt"].iloc[0])
conn.close()

last_modified = datetime.fromtimestamp(os.path.getmtime(DATABASE))
st.caption(f"Database last updated: **{last_modified.strftime('%d %B %Y, %I:%M %p')}**")

cols = st.columns(3)
table_labels = {
    "student": "🎓 Students", "staff": "👩‍🏫 Staff", "visitors": "🚶 Visitors",
    "transportation": "🚌 Transport", "admission": "📥 Admissions", "library": "📚 Library",
    "attendence": "📅 Attendance", "fees": "💰 Fees", "examination": "📝 Exam Results",
}

for i, (table, label) in enumerate(table_labels.items()):
    with cols[i % 3]:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{counts[table]:,}</div>
            <div class="kpi-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)
    if i % 3 == 2:
        st.write("")

# --------------------------------------------------
# DATA BACKUP / EXPORT
# --------------------------------------------------

st.markdown('<div class="section-label">Backup & Export</div>', unsafe_allow_html=True)

st.markdown("""
<div class="feature-card">
    <div class="icon">💾</div>
    <h4>Download Full Database</h4>
    <p>Exports every table. The Attendance table is large (140,000+ rows), so this
    may take up to a minute — a progress message will show while it works.</p>
</div>
""", unsafe_allow_html=True)

st.write("")

backup_col1, backup_col2 = st.columns(2)

with backup_col1:
    if st.button("📦 Prepare Excel Backup (slower, formatted)", use_container_width=True):
        with st.spinner("Building backup — this can take up to a minute for large tables..."):
            conn = get_connection()
            buffer = io.BytesIO()

            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                for table in TABLES:
                    df = pd.read_sql(f"SELECT * FROM {table}", conn)
                    df.to_excel(writer, sheet_name=table[:31], index=False)

            conn.close()
            buffer.seek(0)
            st.session_state["backup_ready_xlsx"] = buffer.getvalue()

        st.success("Excel backup ready.")

with backup_col2:
    if st.button("⚡ Prepare CSV Backup (faster, .zip)", use_container_width=True):
        with st.spinner("Building backup..."):
            import zipfile

            conn = get_connection()
            zip_buffer = io.BytesIO()

            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                for table in TABLES:
                    df = pd.read_sql(f"SELECT * FROM {table}", conn)
                    csv_bytes = df.to_csv(index=False).encode("utf-8")
                    zf.writestr(f"{table}.csv", csv_bytes)

            conn.close()
            zip_buffer.seek(0)
            st.session_state["backup_ready_zip"] = zip_buffer.getvalue()

        st.success("CSV backup ready.")

if "backup_ready_xlsx" in st.session_state:
    st.download_button(
        label="⬇️ Download Excel Backup (.xlsx)",
        data=st.session_state["backup_ready_xlsx"],
        file_name=f"school_backup_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

if "backup_ready_zip" in st.session_state:
    st.download_button(
        label="⬇️ Download CSV Backup (.zip)",
        data=st.session_state["backup_ready_zip"],
        file_name=f"school_backup_{datetime.now().strftime('%Y%m%d_%H%M')}.zip",
        mime="application/zip"
    )

# --------------------------------------------------
# APP APPEARANCE — working theme switcher
# --------------------------------------------------

st.markdown('<div class="section-label">App Appearance</div>', unsafe_allow_html=True)

selected = st.selectbox(
    "Choose a theme",
    list(THEMES.keys()),
    index=list(THEMES.keys()).index(st.session_state["selected_theme"])
)

if selected != st.session_state["selected_theme"]:
    st.session_state["selected_theme"] = selected
    st.rerun()

t = THEMES[st.session_state["selected_theme"]]
st.markdown(f"""
<div class="feature-card">
    <p style="margin-bottom: 0.8rem;">Preview: <strong>{st.session_state['selected_theme']}</strong></p>
    <div style="display:flex; gap:0.6rem; margin-bottom:0.8rem;">
        <div style="width:40px; height:40px; border-radius:8px; background:{t['bg_note']}; border:1px solid {t['hairline']};"></div>
        <div style="width:40px; height:40px; border-radius:8px; background:{t['panel']}; border:1px solid {t['hairline']};"></div>
        <div style="width:40px; height:40px; border-radius:8px; background:{t['accent']};"></div>
    </div>
    <p style="font-size:0.85rem;">This changes cards, hero sections, and KPI tiles across the app immediately.</p>
</div>
""", unsafe_allow_html=True)

st.caption(
    "⚠️ Native Streamlit elements (buttons, sliders, page background) follow "
    "`.streamlit/config.toml` and require restarting the app to change — "
    "that part can't be switched live. The custom cards above update instantly."
)

# --------------------------------------------------
# USER MANAGEMENT (Admin only — page itself is already Admin-gated)
# --------------------------------------------------

from database.users_queries import get_all_users, username_exists, create_user, delete_user, count_admins

st.markdown('<div class="section-label">User Management</div>', unsafe_allow_html=True)

users_df = get_all_users()

st.dataframe(users_df, use_container_width=True, hide_index=True)

with st.expander("➕ Create New User"):
    new_username = st.text_input("Username", key="new_user_username")
    new_full_name = st.text_input("Full Name", key="new_user_fullname")
    new_password = st.text_input("Password", type="password", key="new_user_password")
    new_role = st.selectbox("Role", ["Admin", "Teacher", "Accountant"], key="new_user_role")

    if st.button("Create User", use_container_width=True):
        if not new_username or not new_password or not new_full_name:
            st.error("All fields are required.")
        elif username_exists(new_username):
            st.error("This username already exists.")
        elif len(new_password) < 6:
            st.error("Password must be at least 6 characters.")
        else:
            create_user(new_username, new_password, new_role, new_full_name)
            st.success(f"User '{new_username}' created successfully.")
            st.rerun()

with st.expander("🗑 Remove a User"):
    if not users_df.empty:
        username_to_remove = st.selectbox(
            "Select user to remove",
            users_df["Username"].tolist(),
            key="remove_user_select"
        )

        if st.button("Remove User", use_container_width=True):
            target_role = users_df[users_df["Username"] == username_to_remove]["Role"].iloc[0]

            if target_role == "Admin" and count_admins() <= 1:
                st.error("Cannot remove the last remaining Admin account.")
            elif username_to_remove == st.session_state.get("username"):
                st.error("You cannot remove your own account while logged in.")
            else:
                delete_user(username_to_remove)
                st.success(f"User '{username_to_remove}' removed.")
                st.rerun()

st.markdown('<div class="section-label">Branch Management</div>', unsafe_allow_html=True)

branches_df = get_all_branches()

st.dataframe(branches_df, use_container_width=True, hide_index=True)

with st.expander("➕ Add New Branch"):
    branch_name = st.text_input("Branch Name", key="new_branch_name")
    branch_address = st.text_input("Address", key="new_branch_address")
    branch_city = st.text_input("City", key="new_branch_city")
    branch_phone = st.text_input("Phone", key="new_branch_phone")
    branch_principal = st.text_input("Principal Name", key="new_branch_principal")

    if st.button("Create Branch", use_container_width=True, key="create_branch_btn"):
        if not branch_name:
            st.error("Branch Name is required.")
        elif branch_name in branches_df["Branch_Name"].values:
            st.error("A branch with this name already exists.")
        else:
            new_id = add_branch(branch_name, branch_address, branch_city, branch_phone, branch_principal)
            st.success(f"Branch '{branch_name}' created (Branch_ID: {new_id}).")
            st.rerun()