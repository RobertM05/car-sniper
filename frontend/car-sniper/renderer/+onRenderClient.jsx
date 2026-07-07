import ReactDOM from 'react-dom/client';
import { HelmetProvider } from 'react-helmet-async';
import { BrowserRouter } from 'react-router-dom';
import { LanguageProvider } from '../src/LanguageContext';
import '../src/index.css';

export default function onRenderClient(pageContext) {
    const { Page, pageProps } = pageContext;
    ReactDOM.hydrateRoot(
        document.getElementById('root'),
        <HelmetProvider>
            <BrowserRouter>
                <LanguageProvider>
                    <Page {...pageProps} />
                </LanguageProvider>
            </BrowserRouter>
        </HelmetProvider>
    );
}
