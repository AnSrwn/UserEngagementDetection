# Nuxt 3 Minimal Starter

Look at the [Nuxt 3 documentation](https://nuxt.com/docs/getting-started/introduction) to learn more.

## Setup

Make sure to install the dependencies:

```bash
# yarn
yarn install

# npm
npm install

# pnpm
pnpm install
```

## Development Server

### Setup SSL
Install mkcert. Installation instructions can be found here: https://github.com/FiloSottile/mkcert   
Create certificates by running the following command in the frontend folder:   
```bash
mkcert localhost
```
Update `nuxt.config.ts`:
```bash
devServer: {
    https: {
      key: 'localhost-key.pem',
      cert: 'localhost.pem'
    }
  },
```
Use the following environment variable:
```bash
NODE_TLS_REJECT_UNAUTHORIZED=0
```

### Start Dev Server
Start the development server on `http://localhost:3000`

```bash
npm run dev
```

## Production

Build the application for production:

```bash
npm run build
```

Locally preview production build:

```bash
npm run preview
```

Check out the [deployment documentation](https://nuxt.com/docs/getting-started/deployment) for more information.
