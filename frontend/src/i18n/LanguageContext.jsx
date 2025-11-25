import { createContext, useContext, useState, useEffect, useCallback, useMemo } from 'react';
import { translations, languageNames, getTranslation } from './translations';

const LanguageContext = createContext(null);

// Supported languages
export const LANGUAGES = ['en', 'hi', 'te', 'ta', 'kn'];

// Default language
const DEFAULT_LANGUAGE = 'en';

// Storage key
const LANGUAGE_STORAGE_KEY = 'agrosentinel-language';

export function LanguageProvider({ children }) {
  const [language, setLanguageState] = useState(() => {
    // Try to get from localStorage
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem(LANGUAGE_STORAGE_KEY);
      if (stored && LANGUAGES.includes(stored)) {
        return stored;
      }
      // Try to detect browser language
      const browserLang = navigator.language?.split('-')[0];
      if (browserLang && LANGUAGES.includes(browserLang)) {
        return browserLang;
      }
    }
    return DEFAULT_LANGUAGE;
  });

  // Save language preference
  useEffect(() => {
    localStorage.setItem(LANGUAGE_STORAGE_KEY, language);
    // Update HTML lang attribute
    document.documentElement.lang = language;
  }, [language]);

  // Set language with validation
  const setLanguage = useCallback((lang) => {
    if (LANGUAGES.includes(lang)) {
      setLanguageState(lang);
    }
  }, []);

  // Translation function
  const t = useCallback((path, fallback) => {
    const result = getTranslation(language, path);
    return result || fallback || path;
  }, [language]);

  // Get current translations object
  const currentTranslations = useMemo(() => {
    return translations[language] || translations[DEFAULT_LANGUAGE];
  }, [language]);

  // Get language name
  const getLanguageName = useCallback((code) => {
    return languageNames[code] || code;
  }, []);

  const value = useMemo(() => ({
    language,
    setLanguage,
    t,
    translations: currentTranslations,
    languageNames,
    getLanguageName,
    availableLanguages: LANGUAGES,
  }), [language, setLanguage, t, currentTranslations, getLanguageName]);

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
}

// Custom hook for using language context
export function useLanguage() {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
}

// HOC for class components (if needed)
export function withLanguage(Component) {
  return function WrappedComponent(props) {
    const languageContext = useLanguage();
    return <Component {...props} {...languageContext} />;
  };
}

export default LanguageContext;
