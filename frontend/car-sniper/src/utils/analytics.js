import ReactGA from 'react-ga4';

const TRACKING_ID = import.meta.env.VITE_GA_TRACKING_ID || "G-XXXXXXXXXX"; // Replace with real GA4 Measurement ID in production

let isInitialized = false;

export const initGA = () => {
  if (!isInitialized && TRACKING_ID !== "G-XXXXXXXXXX") {
    ReactGA.initialize(TRACKING_ID);
    isInitialized = true;
  }
};

export const logPageView = (path) => {
  if (isInitialized) {
    ReactGA.send({ hitType: "pageview", page: path });
  }
};

export const logEvent = (category, action, label = null, value = null) => {
  if (isInitialized) {
    ReactGA.event({
      category: category,
      action: action,
      label: label,
      value: value
    });
  } else {
      console.log(`[Analytics Event] ${category} - ${action} - ${label} - ${value}`);
  }
};
