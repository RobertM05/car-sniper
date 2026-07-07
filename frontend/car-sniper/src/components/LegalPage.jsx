import React from 'react';
import { useLanguage } from '../LanguageContext';
import { Helmet } from 'react-helmet-async';

const LegalPage = ({ type }) => {
    const { t } = useLanguage();
    
    const titleKey = type === 'terms' ? 'termsTitle' : 'privacyTitle';
    const contentKey = type === 'terms' ? 'termsContent' : 'privacyContent';
    
    const title = t('legal', titleKey);
    const content = t('legal', contentKey);

    return (
        <div className="container" style={{ marginTop: '40px', padding: '2rem', backgroundColor: 'var(--bg-secondary)', borderRadius: '12px' }}>
            <Helmet>
                <title>{title} | CarSniper</title>
                <meta name="description" content={title} />
            </Helmet>
            
            <h1 style={{ marginBottom: '2rem', color: 'var(--primary-color)' }}>{title}</h1>
            
            {/* Content sourced from hardcoded translations — trusted source */}
            <div 
                className="legal-content" 
                style={{ lineHeight: '1.8', color: 'var(--text-primary)' }}
                dangerouslySetInnerHTML={{ __html: content }} 
            />
            
        </div>
    );
};

export default LegalPage;
