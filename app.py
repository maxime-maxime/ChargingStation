import streamlit as st
import pandas as pd
from uuid import uuid4

# Import your real domain logic
from infrastructure.repositories.in_memory_charging_station_repository import InMemoryChargingStationRepository
from infrastructure.repositories.in_memory_malfunction_report_repository import InMemoryMalfunctionReportRepository
from domain.services.malfunction_report_service import MalfunctionReportService
from infrastructure.data.ladesaeulenregister_loader import LadesaeulenregisterLoader
from domain.enums.malfunction_type import MalfunctionType
from domain.enums.report_status import ReportStatus
from domain.value_objects.station_id import StationId # Make sure this import is at the top

# --- PAGE CONFIG ---
st.set_page_config(page_title="Berlin EV Support", layout="wide", page_icon="🔌")

# --- INITIALIZE SYSTEM (The "Brain") ---
@st.cache_resource
def init_system():
    station_repo = InMemoryChargingStationRepository()
    report_repo = InMemoryMalfunctionReportRepository()
    
    # Load REAL Berlin stations from your CSV
    loader = LadesaeulenregisterLoader()
    berlin_stations = loader.load_berlin_stations()
    for station in berlin_stations:
        station_repo.save(station)
        
    service = MalfunctionReportService(report_repo, station_repo)
    return service, station_repo

service, station_repo = init_system()

# --- TABS FOR DIFFERENT VIEWS ---
tab1, tab2, tab3 = st.tabs(["📢 Report Issue", "👷 Operator Dashboard", "📊 Network Stats"])

# --- TAB 1: USER REPORTING ---
with tab1:
    st.header("Report a Malfunction")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        with st.container(border=True):
            st.subheader("Station Selection")
            all_stations = station_repo.find_all()
            station_map = {f"{s.name} ({s.postal_code})": s.station_id.value for s in all_stations}
            
            selected_display = st.selectbox("Which station are you at?", options=list(station_map.keys()))
            selected_id = station_map[selected_display]
            current_station = station_repo.find_by_id(StationId(selected_id))
            
            st.info(f"📍 **Address:** {current_station.address or 'Berlin'}")
            if current_station.latitude:
                st.map(pd.DataFrame({'lat': [current_station.latitude], 'lon': [current_station.longitude]}))

    with col2:
        with st.form("malfunction_form"):
            st.subheader("Issue Details")
            m_type = st.selectbox("Issue Type", options=[t for t in MalfunctionType], format_func=lambda x: x.value.replace('_', ' ').title())
            description = st.text_area("What's wrong?", help="Minimum 10 characters required.")
            email = st.text_input("Your Email (Optional)")
            
            submit = st.form_submit_button("Submit Report", use_container_width=True)
            
            if submit:
                try:
                    # Run your TDD-tested logic!
                    report_id = service.submit_malfunction_report(selected_id, m_type, description, email)
                    result = service.process_malfunction_report(report_id)
                    
                    if result.success:
                        st.success(f"Report Submitted! Ticket: {str(result.ticket_id)[:8]}")
                        st.balloons()
                    else:
                        st.error(f"Validation Error: {', '.join(result.errors)}")
                except ValueError as e:
                    st.warning(f"Validation Rule: {e}")

# --- TAB 2: OPERATOR DASHBOARD ---
with tab2:
    st.header("Operator Control Panel")
    reports = service.get_all_reports()
    
    pending_reports = [r for r in reports if r.status != ReportStatus.RESOLVED]
    
    if not pending_reports:
        st.write("✅ No open tickets! All stations operational.")
    else:
        for r in pending_reports:
            with st.expander(f"TICKET: {str(r.ticket_id)[:8]} - Station: {r.station_id.value}"):
                st.write(f"**Issue:** {r._malfunction_type.value}")
                st.write(f"**Details:** {r._description.value}")
                
                if st.button("Mark as Resolved", key=f"res_{r.report_id}"):
                    service.resolve_malfunction(r.ticket_id, "Fixed by Operator")
                    st.rerun()

# --- TAB 3: STATISTICS ---
with tab3:
    st.header("Berlin Network Overview")
    total_stations = len(station_repo.find_all())
    total_reports = len(service.get_all_reports())
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Stations", total_stations)
    c2.metric("Active Reports", len(pending_reports))
    c3.metric("System Health", f"{(1 - len(pending_reports)/total_stations)*100:.1f}%")