import { useRef, useState, useCallback, useEffect, memo } from 'react'
import Webcam from 'react-webcam'
import { motion, AnimatePresence } from 'framer-motion'
import { analyzeWithRisk, getOnlineStatus } from '../services/api'
import { useStore } from '../store/useStore'
import ResultCard from '../components/ResultCard'
import { useLanguage } from '../i18n'

const videoConstraints = { facingMode: 'environment', aspectRatio: 3/4 }

function Scanner() {
  const webcamRef = useRef(null)
  const fileInputRef = useRef(null)
  const { result, loading, location, setResult, setLoading, setLocation, clearResult } = useStore()
  const [cameraError, setCameraError] = useState(null)
  const [error, setError] = useState(null)
  const [offlineSaved, setOfflineSaved] = useState(false)
  const { t, language } = useLanguage()
  
  useEffect(() => {
    if (!navigator.geolocation) {
      setLocation({ latitude: 23.2599, longitude: 77.4126 })
      return
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => setLocation({ latitude: pos.coords.latitude, longitude: pos.coords.longitude }),
      () => setLocation({ latitude: 23.2599, longitude: 77.4126 })
    )
  }, [setLocation])
  
  const processImage = useCallback(async (blob) => {
    if (!location) return
    setLoading(true)
    setError(null)
    setOfflineSaved(false)
    try {
      const file = new File([blob], 'capture.jpg', { type: 'image/jpeg' })
      const data = await analyzeWithRisk(file, location.latitude, location.longitude)
      
      // Check if this was an offline save
      if (data.offline) {
        setOfflineSaved(true)
        setResult(null)
      } else {
        setResult(data)
      }
    } catch (err) {
      if (err.message === 'offline') {
        setOfflineSaved(true)
      } else {
        setError(err.message || 'Failed to analyze image')
      }
    }
    setLoading(false)
  }, [location, setLoading, setResult])
  
  const captureImage = useCallback(async () => {
    if (!webcamRef.current) return
    const imageSrc = webcamRef.current.getScreenshot()
    if (!imageSrc) return
    const response = await fetch(imageSrc)
    const blob = await response.blob()
    processImage(blob)
  }, [processImage])
  
  const handleFileUpload = useCallback((e) => {
    const file = e.target.files?.[0]
    if (!file) return
    processImage(file)
    e.target.value = ''
  }, [processImage])
  
  const handleCameraError = useCallback(() => setCameraError(true), [])

  const offlineSavedText = {
    en: "Scan saved! It will be analyzed when you're back online.",
    hi: "स्कैन सहेजा गया! जब आप ऑनलाइन वापस आएंगे तो इसका विश्लेषण किया जाएगा।",
    te: "స్కాన్ సేవ్ చేయబడింది! మీరు తిరిగి ఆన్‌లైన్‌లో ఉన్నప్పుడు ఇది విశ్లేషించబడుతుంది.",
    ta: "ஸ்கேன் சேமிக்கப்பட்டது! நீங்கள் மீண்டும் ஆன்லைனில் இருக்கும்போது இது பகுப்பாய்வு செய்யப்படும்.",
    kn: "ಸ್ಕ್ಯಾನ್ ಉಳಿಸಲಾಗಿದೆ! ನೀವು ಮತ್ತೆ ಆನ್‌ಲೈನ್‌ನಲ್ಲಿರುವಾಗ ಇದನ್ನು ವಿಶ್ಲೇಷಿಸಲಾಗುತ್ತದೆ."
  }
  
  return (
    <div className="flex flex-col h-full">
      <div className="text-center mb-4">
        <h1 className="text-xl font-bold">{t('scanner.title')}</h1>
        {location && (
          <p className="text-xs text-gray-500 mt-1">
            {location.latitude.toFixed(4)}, {location.longitude.toFixed(4)}
          </p>
        )}
      </div>
      
      {error && (
        <div className="mb-4 p-3 bg-red-500/20 border border-red-500/50 rounded-lg text-sm text-center">
          {error}
        </div>
      )}

      {/* Offline saved notification */}
      <AnimatePresence>
        {offlineSaved && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="mb-4 p-4 bg-yellow-500/20 border border-yellow-500/50 rounded-xl text-sm"
          >
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-yellow-500/30 rounded-full flex items-center justify-center flex-shrink-0">
                <svg className="w-5 h-5 text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <p className="font-medium text-yellow-500">Offline Mode</p>
                <p className="text-secondary-color text-xs mt-1">
                  {offlineSavedText[language] || offlineSavedText.en}
                </p>
              </div>
              <button
                onClick={() => setOfflineSaved(false)}
                className="ml-auto text-secondary-color hover:text-primary"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
      
      <div className="flex-1 relative rounded-2xl overflow-hidden bg-black min-h-[300px]">
        {cameraError ? (
          <div className="absolute inset-0 flex flex-col items-center justify-center bg-secondary">
            <svg className="w-16 h-16 text-secondary-color mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
            </svg>
            <p className="text-gray-400 text-sm">{t('scanner.cameraError')}</p>
            <button
              onClick={() => fileInputRef.current?.click()}
              className="mt-4 px-6 py-2 bg-accent text-primary rounded-lg font-medium"
            >
              {t('scanner.uploadImage')}
            </button>
          </div>
        ) : (
          <Webcam
            ref={webcamRef}
            audio={false}
            screenshotFormat="image/jpeg"
            videoConstraints={videoConstraints}
            onUserMediaError={handleCameraError}
            className="absolute inset-0 w-full h-full object-cover"
          />
        )}
        
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div className="w-56 h-56 relative">
            <div className="absolute top-0 left-0 w-8 h-8 border-t-2 border-l-2 border-accent rounded-tl-lg" />
            <div className="absolute top-0 right-0 w-8 h-8 border-t-2 border-r-2 border-accent rounded-tr-lg" />
            <div className="absolute bottom-0 left-0 w-8 h-8 border-b-2 border-l-2 border-accent rounded-bl-lg" />
            <div className="absolute bottom-0 right-0 w-8 h-8 border-b-2 border-r-2 border-accent rounded-br-lg" />
          </div>
        </div>
        
        {loading && (
          <div className="absolute inset-0 bg-black/60 flex items-center justify-center">
            <div className="text-center">
              <div className="w-12 h-12 border-2 border-accent border-t-transparent rounded-full animate-spin mx-auto" />
              <p className="text-sm mt-4">{t('scanner.analyzing')}</p>
            </div>
          </div>
        )}
      </div>
      
      <div className="mt-4 flex gap-3">
        <motion.button
          onClick={captureImage}
          disabled={loading || !location || cameraError}
          whileTap={{ scale: 0.95 }}
          className="flex-1 py-4 bg-accent text-primary font-bold rounded-xl disabled:opacity-50 flex items-center justify-center gap-2"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          {loading ? t('scanner.analyzing') : t('scanner.takePhoto')}
        </motion.button>
        
        <motion.button
          onClick={() => fileInputRef.current?.click()}
          disabled={loading || !location}
          whileTap={{ scale: 0.95 }}
          className="w-14 h-14 bg-secondary rounded-xl border border-theme flex items-center justify-center disabled:opacity-50"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
        </motion.button>
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          capture="environment"
          onChange={handleFileUpload}
          className="hidden"
        />
      </div>
      
      <AnimatePresence>
        {result && <ResultCard data={result} onClose={clearResult} />}
      </AnimatePresence>
    </div>
  )
}

export default memo(Scanner)
