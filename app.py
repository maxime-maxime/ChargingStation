import streamlit as st
import pandas as pd
from uuid import uuid4
import folium
from streamlit_folium import st_folium

# Import your domain logic
from infrastructure.repositories.in_memory_charging_station_repository import (
    InMemoryChargingStationRepository
)
from infrastructure.repositories.in_memory_malfunction_report_repository import (
    InMemoryMalfunctionReportRepository
)
from domain.services.malfunction_report_service import MalfunctionReportService
from infrastructure.data.ladesaeulenregister_loader import LadesaeulenregisterLoader
from domain.enums.malfunction_type import MalfunctionType
from domain.enums.report_status import ReportStatus
from domain.value_objects.station_id import StationId

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Berlin EV Charging Network",
    layout="wide",
    page_icon="🔌"
)

# --- INITIALIZE SYSTEM (Cached) ---
@st.cache_resource
def init_system():
    """Initialize repositories, load data, and create service"""
    station_repo = InMemoryChargingStationRepository()
    report_repo = InMemoryMalfunctionReportRepository()
    
    # Load real Berlin stations from CSV
    loader = LadesaeulenregisterLoader()
    berlin_stations = loader.load_berlin_stations()
    
    for station in berlin_stations:
        station_repo.save(station)
    
    service = MalfunctionReportService(report_repo, station_repo)
    
    return service, station_repo

service, station_repo = init_system()

# --- AUTHENTICATION STATE ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# Initialize session state for report form
if 'selected_postal_code' not in st.session_state:
    st.session_state.selected_postal_code = None
if 'selected_station_id' not in st.session_state:
    st.session_state.selected_station_id = None

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("🔌 Berlin EV Network")
page = st.sidebar.radio(
    "Navigation",
    ["🔍 Search Stations", "📢 Report Issue", "👷 Operator Dashboard"]
)

st.sidebar.divider()

# Get real-time stats
all_reports = service.get_all_reports()
open_reports = [r for r in all_reports if r.status != ReportStatus.RESOLVED]
defective_stations = [s for s in station_repo.find_all() if s.status.value == "defective"]

st.sidebar.info(
    f"**📊 Network Status**\n\n"
    f"Total Stations: {len(station_repo.find_all())}\n\n"
    f"Active Reports: {len(open_reports)}\n\n"
    f"Defective Stations: {len(defective_stations)}"
)

# ============================================================================
# PAGE 1: SEARCH CHARGING STATIONS (Public)
# ============================================================================
if page == "🔍 Search Stations":
    st.title("🔍 Search Berlin Charging Stations")
    st.markdown("Find available charging stations by postal code")
    
    # Search input
    col1, col2 = st.columns([3, 1])
    with col1:
        postal_code = st.text_input(
            "Enter Postal Code",
            placeholder="e.g., 10115, 10178, 10785",
            help="Berlin postal codes start with 1"
        )
    
    with col2:
        search_button = st.button("🔍 Search", use_container_width=True, type="primary")
    
    # Validation
    if search_button:
        if not postal_code:
            st.error("❌ Please enter a postal code")
        elif not postal_code.isdigit() or len(postal_code) != 5:
            st.error("❌ Invalid postal code format (must be 5 digits)")
        elif not postal_code.startswith('1'):
            st.error("❌ Please enter a Berlin postal code (starts with 1)")
        else:
            # Search stations
            stations = station_repo.find_by_postal_code(postal_code)
            
            if not stations:
                st.warning(f"⚠️ No charging stations found in postal code {postal_code}")
            else:
                st.success(f"✅ Found {len(stations)} charging station(s) in {postal_code}")
                
                # Create map with ALL stations as pins
                stations_with_coords = [s for s in stations if s.latitude and s.longitude]
                
                if stations_with_coords:
                    st.subheader("📍 Station Locations Map")
                    
                    # Calculate bounds to fit all stations
                    lats = [s.latitude for s in stations_with_coords]
                    lons = [s.longitude for s in stations_with_coords]
                    
                    # Center of all stations
                    center_lat = sum(lats) / len(lats)
                    center_lon = sum(lons) / len(lons)
                    
                    # Create map centered on stations
                    m = folium.Map(location=[center_lat, center_lon], zoom_start=13)
                    
                    # Add markers for each station
                    for station in stations_with_coords:
                        # Color code by status
                        if station.status.value == "available":
                            icon_color = "green"
                            icon = "ok-sign"
                        elif station.status.value == "defective":
                            icon_color = "red"
                            icon = "remove-sign"
                        elif station.status.value == "in_use":
                            icon_color = "blue"
                            icon = "time"
                        else:
                            icon_color = "gray"
                            icon = "question-sign"
                        
                        # Create popup text
                        popup_text = f"""
                        <b>{station.name}</b><br>
                        Address: {station.address or 'N/A'}<br>
                        Status: <b>{station.status.value.upper()}</b><br>
                        ID: {station.station_id.value}
                        """
                        
                        folium.Marker(
                            location=[station.latitude, station.longitude],
                            popup=folium.Popup(popup_text, max_width=300),
                            tooltip=station.name,
                            icon=folium.Icon(color=icon_color, icon=icon, prefix='glyphicon')
                        ).add_to(m)
                    
                    # Fit map to show all markers
                    if len(stations_with_coords) > 1:
                        # Calculate bounds
                        sw = [min(lats), min(lons)]  # Southwest corner
                        ne = [max(lats), max(lons)]  # Northeast corner
                        m.fit_bounds([sw, ne], padding=[50, 50])
                    
                    # Display the map - returned_objects=[] prevents re-render on click
                    st_folium(m, width=1200, height=400, returned_objects=[])
                    st.caption(f"🗺️ Showing {len(stations_with_coords)} stations | 🟢 Available | 🔴 Defective | 🔵 In Use")
                else:
                    st.warning("⚠️ No GPS coordinates available for stations in this area")
                
                st.divider()
                st.subheader("📋 Station Details")
                
                # Display stations as expandable cards
                for i, station in enumerate(stations, 1):
                    with st.expander(f"📍 {station.name}", expanded=i<=3):
                        col_a, col_b = st.columns([2, 1])
                        
                        with col_a:
                            st.write(f"**Station ID:** {station.station_id.value}")
                            st.write(f"**Address:** {station.address or 'N/A'}")
                            st.write(f"**Postal Code:** {station.postal_code}")
                            
                            # Status with color coding
                            status = station.status.value
                            if status == "available":
                                st.success(f"🟢 Status: AVAILABLE")
                            elif status == "in_use":
                                st.info(f"🔵 Status: IN USE")
                            elif status == "defective":
                                st.error(f"🔴 Status: DEFECTIVE")
                            else:
                                st.warning(f"🟡 Status: {status.upper()}")
                        
                        with col_b:
                            # Individual station map
                            if station.latitude and station.longitude:
                                mini_map = folium.Map(
                                    location=[station.latitude, station.longitude],
                                    zoom_start=15
                                )
                                folium.Marker(
                                    [station.latitude, station.longitude],
                                    popup=station.name,
                                    tooltip="Station location"
                                ).add_to(mini_map)
                                st_folium(mini_map, width=300, height=200, returned_objects=[])
                            else:
                                st.info("📍 GPS not available")

# ============================================================================
# PAGE 2: REPORT MALFUNCTION (Public) - IMPROVED
# ============================================================================
elif page == "📢 Report Issue":
    st.title("📢 Report Charging Station Malfunction")
    st.markdown("Help us maintain the network by reporting issues")
    
    # Step 1: Search by Postal Code
    st.subheader("1️⃣ Find Your Station")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        search_postal = st.text_input(
            "Enter Postal Code where the station is located",
            placeholder="e.g., 10115",
            key="report_postal_search"
        )
    
    with col2:
        find_button = st.button("🔍 Find Stations", use_container_width=True)
    
    # When postal code is searched
    if find_button and search_postal:
        if search_postal.isdigit() and len(search_postal) == 5:
            stations_in_area = station_repo.find_by_postal_code(search_postal)
            if stations_in_area:
                st.session_state.selected_postal_code = search_postal
                st.success(f"✅ Found {len(stations_in_area)} station(s)")
            else:
                st.warning(f"⚠️ No stations found in {search_postal}")
                st.session_state.selected_postal_code = None
        else:
            st.error("❌ Invalid postal code")
    
    # Step 2: If postal code found, show station selection
    if st.session_state.selected_postal_code:
        st.divider()
        st.subheader("2️⃣ Select the Specific Station")
        
        stations_in_area = station_repo.find_by_postal_code(st.session_state.selected_postal_code)
        
        # Create dropdown with station names
        station_options = {
            f"{s.name} - {s.address or 'Berlin'}": s.station_id.value 
            for s in stations_in_area
        }
        
        selected_display = st.selectbox(
            "Which specific station has the issue?",
            options=list(station_options.keys()),
            help="Select the exact station where you experienced a problem"
        )
        
        selected_id = station_options[selected_display]
        st.session_state.selected_station_id = selected_id
        current_station = station_repo.find_by_id(StationId(selected_id))
        
        # Show selected station details
        col_detail1, col_detail2 = st.columns([1, 1])
        
        with col_detail1:
            with st.container(border=True):
                st.write("**📍 Selected Station**")
                st.write(f"**Name:** {current_station.name}")
                st.write(f"**Address:** {current_station.address or 'Berlin'}")
                st.write(f"**Station ID:** {current_station.station_id.value}")
                st.write(f"**Current Status:** {current_station.status.value.upper()}")
        
        with col_detail2:
            if current_station.latitude and current_station.longitude:
                detail_map = folium.Map(
                    location=[current_station.latitude, current_station.longitude],
                    zoom_start=15
                )
                folium.Marker(
                    [current_station.latitude, current_station.longitude],
                    popup=current_station.name,
                    icon=folium.Icon(color='red', icon='exclamation-sign')
                ).add_to(detail_map)
                st_folium(detail_map, width=400, height=250, returned_objects=[])
        
        # Step 3: Report Form
        st.divider()
        st.subheader("3️⃣ Describe the Issue")
        
        with st.form("malfunction_form"):
            # Malfunction type with icons
            malfunction_icons = {
                MalfunctionType.NOT_CHARGING: "⚡ Not Charging",
                MalfunctionType.PAYMENT_FAILURE: "💳 Payment Failure",
                MalfunctionType.PAYMENT_NOT_REFLECTED: "💰 Payment Not Reflected",
                MalfunctionType.PHYSICAL_DAMAGE: "🔨 Physical Damage",
                MalfunctionType.DISPLAY_MALFUNCTION: "🖥️ Display Malfunction",
                MalfunctionType.CONNECTOR_ISSUE: "🔌 Connector Issue",
                MalfunctionType.OTHER: "❓ Other"
            }
            
            m_type = st.selectbox(
                "What type of issue?",
                options=list(MalfunctionType),
                format_func=lambda x: malfunction_icons[x]
            )
            
            description = st.text_area(
                "Description (10-500 characters)",
                placeholder="Please describe the issue in detail...",
                help="Minimum 10 characters, maximum 500 characters",
                max_chars=500
            )
            
            # Character counter
            if description:
                char_count = len(description)
                if char_count < 10:
                    st.warning(f"⚠️ {10 - char_count} more characters needed")
                else:
                    st.success(f"✅ {char_count}/500 characters")
            
            email = st.text_input(
                "Your Email (Optional)",
                placeholder="email@example.com",
                help="We'll notify you when the issue is resolved"
            )
            
            submit = st.form_submit_button(
                "🚀 Submit Report",
                use_container_width=True,
                type="primary"
            )
            
            if submit:
                try:
                    # Submit through service (triggers validation)
                    report_id = service.submit_malfunction_report(
                        station_id=selected_id,
                        malfunction_type=m_type,
                        description=description,
                        reported_by=email if email else None
                    )
                    
                    # Process report (business rules)
                    result = service.process_malfunction_report(report_id)
                    
                    if result.success:
                        st.success(
                            f"✅ **Report Submitted Successfully!**\n\n"
                            f"Ticket ID: `{str(result.ticket_id)[:8]}...`\n\n"
                            f"The station has been marked as defective and maintenance has been notified."
                        )
                        st.balloons()
                        
                        # Reset form
                        st.session_state.selected_postal_code = None
                        st.session_state.selected_station_id = None
                    else:
                        st.error(
                            f"❌ **Validation Failed**\n\n" +
                            "\n".join(f"- {error}" for error in result.errors)
                        )
                        
                except ValueError as e:
                    st.error(f"⚠️ **Validation Error:** {str(e)}")
    else:
        st.info("👆 Enter a postal code above to find stations in that area")

# ============================================================================
# PAGE 3: OPERATOR DASHBOARD (Login Required)
# ============================================================================
elif page == "👷 Operator Dashboard":
    
    # Authentication check
    if not st.session_state.authenticated:
        st.title("🔐 Operator Login")
        st.markdown("Please login to access the operator dashboard")
        
        col_login1, col_login2, col_login3 = st.columns([1, 2, 1])
        
        with col_login2:
            with st.form("login_form"):
                st.write("**System Operator Access**")
                username = st.text_input("Username", placeholder="operator")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                login_button = st.form_submit_button("🔓 Login", use_container_width=True, type="primary")
                
                if login_button:
                    # Simple authentication (demo)
                    if username == "operator" and password == "berlin2025":
                        st.session_state.authenticated = True
                        st.success("✅ Login successful!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials")
            
            st.divider()
            
            with st.expander("ℹ️ Demo Credentials", expanded=True):
                st.code("Username: operator\nPassword: berlin2025")
                st.caption("""
                **Note:** In a production system, credentials would be:
                - Stored securely in a database (hashed with bcrypt/argon2)
                - Use JWT tokens or session management
                - Support multiple operators with role-based access
                - Include 2FA for security
                
                For this demo/assignment, hardcoded credentials are acceptable
                to demonstrate the authentication flow.
                """)
    
    else:
        # Authenticated - show dashboard
        col_header1, col_header2 = st.columns([4, 1])
        
        with col_header1:
            st.title("👷 Operator Dashboard")
            st.markdown("**Berlin-Wide Network Management** - All stations across Berlin")
        
        with col_header2:
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.authenticated = False
                st.rerun()
        
        # Get reports
        all_reports = service.get_all_reports()
        open_reports = [r for r in all_reports if r.status != ReportStatus.RESOLVED]
        resolved_reports = [r for r in all_reports if r.status == ReportStatus.RESOLVED]
        
        # Metrics
        metric1, metric2, metric3, metric4 = st.columns(4)
        metric1.metric("📊 Total Reports", len(all_reports))
        metric2.metric("🔴 Open Tickets", len(open_reports))
        metric3.metric("✅ Resolved", len(resolved_reports))
        
        defective_count = len([s for s in station_repo.find_all() if s.status.value == "defective"])
        metric4.metric("⚠️ Defective Stations", defective_count)
        
        st.divider()
        
        # Open Tickets Section
        st.subheader("🔴 Open Tickets - Requires Attention")
        
        if not open_reports:
            st.success("✅ No open tickets! All stations across Berlin are operational.")
            st.balloons()
        else:
            st.warning(f"⚠️ {len(open_reports)} station(s) need maintenance")
            
            for report in open_reports:
                station = station_repo.find_by_id(report.station_id)
                
                with st.expander(
                    f"🎫 Ticket: {str(report.ticket_id)[:8]}... | {station.name} ({station.postal_code})",
                    expanded=True
                ):
                    col_a, col_b = st.columns([2, 1])
                    
                    with col_a:
                        st.write(f"**Station:** {station.name}")
                        st.write(f"**Address:** {station.address or 'Berlin'}")
                        st.write(f"**Station ID:** {report.station_id.value}")
                        st.write(f"**Report ID:** {report.report_id}")
                        st.write(f"**Malfunction Type:** {report._malfunction_type.value.replace('_', ' ').title()}")
                        st.write(f"**Description:** {report._description.value}")
                        st.write(f"**Reported By:** {report._reported_by or 'Anonymous'}")
                        st.write(f"**Created:** {report._created_at.strftime('%Y-%m-%d %H:%M')}")
                        st.write(f"**Status:** {report.status.value.upper()}")
                    
                    with col_b:
                        operator_notes = st.text_area(
                            "Resolution Notes",
                            placeholder="Describe what was fixed...\ne.g., 'Replaced connector cable. Tested charging cycle.'",
                            key=f"notes_{report.report_id}",
                            height=120
                        )
                        
                        if st.button(
                            "✅ Mark as Resolved",
                            key=f"resolve_{report.report_id}",
                            use_container_width=True,
                            type="primary"
                        ):
                            if report.ticket_id:
                                service.resolve_malfunction(
                                    ticket_id=report.ticket_id,
                                    operator_notes=operator_notes or "Issue resolved by operator"
                                )
                                st.success("✅ Ticket resolved! Station restored to available.")
                                st.rerun()
        
        st.divider()
        
        # Resolved Tickets Section
        with st.expander(f"✅ Recently Resolved Tickets ({len(resolved_reports)})", expanded=False):
            if resolved_reports:
                st.caption("Showing most recent resolved tickets")
                for report in reversed(resolved_reports[-10:]):  # Show last 10, most recent first
                    station = station_repo.find_by_id(report.station_id)
                    st.write(
                        f"- **{str(report.ticket_id)[:8]}...** | "
                        f"{station.name} ({station.postal_code}) | "
                        f"Type: {report._malfunction_type.value.replace('_', ' ').title()}"
                    )
            else:
                st.write("No resolved tickets yet.")