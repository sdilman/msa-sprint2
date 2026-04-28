import { ApolloServer } from '@apollo/server';
import { startStandaloneServer } from '@apollo/server/standalone';
import { buildSubgraphSchema } from '@apollo/subgraph';
import gql from 'graphql-tag';
import * as grpc from '@grpc/grpc-js';
import * as protoLoader from '@grpc/proto-loader';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Load the booking.proto definition
const PROTO_PATH = path.join(__dirname, 'booking.proto');
const packageDefinition = protoLoader.loadSync(PROTO_PATH, {
  keepCase: false,
  longs: String,
  enums: String,
  defaults: true,
  oneofs: true,
});
const bookingProto = grpc.loadPackageDefinition(packageDefinition).booking;

// Create gRPC client for booking-service
const BOOKING_SERVICE_URL = process.env.BOOKING_SERVICE_URL || 'booking-service:9090';
const bookingClient = new bookingProto.BookingService(
  BOOKING_SERVICE_URL,
  grpc.credentials.createInsecure()
);

// Promisify gRPC calls
function listBookings(userId) {
  return new Promise((resolve, reject) => {
    bookingClient.ListBookings({ userId }, (err, response) => {
      if (err) {
        reject(err);
      } else {
        resolve(response);
      }
    });
  });
}

const typeDefs = gql`
  extend schema @link(url: "https://specs.apollo.dev/federation/v2.0", import: ["@key", "@external"])

  type Booking @key(fields: "id") {
    id: ID!
    userId: String!
    hotelId: String!
    hotel: Hotel
    promoCode: String
    discountPercent: Float
    price: Float
    createdAt: String
  }

  type Hotel @key(fields: "id", resolvable: false) {
    id: ID!
  }

  type Query {
    bookingsByUser(userId: String!): [Booking]
  }
`;

const resolvers = {
  Query: {
    bookingsByUser: async (_, { userId }, { req }) => {
      // ACL: check that the requesting user matches the userId
      const headerUserId = req.headers['userid'];
      if (!headerUserId || headerUserId !== userId) {
        return [];
      }

      try {
        const response = await listBookings(userId);
        return (response.bookings || []).map((b) => ({
          id: b.id,
          userId: b.userId,
          hotelId: b.hotelId,
          promoCode: b.promoCode || null,
          discountPercent: parseFloat(b.discountPercent) || 0,
          price: parseFloat(b.price) || 0,
          createdAt: b.createdAt || null,
        }));
      } catch (err) {
        console.error('gRPC ListBookings error:', err.message);
        return [];
      }
    },
  },
  Booking: {
    __resolveReference: async ({ id }) => {
      // Federation reference resolver — list all bookings and find by id
      // In a real system you'd have a GetBookingById RPC
      try {
        const response = await listBookings('');
        const booking = (response.bookings || []).find((b) => b.id === id);
        if (!booking) return null;
        return {
          id: booking.id,
          userId: booking.userId,
          hotelId: booking.hotelId,
          promoCode: booking.promoCode || null,
          discountPercent: parseFloat(booking.discountPercent) || 0,
          price: parseFloat(booking.price) || 0,
          createdAt: booking.createdAt || null,
        };
      } catch (err) {
        console.error('gRPC resolve reference error:', err.message);
        return null;
      }
    },
    hotel: (booking) => {
      // Return a Hotel reference for federation to resolve via hotel-subgraph
      if (!booking.hotelId) return null;
      return { __typename: 'Hotel', id: booking.hotelId };
    },
  },
};

const server = new ApolloServer({
  schema: buildSubgraphSchema([{ typeDefs, resolvers }]),
});

startStandaloneServer(server, {
  listen: { port: 4001 },
  context: async ({ req }) => ({ req }),
}).then(() => {
  console.log(`✅ Booking subgraph ready at http://localhost:4001/`);
  console.log(`   gRPC target: ${BOOKING_SERVICE_URL}`);
});
