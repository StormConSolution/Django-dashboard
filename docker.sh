#!/bin/sh

# Publish to our dockerhub repo

docker build -f Dockerfile -t repustate/dashboard:new-latest .
docker push repustate/dashboard:new-latest
