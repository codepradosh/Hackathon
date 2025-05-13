import os, requests, streamlit as st, pandas as pd

st.set_page_config(page_title="GeoChatBot", page_icon="🌍", layout="wide")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8091").rstrip("/")
CHAT_ENDPOINT = f"{BACKEND_URL}/chat"

with st.sidebar:
    st.title("🌍 GeoChatBot")
    st.markdown("Chat with an AI tour guide about any place on Earth.")
    st.divider()

st.header("Ask about any city or country ✈️")

col1, col2 = st.columns([2, 1], gap="large")

with col1:
    q = st.text_input("Where to?", placeholder="e.g. Best time to visit Kyoto", key="q")
    if st.button("Tell me about it", use_container_width=True) and q.strip():
        with st.spinner("GeoGuide is thinking…"):
            try:
                r = requests.post(CHAT_ENDPOINT, json={"query": q.strip()})
                r.raise_for_status()
                data = r.json()
            except Exception as e:
                st.error(f"❌ {e}")
                st.stop()

        st.success("Here you go!")

        # Clean Answer Styling (No Bold, Nice Layout)
        st.markdown(
            f"""
            <div style='
                font-size: 18px;
                font-weight: normal;
                line-height: 1.6;
                max-width: 900px;
                text-align: justify;
                padding: 10px 20px;
                background: #1e1e1e;
                border-radius: 12px;
                border: 1px solid #333;
                box-shadow: 0 2px 8px rgba(0,0,0,0.2);
                font-family: "Segoe UI", "Roboto", "Helvetica Neue", sans-serif;
            '>
            <span style="font-size: 20px;">🧑‍🎤</span> {data['answer']}
            </div>
            """,
            unsafe_allow_html=True
        )

        card = data["source_data"]
        facts = {
            "Latitude": card.get("lat"),
            "Longitude": card.get("lon"),
            "Population": card.get("population"),
            "Region": card.get("region"),
            "Timezone": card.get("timezone"),
        }
        facts_str = {k: ("—" if v in (None, "", 0) else str(v)) for k, v in facts.items()}
        st.subheader("Key facts")
        st.dataframe(pd.DataFrame(facts_str.items(), columns=["Field", "Value"]), use_container_width=True)

        nearby = card.get("nearby", [])
        if nearby:
            st.subheader("Nearby cities (≈100 km)")
            st.write(", ".join(nearby))

        # ----------------------------
        # Map with main location + nearby cities
        # ----------------------------
        if card.get("lat") and card.get("lon"):
            st.subheader("Map")

            # Main location
            locations = [{
                "name": card.get("display_name", "Main Location"),
                "lat": card["lat"],
                "lon": card["lon"]
            }]

            # Nearby cities with lat/lon
            nearby_data = card.get("nearby_data", [])
            if isinstance(nearby_data, list):
                for city in nearby_data:
                    if city.get("lat") and city.get("lon"):
                        locations.append({
                            "name": city["name"],
                            "lat": city["lat"],
                            "lon": city["lon"]
                        })

            # Convert to DataFrame and show on map
            df_map = pd.DataFrame(locations)
            st.map(df_map, zoom=6)

            # ----------------------------
            # Better looking table below map
            # ----------------------------
            st.subheader("Nearby Locations Table")
            st.dataframe(
                df_map[["name", "lat", "lon"]].set_index("name"),
                use_container_width=True,
                height=350
            )

with col2:
  st.image(
    "img.jpg", 
    caption="Travel Vibe", 
    use_column_width=True
)

st.divider(); st.caption("©️ 2025 GeoChatBot 🛠️")
