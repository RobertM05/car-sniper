import ReactDOMServer from 'react-dom/server';
import { escapeInject, dangerouslySkipEscape } from 'vike/server';
import { HelmetProvider } from 'react-helmet-async';
import { LanguageProvider } from '../src/LanguageContext';
import '../src/index.css';

export default function onRenderHtml(pageContext) {
    const { Page, pageProps } = pageContext;
    const helmetContext = {};

    const html = ReactDOMServer.renderToString(
        <HelmetProvider context={helmetContext}>
            <LanguageProvider>
                <Page {...pageProps} />
            </LanguageProvider>
        </HelmetProvider>
    );

    const { helmet } = helmetContext;

    return escapeInject`<!DOCTYPE html>
    <html lang="ro">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        ${dangerouslySkipEscape(helmet.title.toString())}
        ${dangerouslySkipEscape(helmet.meta.toString())}
        ${dangerouslySkipEscape(helmet.link.toString())}
        ${dangerouslySkipEscape(helmet.script.toString())}
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    </head>
    <body>
        <div id="root">${dangerouslySkipEscape(html)}</div>
    </body>
    </html>`;
}
