import { Box, Button, Drawer, TextField, Typography } from "@mui/material";
import { useState } from "react";
import { Controller, SubmitHandler, useForm } from "react-hook-form";
import ShipType from "../../../types/ships";
import { BiFilter } from "react-icons/bi";
import vesselReport from "../../../constants/ais_data.json";
import { useMap } from "react-leaflet";

interface FilterSectionProps {
  setLong: any;
  setLat: any;
  defaultZoom: number;
}

const FilterSection: React.FC<FilterSectionProps> = ({
  setLong,
  setLat,
  defaultZoom,
}) => {
  const [showFilters, setShowFilters] = useState<boolean>(false);
  const { handleSubmit, control, reset } = useForm<ShipType>();
  const map = useMap();

  const onSubmit: SubmitHandler<ShipType> = (data) => {
    setShowFilters(false);
    const vesselFound = filterAction(data.ship_id, data.ship_name);

    if (!!vesselFound) {
      setLat(vesselFound.latitude);
      setLong(vesselFound.longitude);
      map.setView([vesselFound.latitude, vesselFound.longitude], 80);
      reset();
      return;
    }

    reset();
    return;
  };

  const filterAction = (ship_id = "", ship_name = "") => {
    return vesselReport.data[0].find(
      (vessel: any) =>
        vessel.ship_id === ship_id || vessel.ship_name === ship_name
    );
  };

  return (
    <>
      <Box
        width={"fit-content"}
        height={"fit-content"}
        position={"absolute"}
        top={"10px"}
        right={"10px"}
        zIndex="1000"
      >
        <Button
          startIcon={<BiFilter />}
          variant="contained"
          disableElevation
          disableFocusRipple
          disableTouchRipple
          disableRipple
          onClick={() => setShowFilters(true)}
          sx={{
            borderRadius: "8px",
            background: "#fff",
            color: "#555866",
            textTransform: "none",
            ":hover": {
              borderRadius: "8px",
              background: "#fff",
              color: "#000",
              textTransform: "none",
            },
          }}
        >
          Filtros
        </Button>
      </Box>
      <Drawer
        anchor={"right"}
        PaperProps={{
          sx: {
            padding: "24px",
            width: "400px",
            display: "flex",
            flexDirection: "column",
            gap: "10px",
          },
        }}
        open={showFilters}
        onClose={() => setShowFilters(false)}
      >
        <Box>
          <Typography
            variant="h1"
            sx={{
              fontSize: "24px",
              color: "#555866",
            }}
          >
            Filtros
          </Typography>
        </Box>
        <form onSubmit={handleSubmit(onSubmit)} style={{display: 'flex', flexDirection: 'column', gap: '10px'}}>
          <Typography
            sx={{
              fontSize: "16px",
              color: "#555866",
            }}
          >
            ID da embarcação
          </Typography>

          <Controller
            name="ship_id"
            control={control}
            render={({ field }) => (
              <TextField {...field} fullWidth placeholder="ex: 1241257AF5" />
            )}
          />
          <Typography
            sx={{
              fontSize: "16px",
              color: "#555866",
            }}
          >
            Nome da embarcação
          </Typography>
          <Controller
            name="ship_name"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                fullWidth
                placeholder="ex: MINHAEMBARCACAO"
              />
            )}
          />
          <Box mt={"24px"} display={"flex"} justifyContent={"flex-end"}>
            <Button
              type="submit"
              variant="contained"
              disableElevation
              disableFocusRipple
              disableTouchRipple
              disableRipple
              onClick={() => setShowFilters(true)}
              sx={{
                borderRadius: "8px",
                background: "#0068FF",
                color: "#FFF",
                textTransform: "none",
                ":hover": {
                  borderRadius: "8px",
                  background: "#0068FF",
                  color: "#FFF",
                  textTransform: "none",
                },
              }}
            >
              Filtrar
            </Button>
          </Box>
        </form>
      </Drawer>
    </>
  );
};

export default FilterSection;
