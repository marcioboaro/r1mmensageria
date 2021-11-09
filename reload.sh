#!/bin/bash
git pull origin master
docker stop r1mmensageria_web_1
docker rm r1mmensageria_web_1
docker rmi r1mmensageria_web
docker-compose up -d