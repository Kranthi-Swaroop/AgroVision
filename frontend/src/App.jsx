import { useEffect, lazy, Suspense } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Header from './components/Header'
import OfflineIndicator from './components/OfflineIndicator'
import { useStore } from './store/useStore'
import { LanguageProvider } from './i18n'

const Home = lazy(() => import('./pages/Home'))
const Scanner = lazy(() => import('./pages/Scanner'))
const History = lazy(() => import('./pages/History'))
const DroneView = lazy(() => import('./pages/DroneView'))
const ChatAssistant = lazy(() => import('./pages/ChatAssistant'))

const Loading = () => (
  <div className="flex items-center justify-center h-64">
    <div className="w-8 h-8 border-2 border-accent border-t-transparent rounded-full animate-spin" />
  </div>
)

// Register service worker
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js')
      .then((registration) => {
        console.log('[App] Service Worker registered:', registration.scope)
      })
      .catch((error) => {
        console.log('[App] Service Worker registration failed:', error)
      })
  })
}

export default function App() {
  const { theme } = useStore()
  
  useEffect(() => {
    const root = document.documentElement
    const applyTheme = (isDark) => {
      if (isDark) {
        root.classList.remove('light')
      } else {
        root.classList.add('light')
      }
      document.querySelector('meta[name="theme-color"]')?.setAttribute(
        'content', isDark ? '#121212' : '#ffffff'
      )
    }
    
    if (theme === 'system') {
      const media = window.matchMedia('(prefers-color-scheme: dark)')
      applyTheme(media.matches)
      const handler = (e) => applyTheme(e.matches)
      media.addEventListener('change', handler)
      return () => media.removeEventListener('change', handler)
    } else {
      applyTheme(theme === 'dark')
    }
  }, [theme])
  
  return (
    <LanguageProvider>
      <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <div className="min-h-[100dvh] bg-primary flex flex-col">
          <OfflineIndicator />
          <Header />
          <main className="flex-1 px-4 pb-20 overflow-y-auto">
            <Suspense fallback={<Loading />}>
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/scan" element={<Scanner />} />
                <Route path="/history" element={<History />} />
                <Route path="/drone" element={<DroneView />} />
                <Route path="/chat" element={<ChatAssistant />} />
              </Routes>
            </Suspense>
          </main>
          <Navbar />
        </div>
      </BrowserRouter>
    </LanguageProvider>
  )
}
