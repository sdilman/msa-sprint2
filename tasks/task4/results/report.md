# kubectl get pods + get services

```bash
stepandilman@Stepans-MBP-2 helm % kubectl get pods       
NAME                               READY   STATUS    RESTARTS   AGE
booking-service-79fdcc77b5-f7dmk   1/1     Running   0          10m
stepandilman@Stepans-MBP-2 helm % kubectl get services
NAME              TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)   AGE
booking-service   ClusterIP   10.108.50.127   <none>        80/TCP    24m
kubernetes        ClusterIP   10.96.0.1       <none>        443/TCP   4h36m
```

# Лог успешной сборки

```bash
stepandilman@Stepans-MBP-2 helm % helm upgrade --install booking-service ./booking-service \
  -f ./booking-service/values-stage.yaml
Release "booking-service" has been upgraded. Happy Helming!
NAME: booking-service
LAST DEPLOYED: Sun May  3 20:51:09 2026
NAMESPACE: default
STATUS: deployed
REVISION: 6
DESCRIPTION: Upgrade complete
TEST SUITE: None
```

# docker image ls + minikube image list

```bash
stepandilman@Stepans-MBP-2 helm % docker image ls
REPOSITORY                    TAG          IMAGE ID       CREATED          SIZE
booking-service               latest       d659a150a790   52 minutes ago   296MB
task3-apollo-gateway          latest       85dd2b9b0d37   9 hours ago      1.24GB
task3-hotel-subgraph          latest       3361d8a6e7e1   9 hours ago      1.15GB
task3-booking-subgraph        latest       be32ebb2e461   9 hours ago      1.16GB
task3-booking-service         latest       36e4781d82f2   9 hours ago      210MB
task3-monolith                latest       26c5316a5419   9 hours ago      517MB
postgres                      15           54778f8df51c   11 days ago      467MB
kong                          latest       257f61ecab8c   6 weeks ago      406MB
gcr.io/k8s-minikube/kicbase   v0.0.50      f3db27eba481   2 months ago     1.35GB
redis                         latest       5144e0a43b37   2 months ago     161MB
python                        3.9-slim     9a63e92e9041   6 months ago     147MB
python                        3.9-alpine   b449c492f8af   6 months ago     55.6MB
postgres                      13           26ece5aa4fc3   11 months ago    445MB
node                          18-alpine    c5914b9dd279   13 months ago    126MB
confluentinc/cp-kafka         7.2.1        6714825cefc3   3 years ago      801MB
confluentinc/cp-zookeeper     7.2.1        c289b1634998   3 years ago      801MB
stepandilman@Stepans-MBP-2 helm % minikube image ls
registry.k8s.io/pause:3.10.1
registry.k8s.io/kube-scheduler:v1.35.1
registry.k8s.io/kube-proxy:v1.35.1
registry.k8s.io/kube-controller-manager:v1.35.1
registry.k8s.io/kube-apiserver:v1.35.1
registry.k8s.io/etcd:3.6.6-0
registry.k8s.io/coredns/coredns:v1.13.1
gcr.io/k8s-minikube/storage-provisioner:v5
docker.io/library/booking-service:latest
```

# Скриншот успешного curl на /ping 

```bash
stepandilman@Stepans-MBP-2 helm % kubectl port-forward svc/booking-service 8081:80
Forwarding from 127.0.0.1:8081 -> 8080
Forwarding from [::1]:8081 -> 8080
Handling connection for 8081

stepandilman@Stepans-MBP-2 helm % curl http://localhost:8081/ping
pong%
```

# Скриншот успешного check-dns.sh

```bash
stepandilman@Stepans-MBP-2 task4 % . ./check-dns.sh
▶️ Running in-cluster DNS test...
pongpod "dns-test" deleted from default namespace
✅ Success
```

# Скриншот успешного check-dns.sh

```bash
stepandilman@Stepans-MBP-2 task4 % . ./check-status.sh
▶️ Checking booking-service deployment...
NAME                               READY   STATUS    RESTARTS   AGE
booking-service-79fdcc77b5-f7dmk   1/1     Running   0          27m

▶️ Checking service...
NAME              TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)   AGE
booking-service   ClusterIP   10.108.50.127   <none>        80/TCP    40m

▶️ Helm release:
booking-service	default  	6       	2026-05-03 20:51:09.935518 +0500 +05	deployed	booking-service-0.1.0	1.0        

▶️ Port-forward to test service locally:
  kubectl port-forward svc/booking-service 8081:80
  Then in another terminal:
    curl http://localhost:8081/ping

▶️ Quick curl (if port-forward already running):
pong✅ Reachable
```

# Локальная симуляция CI/CD

```bash
stepandilman@Stepans-MBP-2 task4 % gitlab-ci-local build test deploy
parsing and downloads finished in 26 ms.
json schema validated in 80 ms
build  starting shell (build)
build  $ docker build -t booking-service:latest -f booking-service/Dockerfile booking-service/
build  > #0 building with "desktop-linux" instance using docker driver
build  > 
build  > #1 [internal] load build definition from Dockerfile
build  > #1 transferring dockerfile: 729B done
build  > #1 DONE 0.0s
build  > 
build  > #2 [internal] load metadata for docker.io/library/golang:1.21-alpine
build  > #2 ...
build  > 
build  > #3 [auth] library/golang:pull token for registry-1.docker.io
build  > #3 DONE 0.0s
build  > 
build  > #2 [internal] load metadata for docker.io/library/golang:1.21-alpine
build  > #2 DONE 1.1s
build  > 
build  > #4 [internal] load .dockerignore
build  > #4 transferring context: 2B done
build  > #4 DONE 0.0s
build  > 
build  > #5 [1/6] FROM docker.io/library/golang:1.21-alpine@sha256:2414035b086e3c42b99654c8b26e6f5b1b1598080d65fd03c7f499552ff4dc94
build  > #5 DONE 0.0s
build  > 
build  > #6 [internal] load build context
build  > #6 transferring context: 29B done
build  > #6 DONE 0.0s
build  > 
build  > #7 [4/6] COPY main.go .
build  > #7 CACHED
build  > 
build  > #8 [5/6] RUN echo "module booking-service" > go.mod &&     echo "" >> go.mod &&     echo "go 1.21" >> go.mod
build  > #8 CACHED
build  > 
build  > #9 [3/6] WORKDIR /app
build  > #9 CACHED
build  > 
build  > #10 [2/6] RUN apk add --no-cache curl
build  > #10 CACHED
build  > 
build  > #11 [6/6] RUN go build -o booking-service main.go
build  > #11 CACHED
build  > 
build  > #12 exporting to image
build  > #12 exporting layers done
build  > #12 writing image sha256:d659a150a7906a2b33a35e0115562b6b8c2700c6e99f854f6f76b5cb19269a49 done
build  > #12 naming to docker.io/library/booking-service:latest done
build  > #12 DONE 0.0s
build  > 
build  > View build details: docker-desktop://dashboard/build/desktop-linux/desktop-linux/c20qweld465n6km4h8vcgqvub
build  $ minikube image load booking-service:latest
build  finished in 11 s
test   starting shell (test)
test   $ docker run --rm -d -p 8080:8080 --name test booking-service:latest
test   > 7b52351998e5ae5dd3fb58f0c0918d11645f35f06a812dd00fe85fbabba102b8
test   $ sleep 3
test   $ curl http://localhost:8080/ping | grep pong
test   >   % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
test   >                                  Dload  Upload   Total   Spent    Left  Speed
100     4  100     4    0     0   1263      0 --:--:-- --:--:-- --:--:--  1333
test   > pong
test   finished in 3.13 s
deploy starting shell (deploy)
deploy $ helm upgrade --install booking-service ./helm/booking-service -f ./helm/booking-service/values-stage.yaml
deploy > Release "booking-service" has been upgraded. Happy Helming!
deploy > NAME: booking-service
deploy > LAST DEPLOYED: Sun May  3 21:31:06 2026
deploy > NAMESPACE: default
deploy > STATUS: deployed
deploy > REVISION: 7
deploy > DESCRIPTION: Upgrade complete
deploy > TEST SUITE: None
deploy $ kubectl get pods
deploy > NAME                               READY   STATUS    RESTARTS   AGE
deploy > booking-service-79fdcc77b5-f7dmk   1/1     Running   0          39m
deploy finished in 210 ms

 PASS  build 
 PASS  test  
 PASS  deploy
```