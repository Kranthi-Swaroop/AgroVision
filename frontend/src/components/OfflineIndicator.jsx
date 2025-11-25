import { memo, useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useLanguage } from '../i18n'
import { getPendingCount, syncPendingScans } from '../services/api'

function OfflineIndicator() {
  const [isOnline, setIsOnline] = useState(navigator.onLine)
  const [pendingCount, setPendingCount] = useState(0)
  const [showBanner, setShowBanner] = useState(false)
  const [syncing, setSyncing] = useState(false)
  const { t, language } = useLanguage()

  useEffect(() => {
    const handleOnline = async () => {
      setIsOnline(true)
      setShowBanner(true)
      
      // Auto-sync pending scans
      const pending = await getPendingCount()
      if (pending > 0) {
        setSyncing(true)
        await syncPendingScans()
        setSyncing(false)
        setPendingCount(0)
      }
      
      // Hide banner after 3 seconds
      setTimeout(() => setShowBanner(false), 3000)
    }

    const handleOffline = () => {
      setIsOnline(false)
      setShowBanner(true)
    }

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    // Check pending count on mount
    getPendingCount().then(setPendingCount)

    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [])

  // Update pending count periodically
  useEffect(() => {
    const interval = setInterval(async () => {
      const count = await getPendingCount()
      setPendingCount(count)
    }, 10000) // Every 10 seconds

    return () => clearInterval(interval)
  }, [])

  const offlineText = {
    en: "You're offline",
    hi: "आप ऑफ़लाइन हैं",
    te: "మీరు ఆఫ్‌లైన్‌లో ఉన్నారు",
    ta: "நீங்கள் ஆஃப்லைனில் உள்ளீர்கள்",
    kn: "ನೀವು ಆಫ್‌ಲೈನ್‌ನಲ್ಲಿದ್ದೀರಿ"
  }

  const onlineText = {
    en: "Back online!",
    hi: "वापस ऑनलाइन!",
    te: "తిరిగి ఆన్‌లైన్‌లో!",
    ta: "மீண்டும் ஆன்லைனில்!",
    kn: "ಮತ್ತೆ ಆನ್‌ಲೈನ್‌ನಲ್ಲಿ!"
  }

  const syncingText = {
    en: "Syncing your scans...",
    hi: "आपके स्कैन सिंक हो रहे हैं...",
    te: "మీ స్కాన్‌లను సమకాలీకరిస్తోంది...",
    ta: "உங்கள் ஸ்கேன்களை ஒத்திசைக்கிறது...",
    kn: "ನಿಮ್ಮ ಸ್ಕ್ಯಾನ್‌ಗಳನ್ನು ಸಿಂಕ್ ಮಾಡಲಾಗುತ್ತಿದೆ..."
  }

  const pendingText = {
    en: `${pendingCount} scan${pendingCount > 1 ? 's' : ''} pending`,
    hi: `${pendingCount} स्कैन लंबित`,
    te: `${pendingCount} స్కాన్‌లు పెండింగ్‌లో`,
    ta: `${pendingCount} ஸ்கேன்கள் நிலுவையில்`,
    kn: `${pendingCount} ಸ್ಕ್ಯಾನ್‌ಗಳು ಬಾಕಿ ಉಳಿದಿವೆ`
  }

  return (
    <>
      {/* Persistent offline indicator in corner */}
      <AnimatePresence>
        {!isOnline && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            className="fixed top-16 right-4 z-50 flex items-center gap-2 px-3 py-2 bg-yellow-500/90 text-black rounded-full text-xs font-medium shadow-lg"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 5.636a9 9 0 010 12.728m0 0l-2.829-2.829m2.829 2.829L21 21M15.536 8.464a5 5 0 010 7.072m0 0l-2.829-2.829m-4.243 2.829a4.978 4.978 0 01-1.414-2.83m-1.414 5.658a9 9 0 01-2.167-9.238m7.824 2.167a1 1 0 111.414 1.414m-1.414-1.414L3 3" />
            </svg>
            <span>Offline</span>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Pending scans indicator */}
      <AnimatePresence>
        {pendingCount > 0 && isOnline && !syncing && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="fixed top-16 right-4 z-50 flex items-center gap-2 px-3 py-2 bg-accent/90 text-primary rounded-full text-xs font-medium shadow-lg"
          >
            <svg className="w-4 h-4 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            <span>{pendingText[language] || pendingText.en}</span>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Banner notifications */}
      <AnimatePresence>
        {showBanner && (
          <motion.div
            initial={{ opacity: 0, y: -50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -50 }}
            className={`fixed top-0 left-0 right-0 z-[100] py-3 px-4 text-center text-sm font-medium ${
              isOnline 
                ? syncing 
                  ? 'bg-accent text-primary' 
                  : 'bg-success text-white'
                : 'bg-yellow-500 text-black'
            }`}
          >
            {isOnline 
              ? syncing 
                ? syncingText[language] || syncingText.en
                : onlineText[language] || onlineText.en
              : offlineText[language] || offlineText.en
            }
          </motion.div>
        )}
      </AnimatePresence>
    </>
  )
}

export default memo(OfflineIndicator)
