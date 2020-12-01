#!/bin/sh

# Publish to our dockerhub repo

docker build -f Dockerfile -t repustate/dashboard-nginx:latest .
docker push repustate/dashboard-nginx:latest
