/**
 * i18n Configuration
 * Supports Vietnamese (vi) and English (en)
 * Auto-detects browser language on first load
 */
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

import vi from './vi.json';
import en from './en.json';

i18n
  // Detect browser language
  .use(LanguageDetector)
  // Pass i18n instance to react-i18next
  .use(initReactI18next)
  .init({
    resources: {
      vi: { translation: vi },
      en: { translation: en },
    },
    // Default language
    fallbackLng: 'vi',
    // Languages supported
    supportedLngs: ['vi', 'en'],
    // Namespace
    defaultNS: 'translation',
    // Debug mode (disable in production)
    debug: process.env.NODE_ENV === 'development',
    interpolation: {
      // React already protects from XSS
      escapeValue: false,
    },
    detection: {
      // Detection order: localStorage → browser language
      order: ['localStorage', 'navigator'],
      // Persist selected language to localStorage
      caches: ['localStorage'],
      lookupLocalStorage: 'i18nextLng',
    },
  });

export default i18n;
