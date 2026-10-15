
export const districts = [
  {
    id: 'D1',
    name: 'North Inner City',
    rent:{
    oneBed: 1682.83,
  twoBed: 2262.23,
  },
    transport: null,
    amenities: {
      groceries: 49,
      restaurants: 124,
      asianRestaurants: 39,
      cafes: 114,
      gyms: 8,
      parks: 13,
      pharmacies: 19,
    },
    famousPlaces: [
      {
        name: "Ha'penny Bridge",
        description:
          'A well-known pedestrian bridge across the River Liffey in central Dublin.',
        image:
          "https://commons.wikimedia.org/wiki/Special:FilePath/Ha%27Penny_Bridge_in_Dublin%2C_Ireland.jpg?width=800",
        imageCredit: 'Photo: Chris Rycroft / Wikimedia Commons',
        sourceUrl:
          'https://commons.wikimedia.org/wiki/File:Ha%27Penny_Bridge_in_Dublin,_Ireland.jpg',
      },
      {
        name: 'River Liffey',
        description:
          'The river running through Dublin city, with walkways and bridges along the city centre.',
        image:
          "https://commons.wikimedia.org/wiki/Special:FilePath/Ha%27Penny_Bridge_in_Dublin%2C_Ireland.jpg?width=800",
        imageCredit: 'Photo: Chris Rycroft / Wikimedia Commons',
        sourceUrl:
          'https://commons.wikimedia.org/wiki/File:Ha%27Penny_Bridge_in_Dublin,_Ireland.jpg',
      },
    ],
  },
  {
    id: 'D2',
    name: 'South East Inner City',
   rent: {
  oneBed: 1796.44,
  twoBed: 2191.48,
},
    transport: null,
    amenities: {
      groceries: 48,
      restaurants: 292,
      asianRestaurants: 38,
      cafes: 202,
      gyms: 26,
      parks: 13,
      pharmacies: 14,
    },
    famousPlaces: [
      {
        name: 'Trinity College Dublin',
        description:
          'Historic university campus in the city centre, known for its architecture and cultural attractions.',
        image:
          'https://commons.wikimedia.org/wiki/Special:FilePath/Trinity_College_%28Dublin%29.JPG?width=800',
        imageCredit: 'Photo: Etiennekd / Wikimedia Commons',
        sourceUrl:
          'https://commons.wikimedia.org/wiki/File:Trinity_College_(Dublin).JPG',
      },
      {
        name: 'River Liffey and city bridges',
        description:
          'The River Liffey is a major feature of central Dublin, with pedestrian routes and bridges nearby.',
        image:
          "https://commons.wikimedia.org/wiki/Special:FilePath/Ha%27Penny_Bridge_in_Dublin%2C_Ireland.jpg?width=800",
        imageCredit: 'Photo: Chris Rycroft / Wikimedia Commons',
        sourceUrl:
          'https://commons.wikimedia.org/wiki/File:Ha%27Penny_Bridge_in_Dublin,_Ireland.jpg',
      },
    ],
  },
  {
    id: 'D3',
    name: 'Clontarf',
    rent: {
  oneBed: 1585.58,
  twoBed: 2133.86,
},
    transport: null,
    amenities: {
      groceries: 21,
      restaurants: 18,
      asianRestaurants: 4,
      cafes: 24,
      gyms: 18,
      parks: 37,
      pharmacies: 20,
    },
    famousPlaces: [
      {
        name: "St Anne's Park",
        description:
          'A large public park on Dublin’s northside, with walking routes, open green spaces and gardens.',
        image:
          "https://commons.wikimedia.org/wiki/Special:FilePath/St._Anne%27s_Park_-_Dublin.jpg?width=800",
        imageCredit: 'Photo: Wikimedia Commons',
        sourceUrl:
          "https://commons.wikimedia.org/wiki/File:St._Anne's_Park_-_Dublin.jpg",
      },
    ],
  },
];

const amenityKeys = [
  'groceries',
  'restaurants',
  'asianRestaurants',
  'cafes',
  'gyms',
  'parks',
  'pharmacies',
];

for (let number = 1; number <= 24; number++) {
  const id = `D${number}`;

  let district = districts.find((item) => item.id === id);

  if (!district) {
    district = {
      id,
      name: `Dublin ${number}`,
      rent: null,
      transport: null,
      amenities: {},
      famousPlaces: [],
    };

    districts.push(district);
  }

  district.amenities ??= {};

  amenityKeys.forEach((key) => {
    if (district.amenities[key] === undefined) {
      district.amenities[key] = null;
    }
  });

  district.famousPlaces ??= [];
}
