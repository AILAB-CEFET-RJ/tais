import {
  Box,
  FormControlLabel,
  FormGroup,
  Switch,
  Typography,
} from "@mui/material";
import L, { LatLngExpression } from "leaflet";
import { useCallback, useMemo, useState } from "react";
import {
  MapContainer,
  Marker,
  Popup,
  TileLayer,
  useMap,
  useMapEvents,
} from "react-leaflet";
import "leaflet.heat";
import { CordTextField } from "../TextField";
import vesselReport from "../../constants/ais_data.json";
import FilterSection from "./components/FilterSection";
import Heatmap from "./components/Heatmap";

const defaultZoom = 10;
const BoatIcon = L.icon({
  iconUrl: "assets/marker.png",
  iconSize: [16, 16],
  iconAnchor: [12, 12],
  popupAnchor: [0, 0],
});

const MapEventsHandler: React.FC<{
  onMapMove: (center: { lat: number; lng: number }) => void;
}> = ({ onMapMove }) => {
  useMapEvents({
    move: (event) => {
      const map = event.target;
      const center = map.getCenter();
      onMapMove(center);
    },
  });

  return null;
};

const data: any = [
  [-15.7801, -47.9292, 0.8],
  [-22.9068, -43.1729, 0.6],
  [-23.5505, -46.6333, 0.9],
  [-12.9716, -38.5018, 0.7],
  [-3.7172, -38.5433, 0.4],
  [-7.2307, -35.8814, 0.5],
  [-15.601, -56.0974, 0.3],
  [-30.0331, -51.2362, 0.6],
  [-16.6861, -49.2646, 0.7],
  [-27.5969, -48.5495, 0.5],
  [-29.6904, -53.8008, 0.4],
  [-5.7945, -35.212, 0.8],
  [-22.9083, -43.1964, 0.6],
  [-22.8183, -43.4914, 0.7],
  [-23.319, -51.1524, 0.5],
  [-29.1669, -51.5206, 0.4],
  [-25.4444, -49.2754, 0.6],
  [-20.2976, -40.295, 0.7],
  [-16.6478, -49.2667, 0.5],
  [-21.1818, -47.7997, 0.4],
  [-23.5917, -46.6431, 0.8],
  [-8.0476, -34.877, 0.6],
  [-23.6375, -46.7611, 0.7],
  [-5.083, -42.8019, 0.5],
  [-5.559, -36.894, 0.4],
  [-22.227, -54.8128, 0.6],
  [-12.9918, -38.5023, 0.7],
  [-29.7032, -52.5073, 0.5],
  [-30.0418, -51.2178, 0.4],
  [-25.9176, -53.3703, 0.8],
  [-25.441, -49.2754, 0.6],
  [-19.9191, -43.9386, 0.7],
  [-23.5505, -46.6333, 0.5],
  [-22.4394, -47.1431, 0.4],
  [-30.0277, -51.2287, 0.6],
  [-8.0476, -34.9326, 0.7],
  [-22.9688, -43.2281, 0.5],
  [-5.7945, -35.211, 0.4],
  [-21.2534, -43.7745, 0.8],
  [-29.1669, -51.5206, 0.6],
  [-25.4444, -49.2765, 0.7],
  [-20.3155, -40.3128, 0.5],
  [-16.6478, -49.2677, 0.4],
  [-21.1821, -47.7958, 0.6],
  [-23.5909, -46.6249, 0.7],
  [-8.0476, -34.898, 0.5],
  [-23.6044, -46.6936, 0.4],
  [-5.0833, -42.8013, 0.8],
  [-5.559, -36.9035, 0.6],
];


const MainContent: React.FC = () => {
  const [lat, setLat] = useState<number>(-22.88);
  const [long, setLong] = useState<number>(-43.2);
  const [seeHeatmap, setSeeHeatmap] = useState<boolean>(false);

  const center = useMemo(() => {
    return [lat, long] as LatLngExpression;
  }, [lat, long]);

  const handleMapMove = useCallback(
    (center: { lat: number; lng: number }) => {
      setLat(center.lat);
      setLong(center.lng);
    },
    [lat, long]
  );

  const toggleHeatmap = (
    event: React.ChangeEvent<HTMLInputElement>,
    checked: boolean
  ) => {
    setSeeHeatmap(checked);
  };

  return (
    <Box
      width="100%"
      height={"calc(100vh - 60px)"}
      bgcolor="#FFF"
      display="flex"
      alignItems="center"
      justifyContent="flex-start"
    >
      <MapContainer
        center={center}
        zoom={defaultZoom}
        scrollWheelZoom={true}
        style={{
          height: "100%",
          width: "100%",
        }}
      >
        {!!seeHeatmap && <Heatmap addressPoints={data} seeHeatmap={seeHeatmap}/>}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {vesselReport.data[0].map((vessel: any) => (
          <Marker
            icon={BoatIcon}
            position={[vessel.latitude, vessel.longitude]}
          >
            <Popup>
              <Box>
                <Typography>
                  <strong>ID da embarcação:</strong> {vessel.ship_id}
                </Typography>
                <Typography>
                  <strong>Nome da embarcação:</strong> {vessel.ship_name}
                </Typography>
              </Box>
            </Popup>
          </Marker>
        ))}
        <MapEventsHandler onMapMove={handleMapMove} />
        <FilterSection
          defaultZoom={defaultZoom}
          setLat={setLat}
          setLong={setLong}
        />
      </MapContainer>
      <Box
        sx={{
          position: "absolute",
          zIndex: "1000",
          top: "70px",
          right: "120px",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          gap: "10px",
          background: "#FFF",
          borderRadius: "8px",
          width: "fit-content",
          padding: "0px 16px",
        }}
      >
        <FormGroup>
          <FormControlLabel
            control={<Switch onChange={toggleHeatmap} value={seeHeatmap} />}
            label="Ver mapa de calor"
          />
        </FormGroup>
      </Box>
      <Box
        sx={{
          position: "absolute",
          zIndex: "1000",
          bottom: "5%",
          left: 0,
          width: "100%",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          gap: "10px",
        }}
      >
        <CordTextField
          variant="filled"
          label="Latitude"
          name="lat"
          value={lat}
        />
        <span>-</span>
        <CordTextField
          variant="filled"
          label="Longitude"
          name="long"
          value={long}
        />
      </Box>
    </Box>
  );
};

export default MainContent;
