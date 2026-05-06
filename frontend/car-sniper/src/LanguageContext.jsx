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
        footer: '© {year} CarSniper. Toate drepturile rezervate.',
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
        footer: '© {year} CarSniper. All rights reserved.',
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
