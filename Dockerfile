FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN apt update && apt install git -y && apt clean && sed -i pyproject.toml -e 's/.*ruamel.*//'
RUN pip install .
RUN pip install --no-deps ruamel.yaml
WORKDIR /deploy
RUN nebari init -p default -d example.com
CMD ["nebari", "deploy","-c", "/deploy/nebari-config.yaml"]
