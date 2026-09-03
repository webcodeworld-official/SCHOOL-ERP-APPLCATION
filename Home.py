import streamlit as st
from database.users_queries import ensure_users_table, seed_demo_users, authenticate
from database.branch_queries import get_all_branches, get_branch_name

st.set_page_config(
    page_title="School ERP System",
    page_icon="🏫",
    layout="wide"
)

ensure_users_table()
seed_demo_users()

MANAGEMENT_ACCESS = {
    "Admin": "all",
    "Teacher": ["Examination Management", "Academic Structure", "Leave Management"],
    "Accountant": ["Fee Management", "Fee Structure Management", "Leave Management"],
    }

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False


def login_page():
    st.markdown("""
    <div style="max-width:420px; margin: 4rem auto; text-align:center;">
        <h1>🏫 School ERP System</h1>
        <p style="color:#A1A1AA;">Sign in to continue</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Log In", use_container_width=True):
            result = authenticate(username, password)
            if result:
                role, full_name, branch_id = result
                st.session_state["authenticated"] = True
                st.session_state["username"] = username
                st.session_state["role"] = role
                st.session_state["full_name"] = full_name
                st.session_state["user_branch_id"] = branch_id
                st.session_state["active_branch_id"] = branch_id
                st.rerun()
            else:
                st.error("Invalid username or password.")

        with st.expander("Demo accounts"):
            st.caption("admin / admin123 — full access, all branches")
            st.caption("teacher / teacher123 — Examination + all Analytics")
            st.caption("accountant / accountant123 — Fees + all Analytics")


# --------------------------------------------------
# NOT LOGGED IN: use st.navigation with a hidden single page,
# so Streamlit's automatic pages/ sidebar never shows.
# --------------------------------------------------

if not st.session_state["authenticated"]:
    login_nav = st.navigation([st.Page(login_page, title="Login")], position="hidden")
    login_nav.run()
    st.stop()

# --------------------------------------------------
# LOGGED IN — everything below is unchanged from before
# --------------------------------------------------

role = st.session_state["role"]

if role == "Admin":
    branches = get_all_branches()
    branch_options = ["All Branches"] + branches["Branch_Name"].tolist()
    branch_id_lookup = {"All Branches": None}
    branch_id_lookup.update(dict(zip(branches["Branch_Name"], branches["Branch_ID"])))

    current_name = get_branch_name(st.session_state.get("active_branch_id"))
    default_index = branch_options.index(current_name) if current_name in branch_options else 0

    with st.sidebar:
        st.markdown("**🏢 Branch View**")
        selected_branch_name = st.selectbox(
            "Viewing", branch_options, index=default_index,
            key="branch_switcher", label_visibility="collapsed"
        )
        new_active_branch = branch_id_lookup[selected_branch_name]
        if new_active_branch != st.session_state.get("active_branch_id"):
            st.session_state["active_branch_id"] = new_active_branch
            st.rerun()
        st.divider()

dashboard = st.Page("pages/00_Dashboard.py", title="Home", icon="🏠", default=True)

analytics_hub = st.Page("pages/analytics_hub.py", title="Analytics Hub", icon="📊")
management_hub = st.Page("pages/management_hub.py", title="ERP Management Hub", icon="⚙️")

analytics_pages = [
    analytics_hub,
    st.Page("pages/01_Students_Analytics.py", title="Students Analytics", icon="🎓"),
    st.Page("pages/02_Staff_Analytics.py", title="Staff Analytics", icon="👩‍🏫"),
    st.Page("pages/03_Visitors_Analytics.py", title="Visitors Analytics", icon="🚶"),
    st.Page("pages/04_Transportation_Analytics.py", title="Transportation Analytics", icon="🚌"),
    st.Page("pages/05_Admission_Analytics.py", title="Admission Analytics", icon="📥"),
    st.Page("pages/06_Examination_Analytics.py", title="Examination Analytics", icon="📝"),
    st.Page("pages/07_Fees_Analytics.py", title="Fees Analytics", icon="💰"),
    st.Page("pages/08_Library_Analytics.py", title="Library Analytics", icon="📚"),
]

all_management_pages = {
    "Student Management": st.Page("pages/09_Student_Management.py", title="Student Management", icon="👨‍🎓"),
    "Admission Management": st.Page("pages/16_Admission_Management.py", title="Admission Management", icon="📥"),
    "Staff Management": st.Page("pages/10_Staff_Management.py", title="Staff Management", icon="👩‍🏫"),
    "Visitor Management": st.Page("pages/11_Visitor_Management.py", title="Visitor Management", icon="🚶"),
    "Library Management": st.Page("pages/12_Library_Management.py", title="Library Management", icon="📚"),
    "Transport Management": st.Page("pages/13_Transport_Management.py", title="Transport Management", icon="🚌"),
    "Fee Management": st.Page("pages/14_Fee_Management.py", title="Fee Management", icon="💰"),
    "Examination Management": st.Page("pages/15_Examination_Management.py", title="Examination Management", icon="📝"),
    "Academic Structure": st.Page("pages/Academic_Structure.py", title="Academic Structure", icon="📖"),
    "Leave Management": st.Page("pages/Leave_Management.py", title="Leave Management", icon="🗓️"),
    "Fee Structure Management": st.Page("pages/Fee_Structure_Management.py", title="Fee Structure Management", icon="⚙️"),
}

access = MANAGEMENT_ACCESS.get(role, [])

if access == "all":
    allowed_management = list(all_management_pages.values())
else:
    allowed_management = [all_management_pages[name] for name in access if name in all_management_pages]

management_pages = [management_hub] + allowed_management

settings_page = st.Page("pages/17_Settings.py", title="Settings", icon="⚙️")

nav_dict = {
    "": [dashboard],
    "📊 ANALYTICS": analytics_pages,
    "⚙️ ERP MANAGEMENT": management_pages,
}

if role == "Admin":
    nav_dict[" "] = [settings_page]

pg = st.navigation(nav_dict)
pg.run()