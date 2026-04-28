import { ApolloServer } from '@apollo/server';
import { startStandaloneServer } from '@apollo/server/standalone';
import { buildSubgraphSchema } from '@apollo/subgraph';
import gql from 'graphql-tag';

const MONOLITH_URL = process.env.MONOLITH_URL || 'http://monolith:8080';

// Fetch hotel by ID from the monolith REST API
// Monolith Hotel entity fields: id, operational, fullyBooked, city, rating, description
async function fetchHotelById(id) {
  try {
    const response = await fetch(`${MONOLITH_URL}/api/hotels/${id}`);
    if (!response.ok) {
      console.error(`Hotel ${id} not found, status: ${response.status}`);
      return null;
    }
    const hotel = await response.json();
    return {
      id: hotel.id,
      name: hotel.description, //|| hotel.id,
      city: hotel.city, // || null,
      stars: hotel.rating ? Math.round(hotel.rating) : null,
    };
  } catch (err) {
    console.error(`Failed to fetch hotel ${id}:`, err.message);
    return null;
  }
}

const typeDefs = gql`
  extend schema @link(url: "https://specs.apollo.dev/federation/v2.0", import: ["@key"])

  type Hotel @key(fields: "id") {
    id: ID!
    name: String
    city: String
    stars: Int
  }

  type Query {
    hotelsByIds(ids: [ID!]!): [Hotel]
  }
`;

const resolvers = {
  Hotel: {
    __resolveReference: async ({ id }) => {
      // Called by federation when another subgraph references a Hotel by id
      return await fetchHotelById(id);
    },
  },
  Query: {
    hotelsByIds: async (_, { ids }) => {
      const results = await Promise.all(ids.map((id) => fetchHotelById(id)));
      return results.filter(Boolean);
    },
  },
};

const server = new ApolloServer({
  schema: buildSubgraphSchema([{ typeDefs, resolvers }]),
});

startStandaloneServer(server, {
  listen: { port: 4002 },
}).then(() => {
  console.log(`✅ Hotel subgraph ready at http://localhost:4002/`);
  console.log(`   Monolith URL: ${MONOLITH_URL}`);
});
