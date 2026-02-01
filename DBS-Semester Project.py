import streamlit as st
import pymssql
import pandas as pd


@st.cache_resource
def init_connection():
    return pymssql.connect(
        server="localhost",
        user="sa",
        password="Saadasad2006",
        database="AutomatedCRM"
    )

conn = init_connection()

def get_data(query):
    return pd.read_sql(query, conn)

#--------------------------------------------------

st.set_page_config(page_title="Automated CRM", layout="wide")
st.title("Automated CRM System")
st.sidebar.title("Navigation")
option = st.sidebar.radio("Go to:", ["Dashboard", "Sales Agents", "Automation Center", "Analysis"])

if option == "Dashboard":
    st.header("Overview")

    revenue_df = get_data("SELECT SUM(TotalAmount) as Total FROM Deals WHERE Stage = 'Closed-Won'")
    total_rev = revenue_df.iloc[0]['Total'] if not revenue_df.empty and revenue_df.iloc[0]['Total'] else 0
    st.metric(label="Total Revenue", value=f"${total_rev:,.2f}")

    st.subheader("Recent Closed Deals")
    sql_recent_deals = """
                       SELECT D.DealDate, 
                              C.FirstName + ' ' + C.LastName as Customer, 
                              A.LastName                     as Agent, 
                              D.TotalAmount
                       FROM Deals D
                                JOIN Customers C ON D.CustomerID = C.CustomerID
                                JOIN SalesAgents A ON D.AgentID = A.AgentID
                       WHERE D.Stage = 'Closed-Won'
                       ORDER BY D.DealDate DESC
                       """
    st.dataframe(get_data(sql_recent_deals), use_container_width=True)



elif option == "Sales Agents":
    st.header("Sales Performance:")

    sql_agents = """
                 SELECT SA.FirstName, 
                        SA.LastName, 
                        R.RegionName, 
                        COUNT(L.LeadID) as ActiveLeads
                 FROM SalesAgents SA
                          JOIN Regions R ON SA.RegionID = R.RegionID
                          LEFT JOIN Leads L ON SA.AgentID = L.AssignedAgentID
                 GROUP BY SA.FirstName, SA.LastName, R.RegionName
                 """
    st.table(get_data(sql_agents))

elif option == "Automation Center":
    st.header("CRM Automation")

    st.subheader("Identify Neglected Leads")
    st.write("Find leads who haven't been converted to customers yet.")

    if st.button("Run Audit"):
        sql_neglected = """
                        SELECT L.FirstName, L.LastName, MC.CampaignName
                        FROM Leads L
                                 JOIN MarketingCampaigns MC ON L.CampaignID = MC.CampaignID
                        WHERE L.LeadID NOT IN (SELECT LeadID FROM Customers WHERE LeadID IS NOT NULL)
                        """
        results = get_data(sql_neglected)

        if not results.empty:
            st.warning(f"Found {len(results)} neglected leads!")
            st.dataframe(results, use_container_width=True)
        else:
            st.success("All leads are being processed correctly.")



    with st.expander("➕ Add New Lead"):
        with st.form("lead_form"):
            campaigns = get_data("SELECT CampaignID, CampaignName FROM MarketingCampaigns")
            agents = get_data("SELECT AgentID, LastName FROM SalesAgents")

            col1, col2 = st.columns(2)
            with col1:
                fname = st.text_input("First Name")
                camp_choice = st.selectbox("Source Campaign", campaigns['CampaignName'])
            with col2:
                lname = st.text_input("Last Name")
                agent_choice = st.selectbox("Assign Agent", agents['LastName'])

            submitted = st.form_submit_button("Save Lead")

            if submitted:
                camp_id = campaigns[campaigns['CampaignName'] == camp_choice]['CampaignID'].values[0]
                agent_id = agents[agents['LastName'] == agent_choice]['AgentID'].values[0]

                with conn.cursor() as cursor:
                    sql = "INSERT INTO Leads (FirstName, LastName, CampaignID, AssignedAgentID) VALUES (%s, %s, %s, %s)"
                    cursor.execute(sql, (fname, lname, int(camp_id), int(agent_id)))
                    conn.commit()
                st.success(f"Lead {fname} {lname} added!")
                st.rerun()

    st.divider()


    st.subheader("Current Leads Directory")
    

    leads_df = get_data("""
        SELECT L.LeadID, L.FirstName, L.LastName, MC.CampaignName, SA.LastName as AssignedAgent
        FROM Leads L
        LEFT JOIN MarketingCampaigns MC ON L.CampaignID = MC.CampaignID
        LEFT JOIN SalesAgents SA ON L.AssignedAgentID = SA.AgentID
    """)

    if not leads_df.empty:

        st.dataframe(leads_df, use_container_width=True)

        st.subheader("Remove a Lead")
        leads_df['Display'] = leads_df['LeadID'].astype(str) + ": " + leads_df['FirstName'] + " " + leads_df['LastName']
        
        lead_to_delete = st.selectbox("Select lead to remove:", leads_df['Display'])
        delete_id = lead_to_delete.split(":")[0]

        if st.button("Confirm Delete", type="primary"):
            try:
                with conn.cursor() as cursor:
                    cursor.execute("DELETE FROM Leads WHERE LeadID = %s", (delete_id,))
                    conn.commit()
                st.warning(f"Lead ID {delete_id} removed.")
                st.rerun()
            except Exception as e:
                st.error(f"Error: Could not delete lead. It might be linked to a Customer record. \n{e}")
    else:
        st.info("No leads found in the database.")





elif option == "Analysis":
    st.header("Sales Analysis & Sorting")


    st.subheader("View Deals")


    sort_choice = st.selectbox(
        "Sort Deals By:",
        ["Highest Value (Money)", "Most Recent (Date)", "Deal Stage"]
    )


    if sort_choice == "Highest Value (Money)":
        order_clause = "ORDER BY D.TotalAmount DESC"
    elif sort_choice == "Most Recent (Date)":
        order_clause = "ORDER BY D.DealDate DESC"
    else:
        order_clause = "ORDER BY D.Stage ASC"

    sql_query = f"""
    SELECT 
        D.DealID,
        C.FirstName + ' ' + C.LastName AS Customer,
        D.TotalAmount,
        D.DealDate,
        D.Stage
    FROM Deals D
    JOIN Customers C ON D.CustomerID = C.CustomerID
    {order_clause}
    """

    df = get_data(sql_query)
    

    if sort_choice == "Highest Value (Money)":
        st.dataframe(df.style.highlight_max(axis=0, subset=['TotalAmount']))
    else:
        st.dataframe(df)

    st.markdown("---")
    st.subheader("🏆 Top Performing Agents")
    
    sql_rank = """
    SELECT TOP 5
        SA.FirstName,
        SA.LastName,
        SUM(D.TotalAmount) as RevenueGenerated
    FROM SalesAgents SA
    JOIN Deals D ON SA.AgentID = D.AgentID
    WHERE D.Stage = 'Closed-Won'
    GROUP BY SA.FirstName, SA.LastName
    ORDER BY RevenueGenerated DESC
    """
    
    st.table(get_data(sql_rank))


elif option == "Pipeline View":
    st.header("Lead Conversion Pipeline")


    view_filter = st.radio("Show:", ["All", "Only Leads", "Only Customers"], horizontal=True)


    sql_base = """
    SELECT 
        L.FirstName + ' ' + L.LastName AS Name,
        MC.CampaignName AS Source,
        CASE 
            WHEN C.CustomerID IS NOT NULL THEN 'Customer'
            ELSE 'Lead'
        END AS Status
    FROM Leads L
    LEFT JOIN Customers C ON L.LeadID = C.LeadID
    JOIN MarketingCampaigns MC ON L.CampaignID = MC.CampaignID
    """


    df = get_data(sql_base)

    if view_filter == "Only Leads":
        df = df[df['Status'] == 'Lead']
    elif view_filter == "Only Customers":
        df = df[df['Status'] == 'Customer']


    def color_status(val):
        color = '#d4edda' if val == 'Customer' else '#fff3cd'
        return f'background-color: {color}'

    st.subheader(f"List of {view_filter}")
    

    st.dataframe(df.style.applymap(color_status, subset=['Status']))


    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Leads", len(df[df['Status'] == 'Lead']))
    with col2:
        st.metric("Converted Customers", len(df[df['Status'] == 'Customer']))
