import streamlit as st
import pyodbc
import pandas as pd

# --- DATABASE CONNECTION ---
# Update 'SERVER_NAME' with your specific Azure Data Studio Server Name (usually 'localhost' or your PC name)
def init_connection():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=localhost;" 
        "DATABASE=AutomatedCRM;"
        "Trusted_Connection=yes;"
    )

conn = init_connection()

# Helper function to run queries
def run_query(query):
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()

# Helper function to get data as a DataFrame (for tables)
def get_data(query):
    return pd.read_sql(query, conn)









# --- APP LAYOUT ---
st.title("🚀 Automated CRM System")
st.sidebar.title("Navigation")
option = st.sidebar.radio("Go to:", ["Dashboard", "Add New Lead", "Sales Agents", "Automation Center"])

# --- TAB 1: DASHBOARD (SHOWCASING SQL JOINS) ---
if option == "Dashboard":
    st.header("Executive Overview")

    # KPI: Total Revenue
    # Concept: Aggregation
    revenue = get_data("SELECT SUM(TotalAmount) as Total FROM Deals WHERE Stage = 'Closed-Won'")
    total_rev = revenue.iloc[0]['Total']
    st.metric(label="Total Revenue", value=f"${total_rev:,.2f}")

    # Report: Recent Deal Activity
    # Concept: SQL JOIN (Deals -> Customers -> Agents)
    st.subheader("Recent Closed Deals")
    sql_recent_deals = """
                       SELECT D.DealDate, \
                              C.FirstName + ' ' + C.LastName as Customer, \
                              A.LastName                     as Agent, \
                              D.TotalAmount
                       FROM Deals D
                                JOIN Customers C ON D.CustomerID = C.CustomerID
                                JOIN SalesAgents A ON D.AgentID = A.AgentID
                       WHERE D.Stage = 'Closed-Won'
                       ORDER BY D.DealDate DESC \
                       """
    st.dataframe(get_data(sql_recent_deals))

# --- TAB 2: DATA ENTRY (SHOWCASING DML - INSERT) ---
elif option == "Add New Lead":
    st.header("Capture New Lead")

    with st.form("lead_form"):
        # Get dynamic lists for dropdowns
        campaigns = get_data("SELECT CampaignID, CampaignName FROM MarketingCampaigns")
        agents = get_data("SELECT AgentID, LastName FROM SalesAgents")

        fname = st.text_input("First Name")
        lname = st.text_input("Last Name")

        # Dropdowns
        camp_choice = st.selectbox("Source Campaign", campaigns['CampaignName'])
        agent_choice = st.selectbox("Assign Agent", agents['LastName'])

        submitted = st.form_submit_button("Save Lead")

        if submitted:
            # Concept: DML (INSERT)
            # 1. Find IDs from names
            camp_id = campaigns[campaigns['CampaignName'] == camp_choice]['CampaignID'].values[0]
            agent_id = agents[agents['LastName'] == agent_choice]['AgentID'].values[0]

            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Leads (FirstName, LastName, CampaignID, AssignedAgentID) VALUES (?, ?, ?, ?)",
                (fname, lname, int(camp_id), int(agent_id))
            )
            conn.commit()
            st.success(f"Lead {fname} {lname} added successfully!")

# --- TAB 3: AGENT VIEW (SHOWCASING 1:M RELATIONS) ---
elif option == "Sales Agents":
    st.header("busts Sales Force")

    # Concept: Group By & Joins
    sql_agents = """
                 SELECT SA.FirstName, \
                        SA.LastName, \
                        R.RegionName, \
                        COUNT(L.LeadID) as ActiveLeads
                 FROM SalesAgents SA
                          JOIN Regions R ON SA.RegionID = R.RegionID
                          LEFT JOIN Leads L ON SA.AgentID = L.AssignedAgentID
                 GROUP BY SA.FirstName, SA.LastName, R.RegionName \
                 """
    st.table(get_data(sql_agents))

# --- TAB 4: AUTOMATION (SHOWCASING COMPLEX LOGIC) ---
elif option == "Automation Center":
    st.header("CRM Automation")

    st.subheader("Identify Neglected Leads")
    st.write("Find leads who haven't been converted to customers yet (Over 30 days).")

    if st.button("Run Audit"):
        # Concept: Complex Filtering/Subqueries
        sql_neglected = """
                        SELECT L.FirstName, L.LastName, MC.CampaignName
                        FROM Leads L
                                 JOIN MarketingCampaigns MC ON L.CampaignID = MC.CampaignID
                        WHERE L.LeadID NOT IN (SELECT LeadID FROM Customers WHERE LeadID IS NOT NULL) \
                        """
        results = get_data(sql_neglected)

        if not results.empty:
            st.warning(f"Found {len(results)} neglected leads!")
            st.dataframe(results)
        else:
            st.success("All leads are being processed correctly.")