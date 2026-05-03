Развернуты сервисы подготовленные в task-2 и сервися task-3 в едином docker compose

Данные в базе монолита и в базе микросервиса booking заполнены из `hotelio-monolith/init-fixtures.sql`

В графах Apollo Federation реализованы вызовы сервисов подготовленных в task-2

```sh
stepandilman@Stepans-MacBook-Pro-2 task3 % docker ps
CONTAINER ID   IMAGE                             COMMAND                  CREATED         STATUS                   PORTS                                        NAMES
f2d885fe43ce   task3-apollo-gateway              "docker-entrypoint.s…"   5 minutes ago   Up 5 minutes             0.0.0.0:4000->4000/tcp                       apollo-gateway-t3
7f403771069b   task3-booking-subgraph            "docker-entrypoint.s…"   5 minutes ago   Up 5 minutes             0.0.0.0:4001->4001/tcp                       booking-subgraph-t3
63819d13c771   task3-booking-service             "python -u server.py"    5 minutes ago   Up 5 minutes (healthy)   0.0.0.0:9090->9090/tcp                       booking-service-t3
a55509babb8a   task3-hotel-subgraph              "docker-entrypoint.s…"   5 minutes ago   Up 5 minutes             0.0.0.0:4002->4002/tcp                       hotel-subgraph-t3
33c3dfd7227d   confluentinc/cp-kafka:7.2.1       "/etc/confluent/dock…"   5 minutes ago   Up 5 minutes (healthy)   0.0.0.0:9092->9092/tcp                       task3-kafka-1
fb8631895a52   task3-monolith                    "java -jar app.jar"      5 minutes ago   Up 5 minutes             0.0.0.0:8084->8080/tcp                       hotelio-monolith-t3
b8f0c3ebe38d   postgres:15                       "docker-entrypoint.s…"   5 minutes ago   Up 5 minutes             0.0.0.0:5432->5432/tcp                       hotelio-db-t3
bdd7a49931fd   confluentinc/cp-zookeeper:7.2.1   "/etc/confluent/dock…"   5 minutes ago   Up 5 minutes (healthy)   2888/tcp, 0.0.0.0:2181->2181/tcp, 3888/tcp   task3-zookeeper-1
df74cc112b09   postgres:15                       "docker-entrypoint.s…"   5 minutes ago   Up 5 minutes             0.0.0.0:5433->5432/tcp                       booking-service-db-t3
stepandilman@Stepans-MacBook-Pro-2 task3 % 
```

```sh
stepandilman@Stepans-MacBook-Pro-2 task3 % docker logs 7f403771069b
Enabling inline tracing for this subgraph. To disable, use ApolloServerPluginInlineTraceDisabled.
✅ Booking subgraph ready at http://localhost:4001/
   gRPC target: booking-service:9090
```