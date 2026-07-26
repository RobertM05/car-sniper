import React, { createContext, useState, useContext, useCallback } from 'react';

const translations = {
    ro: {
        nav: {
            browse: 'Caută',
            partnerNetwork: 'Dealeri Parteneri',
            partner: 'Devino Partener',
            account: 'Cont',
            greeting: 'Salut, {email}',
            logout: 'Deconectare',
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
            advanced: 'Filtre Avansate',
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
            priceDrop: '{percent}% REDUCERE',
            viewDetails: 'Detalii',
        },
        deal: {
            excellent: 'Excelent',
            good: 'Bun',
            fair: 'Corect',
            overpriced: 'Scump',
            analysisTitle: 'AI Deal Analysis',
            cheaper: 'mai ieftin',
            moreExpensive: 'mai scump',
            savingsMessage: 'Economisesti ~{amount} fata de pretul mediu',
            viewDealAriaLabel: 'Vezi oferta: {title}',
        },
        auth: {
            titleLogin: 'Conectare',
            titleRegister: 'Inregistrare',
            subtitle: 'Intra in contul tau pentru a salva alerte si cautari.',
            emailLabel: 'Email',
            emailPlaceholder: 'nume@email.com',
            passwordLabel: 'Parola',
            passwordPlaceholder: 'Introdu parola',
            submitLogin: 'Conecteaza-te',
            submitRegister: 'Creeaza Cont',
            toggleToRegister: 'Nu ai cont? Inregistreaza-te',
            toggleToLogin: 'Ai deja cont? Conecteaza-te',
            loginSuccess: 'Conectare reusita!',
            registerSuccess: 'Cont creat cu succes!',
            errorDefault: 'A aparut o eroare. Incearca din nou.',
        },
        contact: {
            title: 'Devino Partener',
            subtitle: 'Completeaza formularul si te vom contacta in cel mai scurt timp.',
            nameLabel: 'Nume',
            namePlaceholder: 'Nume Prenume',
            phoneLabel: 'Telefon',
            phonePlaceholder: '07xx xxx xxx',
            emailLabel: 'Email',
            emailPlaceholder: 'nume@exemplu.com',
            companyLabel: 'Companie',
            companyPlaceholder: 'SC Exemplu SRL',
            websiteLabel: 'Website URL',
            websitePlaceholder: 'https://www.dealerulmeu.ro',
            hasWebsite: 'Am deja un website auto',
            submit: 'Trimite Cererea',
            success: 'Cererea a fost trimisa cu succes! Te vom contacta in curand.',
            error: 'A aparut o eroare. Incearca din nou.',
        },
        alert: {
            title: 'Setează Alertă de Preț',
            desc: 'Vei primi un email când apar mașini noi sub prețul selectat.',
            email: 'Emailul tău',
            maxPrice: 'Preț Maxim (€)',
            cancel: 'Anulează',
            save: 'Salvează Alerta',
            under: 'sub',
            saving: 'economisind',
            consentRequired: 'Trebuie să fii de acord cu Politica de Confidențialitate pentru a continua.',
            emailPlaceholder: 'nume@exemplu.com',
            consentText: 'Sunt de acord cu <a href="/confidentialitate" target="_blank" style="color: var(--primary-color)">Politica de Confidențialitate</a> și sunt de acord cu prelucrarea datelor mele pentru alertele prin email.',
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
        brands: {
            popularBrands: 'Marci populare',
        },
        alerts: {
            title: 'Alertele Mele',
            noAlerts: 'Nicio alerta',
            noAlertsDesc: 'Creeaza o alerta de pret din pagina de cautare.',
            delete: 'Sterge',
            created: 'Creata',
            myAlerts: 'Alertele mele',
        },
        trustStats: {
            carsMonitored: 'Masini monitorizate',
            avgSavings: 'Economie medie',
            listingsToday: 'Anunturi actualizate azi',
            refreshRate: 'Rata de actualizare',
        },
        footer: '© {year} Motorbit. Toate drepturile rezervate.',
        legal: {
            termsTitle: 'Termeni și Condiții',
            privacyTitle: 'Politica de Confidențialitate',
            termsContent: `
                <h2>1. Despre Motorbit</h2>
                <p>Motorbit funcționează ca un motor de căutare și agregator de anunțuri auto. Nu vindem mașini și nu intermediem tranzacții.</p>
                <h2>2. Răspunderea pentru Anunțuri</h2>
                <p>Conform Legii 365/2002 privind comerțul electronic și a Directivei e-Commerce (2000/31/CE), Motorbit are rolul exclusiv de furnizor de servicii de căutare. Nu suntem responsabili pentru corectitudinea datelor, kilometrajul, starea tehnică a vehiculelor sau eventualele fraude de pe platformele sursă (ex: OLX, Autovit). Toate achizițiile se fac pe riscul utilizatorului.</p>
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
        },
        filters: {
            any: 'Oricare',
            petrol: 'Benzina',
            diesel: 'Diesel',
            hybrid: 'Hibrid',
            electric: 'Electrica',
            automatic: 'Automata',
            manual: 'Manuala',
            price: 'Pret (EUR)',
            min: 'Min',
            max: 'Max',
            year: 'An fabricatie',
            from: 'Din',
            to: 'Pana',
            maxKm: 'Kilometraj maxim',
            fuel: 'Combustibil',
            transmission: 'Transmisie',
            source: 'Sursa',
            apply: 'Aplica filtre',
            clearAll: 'Reseteaza filtrele',
            verifiedPartner: 'Partener Verificat',
            filterButton: 'Filtre',
        },
        dashboard: {
            title: 'Dealer Intelligence',
            welcome: 'Bine ai revenit, Partener Verificat.',
            logout: 'Deconectare',
            totalUsers: 'Utilizatori Inregistrati',
            totalUsersDesc: 'Total utilizatori',
            activeAlerts: 'Alerte Active',
            activeAlertsDesc: 'Urmarire cereri utilizatori',
            marketScans: 'Anunturi Scanate',
            marketScansDesc: 'Masini indexate acum',
            demandChart: 'Cele mai cautate modele (Dupa cautari)',
            trendChart: 'Tendinta utilizatori activi',
            searchQueries: 'Cautari',
            activeBuyers: 'Utilizatori activi',
            actionTitle: 'Ai inventar compatibil?',
            actionDesc: 'Incarca masinile direct in baza noastra de date si sari peste scraper. Listarile tale vor aparea ca "Partener Verificat" in partea de sus a rezultatelor cautarii, ajungand direct la mii de cumparatori activi.',
            addInventory: 'Adauga Inventar',
            comingSoon: 'Functionalitatea de gestionare a inventarului va fi disponibila in curand.',
        },
    },
    en: {
        nav: {
            browse: 'Browse',
            partnerNetwork: 'Partner Network',
            partner: 'Become a Partner',
            account: 'Account',
            greeting: 'Hi, {email}',
            logout: 'Logout',
        },
        hero: {
            title: 'Find your car at the right price.',
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
            progressMessage: 'Searching OLX and Autovit... this may take up to 30 seconds.',
            advanced: 'Advanced Filters',
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
            priceDrop: '{percent}% PRICE DROP',
            viewDetails: 'Details',
        },
        deal: {
            excellent: 'Excellent',
            good: 'Good',
            fair: 'Fair',
            overpriced: 'Overpriced',
            analysisTitle: 'AI Deal Analysis',
            cheaper: 'cheaper',
            moreExpensive: 'more expensive',
            savingsMessage: 'You save ~{amount} vs market average',
            viewDealAriaLabel: 'View deal: {title}',
        },
        auth: {
            titleLogin: 'Sign In',
            titleRegister: 'Register',
            subtitle: 'Sign in to save alerts and searches.',
            emailLabel: 'Email',
            emailPlaceholder: 'name@email.com',
            passwordLabel: 'Password',
            passwordPlaceholder: 'Enter password',
            submitLogin: 'Sign In',
            submitRegister: 'Create Account',
            toggleToRegister: 'No account? Register',
            toggleToLogin: 'Already have an account? Sign In',
            loginSuccess: 'Login successful!',
            registerSuccess: 'Account created successfully!',
            errorDefault: 'An error occurred. Please try again.',
        },
        contact: {
            title: 'Become a Partner',
            subtitle: 'Fill out the form and we will contact you shortly.',
            nameLabel: 'Name',
            namePlaceholder: 'Full Name',
            phoneLabel: 'Phone',
            phonePlaceholder: '+40 7xx xxx xxx',
            emailLabel: 'Email',
            emailPlaceholder: 'name@example.com',
            companyLabel: 'Company',
            companyPlaceholder: 'Example SRL',
            websiteLabel: 'Website URL',
            websitePlaceholder: 'https://www.yourdealership.com',
            hasWebsite: 'I already have a car website',
            submit: 'Submit Request',
            success: 'Request submitted successfully! We will contact you soon.',
            error: 'An error occurred. Please try again.',
        },
        alert: {
            title: 'Set Price Alert',
            desc: 'You will receive an email when new cars appear under the selected price.',
            email: 'Your email',
            maxPrice: 'Max Price (€)',
            cancel: 'Cancel',
            save: 'Save Alert',
            under: 'under',
            saving: 'Saving',
            consentRequired: 'You must agree to the Privacy Policy to proceed.',
            emailPlaceholder: 'name@example.com',
            consentText: 'I agree to the <a href="/confidentialitate" target="_blank" style="color: var(--primary-color)">Privacy Policy</a> and consent to the processing of my data for email alerts.',
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
        brands: {
            popularBrands: 'Popular brands',
        },
        alerts: {
            title: 'My Alerts',
            noAlerts: 'No alerts yet',
            noAlertsDesc: 'Create a price alert from the search page.',
            delete: 'Delete',
            created: 'Created',
            myAlerts: 'My Alerts',
        },
        trustStats: {
            carsMonitored: 'Cars monitored',
            avgSavings: 'Average savings',
            listingsToday: 'Listings updated today',
            refreshRate: 'Refresh rate',
        },
        footer: '© {year} Motorbit. All rights reserved.',
        legal: {
            termsTitle: 'Terms and Conditions',
            privacyTitle: 'Privacy Policy',
            termsContent: `
                <h2>1. About Motorbit</h2>
                <p>Motorbit operates strictly as a search engine and aggregator for automotive listings. We do not sell cars nor intermediate transactions.</p>
                <h2>2. Liability for Listings</h2>
                <p>In accordance with the EU e-Commerce Directive (2000/31/EC) and national laws, Motorbit acts as an intermediary search service. We hold no liability for the accuracy of the listings, the condition of the vehicles, or potential scams originating from third-party platforms (e.g., OLX, Autovit). All purchases are made at the user's own risk.</p>
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
        },
        filters: {
            any: 'Any',
            petrol: 'Petrol',
            diesel: 'Diesel',
            hybrid: 'Hybrid',
            electric: 'Electric',
            automatic: 'Automatic',
            manual: 'Manual',
            price: 'Price (EUR)',
            min: 'Min',
            max: 'Max',
            year: 'Year',
            from: 'From',
            to: 'To',
            maxKm: 'Max mileage',
            fuel: 'Fuel',
            transmission: 'Transmission',
            source: 'Source',
            apply: 'Apply filters',
            clearAll: 'Clear all filters',
            verifiedPartner: 'Verified Partner',
            filterButton: 'Filters',
        },
    }
};

const LanguageContext = createContext();

export const LanguageProvider = ({ children }) => {
    const [lang, setLang] = useState('ro');

    const t = useCallback((section, key, params = {}) => {
        let text = translations[lang]?.[section]?.[key];
        if (!text) {
            const fallback = translations[lang]?.[section];
            text = typeof fallback === 'string' ? fallback : `${section}.${key || 'unknown'}`;
        }

        if (typeof text === 'string') {
            Object.keys(params).forEach(param => {
                text = text.replace(`{${param}}`, params[param]);
            });
        }

        return text;
    }, [lang]);

    return (
        <LanguageContext.Provider value={{ lang, setLang, t }}>
            {children}
        </LanguageContext.Provider>
    );
};

export const useLanguage = () => useContext(LanguageContext);
