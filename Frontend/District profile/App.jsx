
import { useState } from 'react';
import { districts } from './districtData';
import DistrictMap from './DistrictMap';
import './App.css';

const amenityLabels = [
  ['groceries', 'Groceries'],
  ['restaurants', 'Restaurants'],
  ['asianRestaurants', 'Asian Restaurants'],
  ['cafes', 'Cafes'],
  ['gyms', 'Gyms'],
  ['parks', 'Parks'],
  ['pharmacies', 'Pharmacies'],
];

function formatValue(value) {
  if (value === null || value === undefined || value === '') {
    return 'Data not available';
  }

  return value;
}

function formatRent(rent) {
  if (rent === null || rent === undefined || rent === '') {
    return 'Data not available';
  }

  if (typeof rent === 'number') {
    return `€${rent.toLocaleString('en-IE', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })}/month`;
  }

  if (typeof rent === 'object') {
    const rentDetails = [];

    if (rent.oneBed != null && rent.oneBed !== '') {
      rentDetails.push(
        `1-bedroom: €${Number(rent.oneBed).toLocaleString('en-IE', {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2,
        })}/month`
      );
    }

    if (rent.twoBed != null && rent.twoBed !== '') {
      rentDetails.push(
        `2-bedroom: €${Number(rent.twoBed).toLocaleString('en-IE', {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2,
        })}/month`
      );
    }

    return rentDetails.length
  ? rentDetails.join('\n')
  : 'Data not available';
  }

  return 'Data not available';
}

function FamousPlaceCard({ place }) {
  const [imageFailed, setImageFailed] = useState(false);

  return (
    <article className="place-card">
      {place.image && !imageFailed ? (
        <img
          className="place-image"
          src={place.image}
          alt={place.name}
          loading="lazy"
          onError={() => setImageFailed(true)}
        />
      ) : (
        <div className="place-image place-image-fallback">
          Photo unavailable
        </div>
      )}

      <div className="place-content">
        <h4>{place.name}</h4>
      </div>
    </article>
  );
}

export default function App() {
  const [selectedDistrictId, setSelectedDistrictId] = useState('D1');

  const selectedDistrict =
    districts.find((district) => district.id === selectedDistrictId) ??
    districts[0];

  function handleMapSelection(districtId) {
    const district = districts.find(
      (item) =>
        item.id.toUpperCase() === String(districtId).toUpperCase()
    );

    if (district) {
      setSelectedDistrictId(district.id);
    }
  }

  return (
    <main className="district-page">
      <header className="page-header">
        <p className="eyebrow">DUBLIN AREA GUIDE</p>
        <h1>Dublin District Profile</h1>
      </header>

      <section className="district-layout">
        <div className="map-card">
          <div className="section-heading">
            <div>
              <h2>Explore the map</h2>
              <p>Select a D1, D2 or D3 boundary.</p>
            </div>

            <span className="map-badge">Interactive map</span>
          </div>

          <DistrictMap
            selectedDistrict={selectedDistrict.id}
            onSelectDistrict={handleMapSelection}
          />
        </div>

        <div className="profile-card" key={selectedDistrict.id}>
          <div className="profile-heading">
            <div>
              <p className="eyebrow">DISTRICT PROFILE</p>
              <h2>{selectedDistrict.name}</h2>
            </div>

            <span className="district-pill">
              {selectedDistrict.id}
            </span>
          </div>

          <div className="profile-detail">
            <span>Average rent</span>
            <strong>{formatRent(selectedDistrict.rent)}</strong>
          </div>

          <section className="amenities-section">
            <h3>Available Amenities</h3>

            <div className="amenities-list">
              {amenityLabels.map(([key, label]) => {
                const value = selectedDistrict.amenities?.[key];

                return (
                  <div className="amenity-row" key={key}>
                    <span>{label}</span>
                    <strong>{formatValue(value)}</strong>
                  </div>
                );
              })}
            </div>
          </section>

          <section className="famous-places-section">
            <div className="section-heading">
              <h3>Famous Places</h3>

              <span className="place-count">
                {selectedDistrict.famousPlaces?.length ?? 0} places
              </span>
            </div>

            {selectedDistrict.famousPlaces?.length ? (
              <div className="places-list">
                {selectedDistrict.famousPlaces.map((place) => (
                  <FamousPlaceCard
                    key={place.name}
                    place={place}
                  />
                ))}
              </div>
            ) : (
              <p>No famous places available.</p>
            )}
          </section>
        </div>
      </section>
    </main>
  );
}
