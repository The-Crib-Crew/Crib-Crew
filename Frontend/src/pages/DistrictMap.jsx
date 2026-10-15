
import { useEffect, useRef } from 'react';
import * as maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { districts } from './districtData';
import maplibreWorkerUrl from 'maplibre-gl/dist/maplibre-gl-worker.mjs?url';
import proj4 from 'proj4';

maplibregl.setWorkerUrl(maplibreWorkerUrl);

const MAP_STYLE = 'https://tiles.openfreemap.org/styles/liberty';

const DISTRICT_IDS = Array.from(
  { length: 24 },
  (_, index) => `D${index + 1}`
);

const LANDMARK_LOCATIONS = {
  "Ha'penny Bridge": [-6.2675, 53.3468],
  'River Liffey': [-6.2605, 53.3475],
  'River Liffey and city bridges': [-6.2605, 53.3475],
  'Trinity College Dublin': [-6.2546, 53.3438],
  "St Anne's Park": [-6.1785, 53.3737],
};

function districtIdFromPostcode(value) {
  const match = String(value ?? '')
    .trim()
    .match(/^Dublin\s*(\d{1,2})$/i);

  return match ? `D${match[1]}` : '';
}

function convertCoordinates(coordinates) {
  if (
    Array.isArray(coordinates) &&
    coordinates.length >= 2 &&
    typeof coordinates[0] === 'number' &&
    typeof coordinates[1] === 'number'
  ) {
    return proj4('EPSG:2157', 'EPSG:4326', coordinates);
  }

  return coordinates.map(convertCoordinates);
}

function getGeometryBounds(geometry) {
  const bounds = new maplibregl.LngLatBounds();

  function walk(coordinates) {
    if (
      Array.isArray(coordinates) &&
      coordinates.length >= 2 &&
      typeof coordinates[0] === 'number' &&
      typeof coordinates[1] === 'number'
    ) {
      bounds.extend(coordinates);
      return;
    }

    if (Array.isArray(coordinates)) {
      coordinates.forEach(walk);
    }
  }

  if (geometry?.coordinates) {
    walk(geometry.coordinates);
  }

  return bounds.isEmpty() ? null : bounds;
}

function addBuildingLayer(map) {
  const buildingLayer = map.getStyle().layers?.find(
    (layer) =>
      layer['source-layer'] === 'building' &&
      layer.source &&
      layer.type === 'fill'
  );

  if (!buildingLayer || map.getLayer('district-3d-buildings')) {
    return;
  }

  const labelLayer = map.getStyle().layers?.find(
    (layer) =>
      layer.type === 'symbol' &&
      layer.layout?.['text-field']
  );

  map.addLayer(
    {
      id: 'district-3d-buildings',
      source: buildingLayer.source,
      'source-layer': buildingLayer['source-layer'],
      type: 'fill-extrusion',
      minzoom: 14,
      paint: {
        'fill-extrusion-color': '#b9d8ca',
        'fill-extrusion-height': [
          'interpolate',
          ['linear'],
          ['zoom'],
          14,
          0,
          15,
          ['coalesce', ['get', 'render_height'], ['get', 'height'], 8],
        ],
        'fill-extrusion-base': [
          'coalesce',
          ['get', 'render_min_height'],
          ['get', 'min_height'],
          0,
        ],
        'fill-extrusion-opacity': 0.9,
      },
    },
    labelLayer?.id
  );
}

function createPopupContent(place) {
  const container = document.createElement('div');
  container.className = 'landmark-popup';

  const image = document.createElement('img');
  image.className = 'landmark-popup-image';
  image.src = place.image;
  image.alt = place.name;

  image.onerror = () => {
    image.style.display = 'none';
  };

  const title = document.createElement('h3');
  title.textContent = place.name;

  const description = document.createElement('p');
  description.textContent = place.description;

  const link = document.createElement('a');
  link.href = place.sourceUrl;
  link.target = '_blank';
  link.rel = 'noreferrer';
  link.textContent = 'View photo source';

  container.append(image, title, description, link);

  return container;
}

export default function DistrictMap({
  selectedDistrict,
  onSelectDistrict,
}) {
  const mapContainerRef = useRef(null);
  const mapRef = useRef(null);
  const selectedDistrictRef = useRef(selectedDistrict);
  const onSelectDistrictRef = useRef(onSelectDistrict);

  useEffect(() => {
    selectedDistrictRef.current = selectedDistrict;
  }, [selectedDistrict]);

  useEffect(() => {
    onSelectDistrictRef.current = onSelectDistrict;
  }, [onSelectDistrict]);

  useEffect(() => {
    if (!mapContainerRef.current || mapRef.current) return;

    let cancelled = false;
    let map;

    async function initialiseMap() {
      try {
        proj4.defs(
          'EPSG:2157',
          '+proj=tmerc +lat_0=53.5 +lon_0=-8 +k=0.99982 ' +
            '+x_0=600000 +y_0=750000 +ellps=GRS80 +units=m +no_defs'
        );

        const response = await fetch(
          '/data/dublin_postcode_boundaries.geojson'
        );

        if (!response.ok) {
          throw new Error(
            `Boundary file request failed (${response.status})`
          );
        }

        const rawGeoJSON = await response.json();

        if (!rawGeoJSON?.features?.length) {
          throw new Error('The boundary file contains no features.');
        }

        const geoJSON = {
          type: 'FeatureCollection',
          features: rawGeoJSON.features.map((feature) => ({
            ...feature,
            properties: {
              ...feature.properties,
              districtId: districtIdFromPostcode(
                feature.properties?.postcodes
              ),
            },
            geometry: {
              ...feature.geometry,
              coordinates: convertCoordinates(
                feature.geometry.coordinates
              ),
            },
          })),
        };

        if (cancelled || !mapContainerRef.current) return;

        map = new maplibregl.Map({
          container: mapContainerRef.current,
          style: MAP_STYLE,
          center: [-6.2603, 53.3498],
          zoom: 10.5,
          pitch: 45,
          bearing: -12,
          maxPitch: 70,
          attributionControl: true,
          canvasContextAttributes: {
            antialias: true,
          },
        });

        mapRef.current = map;

        map.addControl(
          new maplibregl.NavigationControl({
            visualizePitch: true,
          }),
          'top-right'
        );

        map.addControl(
          new maplibregl.FullscreenControl(),
          'top-right'
        );

        map.on('load', () => {
          if (cancelled) return;

          try {
            addBuildingLayer(map);

            map.addSource('dublin-districts', {
              type: 'geojson',
              data: geoJSON,
            });

            map.addLayer({
              id: 'district-fill',
              type: 'fill',
              source: 'dublin-districts',
              filter: [
                'in',
                ['get', 'districtId'],
                ['literal', DISTRICT_IDS],
              ],
              paint: {
                'fill-color': [
                  'case',
                  [
                    '==',
                    ['get', 'districtId'],
                    selectedDistrictRef.current,
                  ],
                  '#20c997',
                  '#83cbb0',
                ],
                'fill-opacity': [
                  'case',
                  [
                    '==',
                    ['get', 'districtId'],
                    selectedDistrictRef.current,
                  ],
                  0.55,
                  0.2,
                ],
                'fill-color-transition': {
                  duration: 350,
                  delay: 0,
                },
                'fill-opacity-transition': {
                  duration: 350,
                  delay: 0,
                },
              },
            });

            map.addLayer({
              id: 'district-outline',
              type: 'line',
              source: 'dublin-districts',
              filter: [
                'in',
                ['get', 'districtId'],
                ['literal', DISTRICT_IDS],
              ],
              paint: {
                'line-color': [
                  'case',
                  [
                    '==',
                    ['get', 'districtId'],
                    selectedDistrictRef.current,
                  ],
                  '#006b50',
                  '#47796b',
                ],
                'line-width': [
                  'case',
                  [
                    '==',
                    ['get', 'districtId'],
                    selectedDistrictRef.current,
                  ],
                  4,
                  1.5,
                ],
                'line-opacity-transition': {
                  duration: 350,
                  delay: 0,
                },
              },
            });

            // Add visible labels for districts where GeoJSON data exists.
            map.addLayer({
              id: 'district-labels',
              type: 'symbol',
              source: 'dublin-districts',
              filter: [
                'in',
                ['get', 'districtId'],
                ['literal', DISTRICT_IDS],
              ],
              layout: {
                'text-field': ['get', 'districtId'],
                'text-font': ['Open Sans Bold'],
                'text-size': [
                  'interpolate',
                  ['linear'],
                  ['zoom'],
                  9,
                  11,
                  13,
                  16,
                ],
                'text-allow-overlap': true,
                'text-ignore-placement': true,
              },
              paint: {
                'text-color': '#174b3a',
                'text-halo-color': '#ffffff',
                'text-halo-width': 2,
              },
            });

            map.on('click', 'district-fill', (event) => {
              const id = event.features?.[0]?.properties?.districtId;

              if (!DISTRICT_IDS.includes(id)) return;

              onSelectDistrictRef.current?.(id);

              const bounds = getGeometryBounds(
                event.features[0].geometry
              );

              if (bounds) {
                map.flyTo({
                  center: bounds.getCenter(),
                  zoom: 9.5,
                  pitch: 55,
                  bearing: -15,
                  duration: 1500,
                  essential: true,
                });
              }
            });

            map.on('mouseenter', 'district-fill', () => {
              map.getCanvas().style.cursor = 'pointer';
            });

            map.on('mouseleave', 'district-fill', () => {
              map.getCanvas().style.cursor = '';
            });

            // Add famous-place markers for existing district data.
            districts.forEach((district) => {
              if (!DISTRICT_IDS.includes(district.id)) return;

              (district.famousPlaces ?? []).forEach((place) => {
                const coordinates = LANDMARK_LOCATIONS[place.name];

                if (!coordinates) return;

                const markerElement = document.createElement('button');
                markerElement.type = 'button';
                markerElement.className = 'landmark-marker';
                markerElement.setAttribute('aria-label', place.name);
                markerElement.title = place.name;
                markerElement.textContent = '★';

                const popup = new maplibregl.Popup({
                  offset: 22,
                  closeButton: true,
                  maxWidth: '280px',
                }).setDOMContent(createPopupContent(place));

                const marker = new maplibregl.Marker({
                  element: markerElement,
                  anchor: 'bottom',
                })
                  .setLngLat(coordinates)
                  .setPopup(popup)
                  .addTo(map);

                markerElement.addEventListener('click', () => {
                  map.flyTo({
                    center: coordinates,
                    zoom: 9.5,
                    pitch: 55,
                    duration: 1400,
                    essential: true,
                  });
                });

                markerElement.style.display =
                  district.id === selectedDistrictRef.current
                    ? 'flex'
                    : 'none';

                markerElement.dataset.districtId = district.id;

                if (!map._districtLandmarkMarkers) {
                  map._districtLandmarkMarkers = [];
                }

                map._districtLandmarkMarkers.push(marker);
              });
            });

            // Animate into the full extent of available D1-D24 boundaries.
            const bounds = new maplibregl.LngLatBounds();

            geoJSON.features.forEach((feature) => {
              if (!DISTRICT_IDS.includes(feature.properties.districtId)) {
                return;
              }

              const featureBounds = getGeometryBounds(feature.geometry);

              if (featureBounds) {
                bounds.extend(featureBounds);
              }
            });

            if (!bounds.isEmpty()) {
              map.flyTo({
                center: bounds.getCenter(),
                zoom: 10.5,
                pitch: 45,
                bearing: -12,
                duration: 2200,
                essential: true,
              });
            }
          } catch (error) {
            console.error('Could not initialise district layers:', error);
          }
        });
      } catch (error) {
        console.error('Could not initialise the 3D map:', error);
      }
    }

    initialiseMap();

    return () => {
      cancelled = true;
      map?.remove();
      mapRef.current = null;
    };
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;

    function updateSelection() {
      if (!map.getLayer('district-fill')) return;

      map.setPaintProperty('district-fill', 'fill-color', [
        'case',
        ['==', ['get', 'districtId'], selectedDistrict],
        '#20c997',
        '#83cbb0',
      ]);

      map.setPaintProperty('district-fill', 'fill-opacity', [
        'case',
        ['==', ['get', 'districtId'], selectedDistrict],
        0.55,
        0.2,
      ]);

      map.setPaintProperty('district-outline', 'line-color', [
        'case',
        ['==', ['get', 'districtId'], selectedDistrict],
        '#006b50',
        '#47796b',
      ]);

      map.setPaintProperty('district-outline', 'line-width', [
        'case',
        ['==', ['get', 'districtId'], selectedDistrict],
        4,
        1.5,
      ]);

      map._districtLandmarkMarkers?.forEach((marker) => {
        marker.getElement().style.display =
          marker.getElement().dataset.districtId === selectedDistrict
            ? 'flex'
            : 'none';
      });
    }

    if (map.isStyleLoaded()) {
      updateSelection();
    } else {
      map.once('load', updateSelection);
    }
  }, [selectedDistrict]);

  return (
    <div className="district-map">
      <div
        ref={mapContainerRef}
        className="district-map-canvas"
        aria-label="Interactive 3D map of Dublin districts"
      />
    </div>
  );
}
