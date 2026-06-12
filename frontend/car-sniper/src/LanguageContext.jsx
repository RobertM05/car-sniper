import React, { createContext, useState, useContext } from 'react';

const translations = {
    ro: {
        nav: {
            browse: 'Caută',
            partnerNetwork: 'Dealeri Parteneri',
            partner: 'Devino Partener',
            account: 'Cont',
        },
        hero: {
            title: 'Mașini Premium. Performanță Excepțională.',
            subtitle: 'Găsește cele mai bune oferte din mii de anunțuri verificate de pe OLX și Autovit.',
        },
        search: {
            make: 'Marca',
            anyMake: 'Orice Marcă',
            model: 'Model',
            anyModel: 'Orice Model',
            minPrice: 'Preț Min (€)',
            maxPrice: 'Preț Max (€)',
            minYear: 'An Min',
            maxYear: 'An Max',
            maxKm: 'Km Max',
            limit: 'Limită Anunțuri',
            searchBtn: 'CAUTĂ',
            searching: 'Se caută...',
            advanced: 'Filtre Avansate ▾',
            fast: 'Rapid (50)',
            normal: 'Normal (100)',
            extended: 'Extins (300)',
            all: 'Maxim (Toate)',
            setAlert: 'Setează Alertă',
            selectMakeModel: 'Selectează Marca și Modelul',
        },
        results: {
            foundPrefix: 'Am găsit',
            foundSuffix: 'rezultate',
            sortPriceAsc: 'Preț (Crescător)',
            sortPriceDesc: 'Preț (Descrescător)',
            sortYearDesc: 'An (Cel mai nou)',
            sortYearAsc: 'An (Cel mai vechi)',
            sortKmAsc: 'Km (Cei mai puțini)',
            noResultsTitle: 'Nu am găsit nicio mașină',
            noResultsSubtitle: 'Încearcă să modifici filtrele pentru a vedea mai multe rezultate.',
        },
        card: {
            noTitle: 'Anunț fără titlu',
            priceOnRequest: 'Preț la cerere',
            viewAd: 'Vezi Anunț',
        },
        deal: {
            excellent: 'Excelent',
            good: 'Bun',
            fair: 'Corect',
            overpriced: 'Scump',
        },
        alert: {
            title: 'Setează Alertă de Preț',
            desc: 'Vei primi un email când apar mașini noi sub prețul selectat.',
            email: 'Emailul tău',
            maxPrice: 'Preț Maxim (€)',
            cancel: 'Anulează',
            save: 'Salvează Alerta',
        },
        stats: {
            title: 'Analiză Piață',
            avgPrice: 'Preț Mediu',
            avgYear: 'An Mediu',
            avgKm: 'Km Mediu',
            minPrice: 'Preț Minim',
            maxPrice: 'Preț Maxim',
            basedOn: 'bazat pe {count} anunțuri',
        },
        pagination: {
            prev: 'Anterior',
            next: 'Următor',
        },
        dealOfTheDay: {
            title: 'Ofertele Zilei',
            subtitle: 'Cele mai bune raporturi calitate-preț din ultimele 48 de ore',
            loading: 'Se încarcă cele mai bune oferte...',
        },
        footer: '© {year} CarSniper. Toate drepturile rezervate.',
        legal: {
            termsTitle: 'Termeni și Condiții',
            privacyTitle: 'Politica de Confidențialitate',
            termsContent: `
                <h2>1. Despre CarSniper</h2>
                <p>CarSniper funcționează ca un motor de căutare și agregator de anunțuri auto. Nu vindem mașini și nu intermediem tranzacții.</p>
                <h2>2. Răspunderea pentru Anunțuri</h2>
                <p>Conform Legii 365/2002 privind comerțul electronic și a Directivei e-Commerce (2000/31/CE), CarSniper are rolul exclusiv de furnizor de servicii de căutare. Nu suntem responsabili pentru corectitudinea datelor, kilometrajul, starea tehnică a vehiculelor sau eventualele fraude de pe platformele sursă (ex: OLX, Autovit). Toate achizițiile se fac pe riscul utilizatorului.</p>
                <h2>3. Drepturi de Autor și Web Scraping</h2>
                <p>Informațiile indexate provin din surse publice și sunt utilizate strict în scop informațional, conform excepțiilor privind "Text and Data Mining" (Directiva UE 2019/790). Mărcile înregistrate aparțin deținătorilor de drept.</p>
            `,
            privacyContent: `
                <h2>1. Colectarea Datelor</h2>
                <p>În conformitate cu Regulamentul GDPR (UE 2016/679) și Legea 190/2018, colectăm adresa ta de email și preferințele de căutare strict pentru a-ți trimite alerte de preț și a menține contul tău activ.</p>
                <h2>2. Stocarea și Securitatea</h2>
                <p>Datele sunt stocate în siguranță prin intermediul partenerului nostru de infrastructură (Supabase). Nu vindem datele tale către terți.</p>
                <h2>3. Drepturile Tale</h2>
                <p>Ai dreptul la acces, rectificare și "Dreptul de a fi uitat" (ștergerea completă a contului și a alertelor). Pentru a exercita aceste drepturi, ne poți contacta oricând.</p>
            `
        }
    },
    en: {
        nav: {
            browse: 'Browse',
            partnerNetwork: 'Partner Network',
            partner: 'Become a Partner',
            account: 'Account',
        },
        hero: {
            title: 'Luxury Cars. Curated for Performance.',
            subtitle: 'Explore the finest high-end vehicles globally via OLX and Autovit aggregations.',
        },
        search: {
            make: 'Make',
            anyMake: 'Any Make',
            model: 'Model',
            anyModel: 'Any Model',
            minPrice: 'Min Price (€)',
            maxPrice: 'Max Price (€)',
            minYear: 'Min Year',
            maxYear: 'Max Year',
            maxKm: 'Max Km',
            limit: 'Results Limit',
            searchBtn: 'SEARCH',
            searching: 'Searching...',
            advanced: 'Advanced Filters ▾',
            fast: 'Fast (50)',
            normal: 'Normal (100)',
            extended: 'Extended (300)',
            all: 'Max (All)',
            setAlert: 'Set Alert',
            selectMakeModel: 'Select Make and Model',
        },
        results: {
            foundPrefix: 'Found',
            foundSuffix: 'results',
            sortPriceAsc: 'Price (Ascending)',
            sortPriceDesc: 'Price (Descending)',
            sortYearDesc: 'Year (Newest)',
            sortYearAsc: 'Year (Oldest)',
            sortKmAsc: 'Km (Lowest)',
            noResultsTitle: 'No cars found',
            noResultsSubtitle: 'Try adjusting your filters to see more results.',
        },
        card: {
            noTitle: 'Untitled Ad',
            priceOnRequest: 'Price on request',
            viewAd: 'View Ad',
        },
        deal: {
            excellent: 'Excellent',
            good: 'Good',
            fair: 'Fair',
            overpriced: 'Overpriced',
        },
        alert: {
            title: 'Set Price Alert',
            desc: 'You will receive an email when new cars appear under the selected price.',
            email: 'Your email',
            maxPrice: 'Max Price (€)',
            cancel: 'Cancel',
            save: 'Save Alert',
        },
        stats: {
            title: 'Market Analysis',
            avgPrice: 'Avg Price',
            avgYear: 'Avg Year',
            avgKm: 'Avg Km',
            minPrice: 'Min Price',
            maxPrice: 'Max Price',
            basedOn: 'based on {count} listings',
        },
        pagination: {
            prev: 'Previous',
            next: 'Next',
        },
        dealOfTheDay: {
            title: 'Deals of the Day',
            subtitle: 'The best value-for-money listings from the last 48 hours',
            loading: 'Loading top deals...',
        },
        footer: '© {year} CarSniper. All rights reserved.',
        legal: {
            termsTitle: 'Terms and Conditions',
            privacyTitle: 'Privacy Policy',
            termsContent: `
                <h2>1. About CarSniper</h2>
                <p>CarSniper operates strictly as a search engine and aggregator for automotive listings. We do not sell cars nor intermediate transactions.</p>
                <h2>2. Liability for Listings</h2>
                <p>In accordance with the EU e-Commerce Directive (2000/31/EC) and national laws, CarSniper acts as an intermediary search service. We hold no liability for the accuracy of the listings, the condition of the vehicles, or potential scams originating from third-party platforms (e.g., OLX, Autovit). All purchases are made at the user's own risk.</p>
                <h2>3. Copyright and Web Scraping</h2>
                <p>The indexed information comes from publicly available sources and is used strictly for informational purposes, falling under the "Text and Data Mining" exception (EU Directive 2019/790). Trademarks belong to their respective owners.</p>
            `,
            privacyContent: `
                <h2>1. Data Collection</h2>
                <p>In compliance with the GDPR (EU 2016/679) and applicable national laws, we collect your email address and search preferences exclusively to provide you with price alerts and maintain your account.</p>
                <h2>2. Storage and Security</h2>
                <p>Your data is securely stored through our infrastructure partner (Supabase). We do not sell your personal data to third parties.</p>
                <h2>3. Your Rights</h2>
                <p>You have the right to access, rectify, and the "Right to be Forgotten" (complete account deletion). To exercise these rights, you may contact us at any time.</p>
            `
        }
    }
};

const LanguageContext = createContext();

export const LanguageProvider = ({ children }) => {
    const [lang, setLang] = useState('ro');

    const t = (section, key, params = {}) => {
        let text = translations[lang]?.[section]?.[key];
        if (!text) {
            const fallback = translations[lang]?.[section];
            text = typeof fallback === 'string' ? fallback : `${section}.${key}`;
        }

        if (typeof text === 'string') {
            Object.keys(params).forEach(param => {
                text = text.replace(`{${param}}`, params[param]);
            });
        }

        return text;
    };

    return (
        <LanguageContext.Provider value={{ lang, setLang, t }}>
            {children}
        </LanguageContext.Provider>
    );
};

export const useLanguage = () => useContext(LanguageContext);
