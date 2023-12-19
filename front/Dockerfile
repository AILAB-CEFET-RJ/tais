FROM node:14-alpine as builder

WORKDIR /front_app

COPY package*.json ./

RUN npm install --force

COPY ./ .

RUN npm run build

EXPOSE 3000

CMD [ "npx", "serve", "build" ]

# Bundle static assets with nginx
# FROM nginx:1.21.0-alpine as production

# ENV NODE_ENV production
# Copy built assets from `builder` image
# COPY --from=builder /front_app/build /usr/share/nginx/html
# COPY nginx.conf /etc/nginx/conf.d/default.conf

# EXPOSE 3000

# CMD ["nginx", "-g", "daemon off;"]