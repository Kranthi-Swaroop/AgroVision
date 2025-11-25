import { memo, useMemo } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useLanguage } from '../i18n'

const LINKS = [
  { path: '/', labelKey: 'nav.home', icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6' },
  { path: '/scan', labelKey: 'nav.scanner', icon: 'M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z M15 13a3 3 0 11-6 0 3 3 0 016 0z' },
  { path: '/drone', labelKey: 'nav.fieldMap', icon: 'M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7' },
  { path: '/chat', labelKey: 'nav.chat', icon: 'M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z' },
  { path: '/history', labelKey: 'nav.history', icon: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z' }
]

function Navbar() {
  const location = useLocation()
  const { t } = useLanguage()
  
  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-secondary border-t border-theme safe-bottom z-50">
      <div className="flex items-center justify-around h-14">
        {LINKS.map(link => (
          <Link
            key={link.path}
            to={link.path}
            className={`flex flex-col items-center justify-center flex-1 h-full py-1 ${
              location.pathname === link.path
                ? 'text-accent'
                : 'text-secondary-color'
            }`}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={link.icon} />
            </svg>
            <span className="text-[10px] mt-0.5 truncate max-w-[50px]">{t(link.labelKey)}</span>
          </Link>
        ))}
      </div>
    </nav>
  )
}

export default memo(Navbar)
