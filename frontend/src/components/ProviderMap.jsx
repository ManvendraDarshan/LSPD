import { MapContainer, Marker, Popup, TileLayer } from "react-leaflet";
import L from "leaflet";
import { Link } from "react-router-dom";

const icon = new L.Icon({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41]
});

export default function ProviderMap({ providers = [], center = [23.4733, 77.9479], height = "520px" }) {
  const withLocations = providers.filter((p) => p.latitude && p.longitude);
  const mapCenter = withLocations[0] ? [withLocations[0].latitude, withLocations[0].longitude] : center;
  return (
    <div className="overflow-hidden rounded-lg border bg-white" style={{ height }}>
      <MapContainer center={mapCenter} zoom={withLocations.length ? 12 : 6} scrollWheelZoom className="h-full w-full">
        <TileLayer attribution="&copy; OpenStreetMap contributors" url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        {withLocations.map((provider) => (
          <Marker key={provider.id} position={[provider.latitude, provider.longitude]} icon={icon}>
            <Popup>
              <div className="space-y-1">
                <strong>{provider.business_name}</strong>
                <div>{provider.categories?.[0]?.name}</div>
                <div>{provider.average_rating} stars</div>
                <Link to={`/providers/${provider.id}`}>Open details</Link>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}
