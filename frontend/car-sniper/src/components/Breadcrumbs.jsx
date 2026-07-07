import React from 'react';
import { useLocation, Link, useParams } from 'react-router-dom';

const Breadcrumbs = () => {
    const location = useLocation();
    const { make, model, email: dealerEmail } = useParams();
    const path = location.pathname;

    const crumbs = [{ label: 'Home', href: '/' }];

    if (path.startsWith('/masini/') && make) {
        crumbs.push({ label: decodeURIComponent(make), href: '/masini/' + make });
        if (model) crumbs.push({ label: decodeURIComponent(model), href: path });
    } else if (path.startsWith('/dealer/') && dealerEmail) {
        crumbs.push({ label: decodeURIComponent(dealerEmail), href: path });
    } else if (path === '/partner-dashboard') {
        crumbs.push({ label: 'Partner Dashboard', href: path });
    } else if (path === '/alerts') {
        crumbs.push({ label: 'My Alerts', href: path });
    } else if (path === '/termeni') {
        crumbs.push({ label: 'Terms', href: path });
    } else if (path === '/confidentialitate') {
        crumbs.push({ label: 'Privacy', href: path });
    }

    if (crumbs.length <= 1) return null;

    return (
        <nav className="breadcrumbs" aria-label="Breadcrumb">
            {crumbs.map((crumb, i) => (
                <span key={crumb.href}>
                    {i > 0 && <span className="breadcrumb-sep">/</span>}
                    {i === crumbs.length - 1 ? (
                        <span className="breadcrumb-current">{crumb.label}</span>
                    ) : (
                        <Link to={crumb.href} className="breadcrumb-link">{crumb.label}</Link>
                    )}
                </span>
            ))}
        </nav>
    );
};

export default Breadcrumbs;
