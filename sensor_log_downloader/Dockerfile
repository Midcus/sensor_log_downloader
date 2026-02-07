FROM node:20-alpine AS tw
WORKDIR /build

COPY tailwind.config.js ./tailwind.config.js
COPY input.css ./input.css
COPY templates ./templates

RUN npm init -y \
  && npm install -D tailwindcss@3.4.17 \
  && npx tailwindcss@3.4.17 -i ./input.css -o ./tailwind.css --minify


FROM python:3.9-slim
WORKDIR /app

RUN pip install flask werkzeug gunicorn

COPY downloader.py .
COPY run.sh .
COPY templates/ ./templates/

RUN mkdir -p /app/static
COPY --from=tw /build/tailwind.css /app/static/tailwind.css

RUN chmod +x run.sh
CMD ["./run.sh"]
