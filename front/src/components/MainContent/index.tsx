import {
  Box,
  FormControlLabel,
  FormGroup,
  Switch,
  Typography,
} from "@mui/material";
import L, { LatLngExpression } from "leaflet";
import { useCallback, useEffect, useMemo, useState } from "react";
import {
  MapContainer,
  Marker,
  Popup,
  TileLayer,
  useMapEvents,
} from "react-leaflet";
import { CordTextField } from "../TextField";
import FilterSection from "./components/FilterSection";
import { aisAPI } from "../../services";
import { GetShipsResponse } from "../../types";
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

const MainContent: React.FC = () => {
  const [lat, setLat] = useState<number>(-22.88);
  const [long, setLong] = useState<number>(-43.2);
  const [vesselReport, setVesselReport] = useState<GetShipsResponse[]>();
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

  const toggleSeeheatmap = (
    event: React.ChangeEvent<HTMLInputElement>,
    checked: boolean
  ) => {
    setSeeHeatmap(!seeHeatmap);
  };

  const getAisData = async () => await aisAPI.get("/api/data");

  const tryGetAisData = async () => {
    try {
      const { data: apiResponse } = await getAisData();
      setVesselReport(apiResponse);
    } catch (err: any) {
      console.log("ERRO", err);
    }
  };

  useEffect(() => {
    tryGetAisData();
  }, []);

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
        <Heatmap seeHeatmap={seeHeatmap} addressPoints={vesselReport} />
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {!!!seeHeatmap && (
          <>
            {vesselReport?.map((vessel: any) => (
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
              vesselReport={vesselReport}
            />
          </>
        )}
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
            control={<Switch onChange={toggleSeeheatmap} />}
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
