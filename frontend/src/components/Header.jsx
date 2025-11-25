import { memo, useCallback, useMemo } from 'react'
import { useStore } from '../store/useStore'
import { useLanguage } from '../i18n'
import LanguageSelector from './LanguageSelector'

function Header() {
  const { theme, setTheme } = useStore()
  const { t } = useLanguage()
  
  const toggleTheme = useCallback(() => {
    const newTheme = theme === 'dark' ? 'light' : theme === 'light' ? 'system' : 'dark'
    setTheme(newTheme)
  }, [theme, setTheme])
  
  const isDark = useMemo(() => 
    theme === 'dark' || (theme === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches),
    [theme]
  )
  
  return (
    <header className="flex items-center justify-between px-4 py-3 safe-top">
      <span className="text-lg font-bold text-accent">{t('appName')}</span>
      <div className="flex items-center gap-2">
        <LanguageSelector />
        <button
          onClick={toggleTheme}
          className="w-10 h-10 flex items-center justify-center rounded-full bg-secondary border border-theme"
          aria-label={isDark ? t('common.lightMode') : t('common.darkMode')}
        >
          {theme === 'system' ? (
            <svg className="w-5 h-5 text-secondary-color" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
          ) : isDark ? (
            <svg className="w-5 h-5 text-secondary-color" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
            </svg>
          ) : (
            <svg className="w-5 h-5 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
          )}
        </button>
      </div>
    </header>
  )
}

export default memo(Header)
