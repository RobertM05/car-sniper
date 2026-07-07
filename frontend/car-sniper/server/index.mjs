import express from 'express';
import { renderPage } from 'vike/server';
import { createServer } from 'vite';

const isProduction = process.env.NODE_ENV === 'production';
const root = process.cwd();

async function startServer() {
    const app = express();

    if (isProduction) {
        app.use(express.static(`${root}/dist/client`));
    } else {
        const vite = await createServer({
            root,
            server: { middlewareMode: true },
        });
        app.use(vite.middlewares);
    }

    app.get('*', async (req, res, next) => {
        try {
            const pageContext = await renderPage({
                urlOriginal: req.originalUrl,
            });
            const { httpResponse } = pageContext;
            if (!httpResponse) return next();
            const { body, statusCode, headers } = httpResponse;
            headers.forEach((value, key) => res.setHeader(key, value));
            res.status(statusCode).send(body);
        } catch (e) {
            next(e);
        }
    });

    const port = process.env.PORT || 3000;
    app.listen(port, () => console.log(`Server running at http://localhost:${port}`));
}

startServer();
