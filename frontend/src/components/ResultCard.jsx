import { memo, useCallback, useMemo } from 'react'
import { motion } from 'framer-motion'
import { useLanguage } from '../i18n'

const RISK_STYLES = {
  CRITICAL: 'text-danger border-danger bg-danger/10',
  HIGH: 'text-orange-500 border-orange-500 bg-orange-500/10',
  MODERATE: 'text-yellow-500 border-yellow-500 bg-yellow-500/10',
  LOW: 'text-success border-success bg-success/10',
  HEALTHY: 'text-success border-success bg-success/10'
}

function ResultCard({ data, onClose }) {
  const { t, language } = useLanguage()
  
  if (!data) return null
  
  const riskStyle = RISK_STYLES[data.risk_level] || 'text-gray-400 border-gray-400 bg-gray-400/10'
  
  // Get translated disease name
  const diseaseName = t(`diseases.${data.disease}`) || data.disease.replace(/_/g, ' ')
  
  // Get translated risk level
  const getRiskLabel = (level) => {
    switch (level) {
      case 'CRITICAL': return t('results.criticalRisk')
      case 'HIGH': return t('results.highRisk')
      case 'MODERATE': return t('results.mediumRisk')
      case 'LOW': return t('results.lowRisk')
      case 'HEALTHY': return t('results.healthy')
      default: return level
    }
  }
  
  return (
    <motion.div
      initial={{ opacity: 0, y: '100%' }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: '100%' }}
      className="fixed inset-x-0 bottom-16 z-40 bg-secondary rounded-t-2xl border-t border-theme p-4 max-h-[70vh] overflow-y-auto"
    >
      <div className="w-12 h-1 bg-gray-600 rounded-full mx-auto mb-4" />
      
      <div className="flex justify-between items-start mb-4">
        <h2 className={`text-lg font-bold ${riskStyle.split(' ')[0]}`}>
          {diseaseName}
        </h2>
        <button
          onClick={onClose}
          className="w-8 h-8 flex items-center justify-center rounded-full bg-primary text-secondary-color border border-theme"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      
      <div className="space-y-3">
        <div className={`p-4 rounded-xl border ${riskStyle}`}>
          <div className="flex justify-between items-center">
            <div>
              <div className="text-xs opacity-70">{t('results.riskLevel')}</div>
              <div className="text-xl font-bold">{getRiskLabel(data.risk_level)}</div>
            </div>
            <div className="text-right">
              <div className="text-xs opacity-70">{t('results.confidence')}</div>
              <div className="text-xl font-bold">{(data.confidence * 100).toFixed(0)}%</div>
            </div>
          </div>
          <div className="mt-2 h-2 bg-black/20 rounded-full overflow-hidden">
            <div 
              className="h-full bg-current rounded-full transition-all"
              style={{ width: `${data.risk_score * 100}%` }}
            />
          </div>
        </div>
        
        {data.weather && (
          <div className="p-3 bg-primary rounded-xl">
            <div className="text-xs text-gray-400 mb-2">{t('results.weather')}</div>
            <div className="grid grid-cols-3 gap-2 text-center">
              <div className="bg-secondary rounded-lg p-2">
                <div className="text-lg font-bold">{data.weather.temperature.toFixed(0)}°</div>
                <div className="text-xs text-gray-400">{t('results.temperature')}</div>
              </div>
              <div className="bg-secondary rounded-lg p-2">
                <div className="text-lg font-bold">{data.weather.humidity}%</div>
                <div className="text-xs text-gray-400">{t('results.humidity')}</div>
              </div>
              <div className="bg-secondary rounded-lg p-2">
                <div className="text-lg font-bold">{data.weather.wind_speed.toFixed(0)}</div>
                <div className="text-xs text-gray-400">Wind m/s</div>
              </div>
            </div>
          </div>
        )}
        
        {data.remedy && data.risk_level !== 'HEALTHY' && (
          <div className="p-4 bg-primary rounded-xl border-l-4 border-accent">
            <div className="text-xs text-accent mb-1">{t('results.treatment')}</div>
            <p className="text-sm font-medium mb-2">{data.remedy.spray}</p>
            <div className="flex gap-4 text-xs text-gray-400">
              <span>{t('results.applicationInterval')}: {data.remedy.repeat}</span>
            </div>
            {data.remedy.precautions && (
              <div className="mt-2 pt-2 border-t border-theme">
                <div className="text-xs text-gray-400 mb-1">{t('results.precautions')}</div>
                <p className="text-xs text-secondary-color">{data.remedy.precautions}</p>
              </div>
            )}
          </div>
        )}
        
        {data.risk_level === 'HEALTHY' && (
          <div className="p-4 bg-success/10 rounded-xl border border-success">
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5 text-success" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              <span className="text-success font-medium">{t('results.healthy')}</span>
            </div>
            <p className="text-sm text-gray-400 mt-2">
              {language === 'hi' ? 'सर्वोत्तम परिणामों के लिए नियमित निगरानी जारी रखें।' :
               language === 'te' ? 'ఉత్తమ ఫలితాల కోసం సాధారణ పర్యవేక్షణ కొనసాగించండి.' :
               language === 'ta' ? 'சிறந்த முடிவுகளுக்கு வழக்கமான கண்காணிப்பைத் தொடருங்கள்.' :
               language === 'kn' ? 'ಉತ್ತಮ ಫಲಿತಾಂಶಗಳಿಗಾಗಿ ನಿಯಮಿತ ಮೇಲ್ವಿಚಾರಣೆಯನ್ನು ಮುಂದುವರಿಸಿ.' :
               'Continue regular monitoring for best results.'}
            </p>
          </div>
        )}
      </div>
    </motion.div>
  )
}

export default memo(ResultCard)
