// Offline-aware API service
import axios from 'axios'
import { offlineStorage } from './offlineStorage'

const API_BASE = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000
})

// Track online status
let isOnline = navigator.onLine

window.addEventListener('online', () => {
  isOnline = true
  console.log('[API] Back online')
  // Trigger sync of pending scans
  syncPendingScans()
})

window.addEventListener('offline', () => {
  isOnline = false
  console.log('[API] Gone offline')
})

// Get current online status
export const getOnlineStatus = () => isOnline

const handleError = (err) => {
  if (err.code === 'ERR_NETWORK' || !isOnline) {
    throw new Error('offline')
  }
  if (err.response?.status === 500) {
    throw new Error('Server error. Please try again later.')
  }
  throw err
}

// Get current language from localStorage
const getLanguage = () => localStorage.getItem('agrosentinel-language') || 'en'

export const predictDisease = async (file) => {
  if (!isOnline) {
    throw new Error('offline')
  }
  
  try {
    const formData = new FormData()
    formData.append('file', file)
    const lang = getLanguage()
    const response = await api.post(`/predict?lang=${lang}`, formData)
    return response.data
  } catch (err) {
    handleError(err)
  }
}

export const analyzeWithRisk = async (file, latitude, longitude) => {
  // Try online first
  if (isOnline) {
    try {
      const formData = new FormData()
      formData.append('file', file)
      const lang = getLanguage()
      const response = await api.post(`/analyze?latitude=${latitude}&longitude=${longitude}&lang=${lang}`, formData)
      
      // Save successful scan to offline storage
      await offlineStorage.saveScan({
        ...response.data,
        latitude,
        longitude
      })
      
      return response.data
    } catch (err) {
      if (err.code !== 'ERR_NETWORK') {
        handleError(err)
      }
      // Fall through to offline handling
    }
  }
  
  // Offline mode - save for later
  console.log('[API] Saving scan for offline processing')
  await offlineStorage.savePendingScan(file, { latitude, longitude })
  
  return {
    offline: true,
    message: 'Scan saved! It will be analyzed when you reconnect.',
    pending: true
  }
}

export const getWeather = async (latitude, longitude) => {
  const cacheKey = `weather_${latitude.toFixed(2)}_${longitude.toFixed(2)}`
  
  // Try cache first if offline
  if (!isOnline) {
    const cached = await offlineStorage.getCachedResponse(cacheKey, 1800000) // 30 min cache
    if (cached) {
      return { ...cached, cached: true }
    }
    throw new Error('offline')
  }
  
  try {
    const response = await api.get(`/weather?latitude=${latitude}&longitude=${longitude}`)
    // Cache the response
    await offlineStorage.cacheApiResponse(cacheKey, response.data)
    return response.data
  } catch (err) {
    // Try cache on error
    const cached = await offlineStorage.getCachedResponse(cacheKey, 3600000) // 1 hour on error
    if (cached) {
      return { ...cached, cached: true }
    }
    handleError(err)
  }
}

export const getSupportedLanguages = async () => {
  const cacheKey = 'languages'
  
  if (!isOnline) {
    const cached = await offlineStorage.getCachedResponse(cacheKey)
    if (cached) return cached
    // Return default languages if offline
    return ['en', 'hi', 'te', 'ta', 'kn']
  }
  
  try {
    const response = await api.get('/languages')
    await offlineStorage.cacheApiResponse(cacheKey, response.data.languages)
    return response.data.languages
  } catch (err) {
    const cached = await offlineStorage.getCachedResponse(cacheKey)
    if (cached) return cached
    return ['en', 'hi', 'te', 'ta', 'kn']
  }
}

// Sync pending scans when back online
export const syncPendingScans = async () => {
  if (!isOnline) return { synced: 0, failed: 0 }
  
  const pending = await offlineStorage.getPendingScans()
  if (pending.length === 0) return { synced: 0, failed: 0 }
  
  console.log(`[API] Syncing ${pending.length} pending scans...`)
  
  let synced = 0
  let failed = 0
  
  for (const scan of pending) {
    try {
      // Convert base64 back to blob
      const response = await fetch(scan.imageData)
      const blob = await response.blob()
      const file = new File([blob], 'offline-scan.jpg', { type: 'image/jpeg' })
      
      // Upload
      const formData = new FormData()
      formData.append('file', file)
      const lang = getLanguage()
      const result = await api.post(
        `/analyze?latitude=${scan.location.latitude}&longitude=${scan.location.longitude}&lang=${lang}`,
        formData
      )
      
      // Save result and remove from pending
      await offlineStorage.saveScan({
        ...result.data,
        latitude: scan.location.latitude,
        longitude: scan.location.longitude,
        originalTimestamp: scan.timestamp
      })
      await offlineStorage.removePendingScan(scan.id)
      synced++
    } catch (err) {
      console.error('[API] Failed to sync scan:', err)
      failed++
    }
  }
  
  console.log(`[API] Sync complete: ${synced} synced, ${failed} failed`)
  return { synced, failed }
}

// Get offline history
export const getOfflineHistory = async (limit = 50) => {
  return offlineStorage.getScans(limit)
}

// Get pending count
export const getPendingCount = async () => {
  return offlineStorage.getPendingCount()
}

// Get location history (server-side, with offline fallback)
export const getLocationHistory = async (latitude, longitude) => {
  if (!isOnline) {
    // Return offline history when offline
    return getOfflineHistory(50)
  }
  
  try {
    const response = await api.get(`/history/location?latitude=${latitude}&longitude=${longitude}`)
    return response.data
  } catch (err) {
    // Return offline history on error
    return getOfflineHistory(50)
  }
}

export const getRemedy = async (disease) => {
  try {
    const response = await api.get(`/remedies/${encodeURIComponent(disease)}`)
    return response.data
  } catch (err) {
    return null
  }
}

// Chat Assistant API
export const sendChatMessage = async (message, language = 'en', sessionId = null) => {
  try {
    const response = await api.post('/chat/send', {
      message,
      language,
      session_id: sessionId
    })
    return response.data
  } catch (err) {
    console.error('[API] Chat error:', err)
    // Return a fallback response if offline or error
    return {
      response: language === 'hi' 
        ? 'क्षमा करें, मैं अभी उपलब्ध नहीं हूं। कृपया बाद में प्रयास करें।'
        : language === 'te'
        ? 'క్షమించండి, నేను ప్రస్తుతం అందుబాటులో లేను. దయచేసి తర్వాత ప్రయత్నించండి.'
        : language === 'ta'
        ? 'மன்னிக்கவும், நான் தற்போது கிடைக்கவில்லை. பின்னர் முயற்சிக்கவும்.'
        : language === 'kn'
        ? 'ಕ್ಷಮಿಸಿ, ನಾನು ಪ್ರಸ್ತುತ ಲಭ್ಯವಿಲ್ಲ. ದಯವಿಟ್ಟು ನಂತರ ಪ್ರಯತ್ನಿಸಿ.'
        : 'Sorry, I am currently unavailable. Please try again later.',
      suggestions: [],
      intent: 'error',
      language,
      timestamp: new Date().toISOString()
    }
  }
}

export const getQuickQuestions = async (language = 'en') => {
  try {
    const response = await api.get(`/chat/quick-questions?language=${language}`)
    return response.data
  } catch (err) {
    console.error('[API] Quick questions error:', err)
    return { questions: [], language }
  }
}

export const getChatSuggestions = async (language = 'en') => {
  try {
    const response = await api.get(`/chat/suggestions?language=${language}`)
    return response.data
  } catch (err) {
    return { suggestions: [], language }
  }
}
