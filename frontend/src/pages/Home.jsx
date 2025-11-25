import { memo } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useLanguage } from '../i18n'

function Home() {
  const { t } = useLanguage()
  
  const FEATURES = [
    {
      titleKey: 'home.feature1Title',
      descriptionKey: 'home.feature1Desc',
      icon: 'M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z M15 13a3 3 0 11-6 0 3 3 0 016 0z',
      link: '/scan'
    },
    {
      titleKey: 'home.feature2Title',
      descriptionKey: 'home.feature2Desc',
      icon: 'M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z',
      link: '/scan'
    },
    {
      titleKey: 'home.feature3Title',
      descriptionKey: 'home.feature3Desc',
      icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
      link: '/scan'
    }
  ]

  const CROPS = [
    { key: 'home.tomato', emoji: '🍅' },
    { key: 'home.potato', emoji: '🥔' },
    { key: 'home.pepper', emoji: '🌶️' }
  ]
  
  return (
    <div className="flex flex-col">
      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="text-center text-secondary-color mb-4"
      >
        {t('tagline')}
      </motion.p>
      
      <Link
        to="/scan"
        className="block mb-6"
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          whileTap={{ scale: 0.98 }}
          className="bg-gradient-to-br from-accent to-orange-600 rounded-2xl p-6 text-primary"
        >
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold">{t('home.scanNow')}</h2>
              <p className="text-sm opacity-80 mt-1">{t('home.subtitle')}</p>
            </div>
            <div className="w-14 h-14 bg-primary/20 rounded-full flex items-center justify-center">
              <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </div>
          </div>
        </motion.div>
      </Link>

      {/* Supported Crops */}
      <div className="mb-6 bg-secondary rounded-xl p-4 border border-theme">
        <h3 className="font-medium mb-3">{t('home.supportedCrops')}</h3>
        <div className="flex justify-around">
          {CROPS.map((crop) => (
            <div key={crop.key} className="text-center">
              <div className="text-3xl mb-1">{crop.emoji}</div>
              <span className="text-sm text-secondary-color">{t(crop.key)}</span>
            </div>
          ))}
        </div>
      </div>
      
      {/* Features */}
      <h3 className="font-medium mb-3">{t('home.features')}</h3>
      <div className="grid grid-cols-1 gap-3">
        {FEATURES.map((feature, index) => (
          <motion.div
            key={feature.titleKey}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <Link
              to={feature.link}
              className="flex items-center gap-4 bg-secondary p-4 rounded-xl border border-theme"
            >
              <div className="w-12 h-12 bg-accent/10 rounded-lg flex items-center justify-center flex-shrink-0">
                <svg className="w-6 h-6 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={feature.icon} />
                </svg>
              </div>
              <div>
                <h3 className="font-medium">{t(feature.titleKey)}</h3>
                <p className="text-xs text-gray-500 mt-1">{t(feature.descriptionKey)}</p>
              </div>
            </Link>
          </motion.div>
        ))}
      </div>
    </div>
  )
}

export default memo(Home)
