#!/bin/bash

set -e

echo "▶️ Checking booking-service deployment..."
kubectl get pods -l app=booking-service

echo
echo "▶️ Checking service..."
kubectl get svc booking-service || echo "(No service found)"

echo
echo "▶️ Helm release:"
helm list | grep booking-service || echo "(No release found)"

echo
echo "▶️ Port-forward to test service locally:"
echo "  kubectl port-forward svc/booking-service 8081:80"
echo "  Then in another terminal:"
echo "    curl http://localhost:8081/ping"

echo
echo "▶️ Quick curl (if port-forward already running):"
curl --fail http://localhost:8081/ping && echo "✅ Reachable" || echo "❌ Not responding"
