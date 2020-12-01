#!/bin/sh

# Publish to our dockerhub repo

docker build -f Dockerfile -t repustate/dashboard:latest .
docker push repustate/dashboard:latest
