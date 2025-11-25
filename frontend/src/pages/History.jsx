import { useState, useEffect, useCallback, memo, useMemo } from 'react'
import { motion } from 'framer-motion'
import { getOfflineHistory, getPendingCount, getOnlineStatus } from '../services/api'
import { useStore } from '../store/useStore'
import { useLanguage } from '../i18n'

const getRiskColor = (score) => {
  if (score >= 0.8) return 'bg-danger'
  if (score >= 0.6) return 'bg-orange-500'
  if (score >= 0.4) return 'bg-yellow-500'
  return 'bg-success'
}

const formatDate = (timestamp) => {
  const date = typeof timestamp === 'number' ? new Date(timestamp) : new Date(timestamp)
  return date.toLocaleDateString('en-IN', {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const RecordItem = memo(({ record, index, t }) => (
  <motion.div
    initial={{ opacity: 0, x: -20 }}
    animate={{ opacity: 1, x: 0 }}
    transition={{ delay: index * 0.05 }}
    className="bg-secondary p-4 rounded-xl"
  >
    <div className="flex items-start gap-3">
      <div className={`w-2 h-2 rounded-full mt-2 ${getRiskColor(record.risk_score || 0)}`} />
      <div className="flex-1 min-w-0">
        <h3 className="font-medium truncate">
          {record.display_name || record.disease?.replace(/_/g, ' ') || 'Unknown'}
        </h3>
        <p className="text-xs text-gray-500">
          {formatDate(record.timestamp || record.created_at)}
        </p>
        {record.remedy && (
          <p className="text-xs text-gray-400 mt-2 line-clamp-2">{record.remedy.spray}</p>
        )}
      </div>
      <div className="text-right">
        <div className="text-lg font-bold">{((record.confidence || 0) * 100).toFixed(0)}%</div>
        <div className="text-xs text-gray-500">{t('results.confidence')}</div>
      </div>
    </div>
  </motion.div>
))

const PendingItem = memo(({ record, index }) => (
  <motion.div
    initial={{ opacity: 0, x: -20 }}
    animate={{ opacity: 1, x: 0 }}
    transition={{ delay: index * 0.05 }}
    className="bg-yellow-500/10 border border-yellow-500/30 p-4 rounded-xl"
  >
    <div className="flex items-center gap-3">
      <div className="w-10 h-10 bg-yellow-500/20 rounded-lg flex items-center justify-center">
        <svg className="w-5 h-5 text-yellow-500 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
      <div className="flex-1">
        <p className="font-medium text-yellow-500">Pending Scan</p>
        <p className="text-xs text-gray-500">{formatDate(record.timestamp)}</p>
      </div>
    </div>
  </motion.div>
))

function History() {
  const { location, setLocation } = useStore()
  const { t, language } = useLanguage()
  const [records, setRecords] = useState([])
  const [pendingScans, setPendingScans] = useState([])
  const [loading, setLoading] = useState(false)
  const [pendingCount, setPendingCount] = useState(0)
  
  useEffect(() => {
    if (location || !navigator.geolocation) return
    navigator.geolocation.getCurrentPosition(
      (pos) => setLocation({ latitude: pos.coords.latitude, longitude: pos.coords.longitude }),
      () => setLocation({ latitude: 23.2599, longitude: 77.4126 })
    )
  }, [location, setLocation])
  
  const loadHistory = useCallback(async () => {
    setLoading(true)
    try {
      // Load from offline storage (IndexedDB)
      const offlineData = await getOfflineHistory(50)
      setRecords(offlineData)
      
      // Check pending count
      const pending = await getPendingCount()
      setPendingCount(pending)
    } catch (err) {
      console.error('Failed to load history:', err)
    }
    setLoading(false)
  }, [])
  
  useEffect(() => {
    loadHistory()
  }, [loadHistory])

  const noHistoryText = {
    en: "No scans yet",
    hi: "अभी तक कोई स्कैन नहीं",
    te: "ఇంకా స్కాన్‌లు లేవు",
    ta: "இன்னும் ஸ்கேன்கள் இல்லை",
    kn: "ಇನ್ನೂ ಸ್ಕ್ಯಾನ್‌ಗಳಿಲ್ಲ"
  }

  const startScanningText = {
    en: "Start scanning to build your history",
    hi: "अपना इतिहास बनाने के लिए स्कैनिंग शुरू करें",
    te: "మీ చరిత్రను నిర్మించడానికి స్కాన్ చేయడం ప్రారంభించండి",
    ta: "உங்கள் வரலாற்றை உருவாக்க ஸ்கேன் செய்யத் தொடங்குங்கள்",
    kn: "ನಿಮ್ಮ ಇತಿಹಾಸವನ್ನು ನಿರ್ಮಿಸಲು ಸ್ಕ್ಯಾನ್ ಮಾಡಲು ಪ್ರಾರಂಭಿಸಿ"
  }

  const pendingText = {
    en: `${pendingCount} scan${pendingCount > 1 ? 's' : ''} waiting to sync`,
    hi: `${pendingCount} स्कैन सिंक होने की प्रतीक्षा में`,
    te: `${pendingCount} స్కాన్‌లు సమకాలీకరణ కోసం వేచి ఉన్నాయి`,
    ta: `${pendingCount} ஸ்கேன்கள் ஒத்திசைக்க காத்திருக்கின்றன`,
    kn: `${pendingCount} ಸ್ಕ್ಯಾನ್‌ಗಳು ಸಿಂಕ್ ಮಾಡಲು ಕಾಯುತ್ತಿವೆ`
  }
  
  return (
    <div className="flex flex-col">
      <h1 className="text-xl font-bold mb-4">{t('history.title')}</h1>

      {/* Pending scans banner */}
      {pendingCount > 0 && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-4 p-3 bg-yellow-500/20 border border-yellow-500/30 rounded-xl flex items-center gap-3"
        >
          <svg className="w-5 h-5 text-yellow-500 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          <span className="text-sm text-yellow-500">
            {pendingText[language] || pendingText.en}
          </span>
        </motion.div>
      )}
      
      {loading && (
        <div className="flex items-center justify-center py-12">
          <div className="w-8 h-8 border-2 border-accent border-t-transparent rounded-full animate-spin" />
        </div>
      )}
      
      {!loading && records.length === 0 && pendingCount === 0 && (
        <div className="bg-secondary rounded-xl p-8 text-center">
          <svg className="w-16 h-16 text-secondary-color mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p className="text-secondary-color">{noHistoryText[language] || noHistoryText.en}</p>
          <p className="text-xs text-secondary-color mt-1">
            {startScanningText[language] || startScanningText.en}
          </p>
        </div>
      )}
      
      <div className="space-y-3">
        {records.map((record, index) => (
          <RecordItem key={record.id || index} record={record} index={index} t={t} />
        ))}
      </div>
    </div>
  )
}

export default memo(History)
