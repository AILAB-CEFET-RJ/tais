import L, { HeatLatLngTuple, LatLng } from "leaflet";
import { useCallback, useEffect, useState } from "react";
import { useMap } from "react-leaflet";

interface HeatmapProps {
  seeHeatmap: boolean;
  addressPoints: any;
}

const Heatmap: React.FC<HeatmapProps> = ({ addressPoints, seeHeatmap }) => {
    const map = useMap();
    const [heatLayer, setHeatLayer] = useState<L.HeatLayer | null>(null);
  
    useEffect(() => {
      if (seeHeatmap) {
        if (!!!heatLayer) {
          const points = addressPoints
            ? addressPoints?.map((p: any) => [p[0], p[1], p[2]]) // lat lng intensity
            : [];
          const newHeatLayer = L.heatLayer(points, {});
          newHeatLayer.addTo(map);
          setHeatLayer(newHeatLayer);
        }
      } else {
        
          heatLayer?.remove();
          setHeatLayer(null);
        
      }
    }, [seeHeatmap, addressPoints, map, heatLayer]);
  
    return null;
  };
  
  export default Heatmap;