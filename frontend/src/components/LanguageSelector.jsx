import { memo, useState, useCallback, useRef, useEffect } from 'react'
import { useLanguage } from '../i18n'

function LanguageSelector() {
  const { language, setLanguage, availableLanguages, getLanguageName } = useLanguage()
  const [isOpen, setIsOpen] = useState(false)
  const dropdownRef = useRef(null)

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleSelect = useCallback((lang) => {
    setLanguage(lang)
    setIsOpen(false)
  }, [setLanguage])

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-1 px-3 py-2 rounded-lg bg-secondary border border-theme text-sm font-medium hover:bg-primary transition-colors"
        aria-label="Select language"
      >
        <svg className="w-4 h-4 text-secondary-color" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129" />
        </svg>
        <span className="hidden sm:inline">{getLanguageName(language)}</span>
        <span className="sm:hidden">{language.toUpperCase()}</span>
        <svg className={`w-3 h-3 transition-transform ${isOpen ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-40 bg-secondary rounded-xl border border-theme shadow-lg overflow-hidden z-50">
          {availableLanguages.map((lang) => (
            <button
              key={lang}
              onClick={() => handleSelect(lang)}
              className={`w-full px-4 py-3 text-left text-sm hover:bg-primary transition-colors flex items-center justify-between ${
                language === lang ? 'text-accent bg-accent/10' : 'text-secondary-color'
              }`}
            >
              <span>{getLanguageName(lang)}</span>
              {language === lang && (
                <svg className="w-4 h-4 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}

export default memo(LanguageSelector)
