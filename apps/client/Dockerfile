ARG PNPM_VERSION=10.14.0

# dev
FROM docker.io/node:22.17.1-slim AS dev

WORKDIR /app

RUN npm install --ignore-scripts --location=global pnpm@${PNPM_VERSION}
COPY ./package.json ./
RUN pnpm install --ignore-scripts
COPY . .

CMD ["pnpm", "run", "dev"]

# build
FROM dev AS build

RUN pnpm run build


# prod
FROM docker.io/nginxinc/nginx-unprivileged:1.28.0-alpine AS prod

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx/50x.html /usr/share/nginx/html
COPY nginx/40x.html /usr/share/nginx/html
COPY nginx/default.conf /etc/nginx/conf.d/default.conf

EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://127.0.0.1:8080/ || exit 1
CMD ["nginx", "-g", "daemon off;"]
