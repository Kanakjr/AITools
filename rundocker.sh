docker system prune -f
docker build -f "Dockerfile" -t newsgenius:latest "."
docker ps -q --filter "name=newsgenius" | xargs -I {} docker stop {}
sleep 5
docker run --rm -d -p 8501:8501/tcp --name newsgenius newsgenius