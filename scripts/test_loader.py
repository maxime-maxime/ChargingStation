from infrastructure.data.ladesaeulenregister_loader import LadesaeulenregisterLoader

print("=" * 60)
print("🔌 Testing CSV Loader")
print("=" * 60)

try:
    loader = LadesaeulenregisterLoader()
    stations = loader.load_berlin_stations()
    
    print(f"\n✅ SUCCESS! Loaded {len(stations)} Berlin stations")
    
    print("\n📍 First 3 stations:")
    for i, station in enumerate(stations[:3], 1):
        print(f"\n{i}. {station.name}")
        print(f"   ID: {station.station_id.value}")
        print(f"   Postal Code: {station.postal_code}")
        print(f"   Address: {station.address or 'N/A'}")
    
    print("\n" + "=" * 60)
    print("✅ Ready to build Streamlit UI!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
