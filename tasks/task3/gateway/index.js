import { ApolloServer } from '@apollo/server';
import { startStandaloneServer } from '@apollo/server/standalone';
import { ApolloGateway, IntrospectAndCompose, RemoteGraphQLDataSource } from '@apollo/gateway';

// Custom data source that forwards headers from the client request to subgraphs
class AuthenticatedDataSource extends RemoteGraphQLDataSource {
  willSendRequest({ request, context }) {
    // Forward the userid header for ACL checks in subgraphs
    if (context.userid) {
      request.http.headers.set('userid', context.userid);
    }
  }
}

const gateway = new ApolloGateway({
  supergraphSdl: new IntrospectAndCompose({
    subgraphs: [
      { name: 'booking', url: 'http://booking-subgraph:4001' },
      { name: 'hotel', url: 'http://hotel-subgraph:4002' },
    ],
  }),
  buildService({ url }) {
    return new AuthenticatedDataSource({ url });
  },
});

const server = new ApolloServer({ gateway });

startStandaloneServer(server, {
  listen: { port: 4000 },
  context: async ({ req }) => ({
    // Extract userid header and pass it through context
    userid: req.headers['userid'] || '',
  }),
}).then(({ url }) => {
  console.log(`🚀 Gateway ready at ${url}`);
});
