import L from "leaflet";
import { useEffect, useState } from "react";
import { useMap } from "react-leaflet";
import { aisAPI } from "../../../../services";
import "leaflet.heat";
import HeatmapLayer from "react-leaflet-heatmap-layer-v3/lib/HeatmapLayer"

interface HeatmapProps {
  seeHeatmap: boolean;
  addressPoints: any;
}

const Heatmap: React.FC<HeatmapProps> = ({ addressPoints, seeHeatmap }) => {
  const map = useMap();

  const [heatmapPoints, setHeatmapPoints] = useState<any>();

  const getHeatmap = async () => await aisAPI.get("/api/heatmap", {});

  const tryGetHeatmap = async () => {
    try {
      const { data: apiResponse } = await getHeatmap();
      console.log("RESPONSE", apiResponse)
      setHeatmapPoints(apiResponse?.heatmap_data)
    } catch (err: any) {
      console.log("ERRO", err);
    }
  };

  useEffect(() => {
      tryGetHeatmap()
  }, [seeHeatmap])


  if(!!!seeHeatmap){
    return <></>
  }
  
  return <HeatmapLayer 
        points={heatmapPoints}
        longitudeExtractor={(p: any) => p[1]}
        latitudeExtractor={(p: any) => p[0]}
        intensityExtractor={(p: any) => parseFloat(p[2])}
        />;
};

export default Heatmap;
