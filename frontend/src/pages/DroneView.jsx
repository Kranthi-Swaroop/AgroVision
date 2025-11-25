import { useState, useEffect, useRef, useCallback, useMemo, memo } from 'react'
import { MapContainer, TileLayer, Circle, Popup, useMap, Rectangle } from 'react-leaflet'
import { motion, AnimatePresence } from 'framer-motion'
import { getLocationHistory } from '../services/api'
import { useStore } from '../store/useStore'
import { useLanguage } from '../i18n'
import 'leaflet/dist/leaflet.css'

const RISK_COLORS = {
  critical: '#FF0000',
  high: '#FF8C00',
  medium: '#FFFF00',
  low: '#00FF7F'
}

const LEGEND_ITEMS = [
  { color: 'bg-danger', label: 'Critical' },
  { color: 'bg-orange-500', label: 'High' },
  { color: 'bg-yellow-500', label: 'Medium' },
  { color: 'bg-success', label: 'Low' }
]

// Disease clusters for realistic simulation
const DISEASE_CLUSTERS = [
  { disease: 'tomato_late_blight', risk: 0.85, spread: 0.002 },
  { disease: 'tomato_early_blight', risk: 0.65, spread: 0.003 },
  { disease: 'tomato_bacterial_spot', risk: 0.55, spread: 0.002 },
  { disease: 'potato_late_blight', risk: 0.9, spread: 0.0025 },
  { disease: 'tomato_yellow_leaf_curl_virus', risk: 0.75, spread: 0.004 },
]

const getRiskColor = (risk) => {
  if (risk >= 0.8) return RISK_COLORS.critical
  if (risk >= 0.6) return RISK_COLORS.high
  if (risk >= 0.4) return RISK_COLORS.medium
  return RISK_COLORS.low
}

// Generate realistic clustered demo data (diseases spread in patches)
const generateDemoData = (lat, lng) => {
  const data = []
  let id = 0
  
  // Create 3-4 disease clusters (infection hotspots)
  const numClusters = 2 + Math.floor(Math.random() * 3)
  
  for (let c = 0; c < numClusters; c++) {
    const cluster = DISEASE_CLUSTERS[Math.floor(Math.random() * DISEASE_CLUSTERS.length)]
    // Cluster center offset from main location
    const clusterLat = lat + (Math.random() - 0.5) * 0.008
    const clusterLng = lng + (Math.random() - 0.5) * 0.008
    
    // Points within this cluster
    const pointsInCluster = 4 + Math.floor(Math.random() * 6)
    for (let i = 0; i < pointsInCluster; i++) {
      const offsetLat = (Math.random() - 0.5) * cluster.spread * 2
      const offsetLng = (Math.random() - 0.5) * cluster.spread * 2
      data.push({
        id: `demo-${id++}`,
        lat: clusterLat + offsetLat,
        lng: clusterLng + offsetLng,
        disease: cluster.disease,
        risk: cluster.risk + (Math.random() - 0.5) * 0.2,
        date: new Date(Date.now() - Math.random() * 3 * 24 * 60 * 60 * 1000).toISOString(),
        confidence: 0.82 + Math.random() * 0.15
      })
    }
  }
  
  // Add some healthy areas
  const healthyPoints = 5 + Math.floor(Math.random() * 5)
  for (let i = 0; i < healthyPoints; i++) {
    data.push({
      id: `demo-${id++}`,
      lat: lat + (Math.random() - 0.5) * 0.01,
      lng: lng + (Math.random() - 0.5) * 0.01,
      disease: 'tomato_healthy',
      risk: 0.1 + Math.random() * 0.15,
      date: new Date().toISOString(),
      confidence: 0.9 + Math.random() * 0.08
    })
  }
  
  return data
}

// Map recenter component
function MapController({ center, zoom }) {
  const map = useMap()
  useEffect(() => {
    if (center) map.setView(center, zoom || 16)
  }, [center, zoom, map])
  return null
}

// Scanning animation overlay
function ScanningOverlay({ bounds, progress }) {
  if (!bounds || progress >= 100) return null
  
  const scanLineY = bounds[0][0] + (bounds[1][0] - bounds[0][0]) * (progress / 100)
  
  return (
    <Rectangle
      bounds={[[scanLineY - 0.0002, bounds[0][1]], [scanLineY + 0.0002, bounds[1][1]]]}
      pathOptions={{
        color: '#00FF00',
        fillColor: '#00FF00',
        fillOpacity: 0.5,
        weight: 2
      }}
    />
  )
}

function DroneView() {
  const { location, setLocation } = useStore()
  const { t } = useLanguage()
  const [infections, setInfections] = useState([])
  const [loading, setLoading] = useState(false)
  const [demoMode, setDemoMode] = useState(false)
  const [analysisRunning, setAnalysisRunning] = useState(false)
  const fileInputRef = useRef(null)
  
  useEffect(() => {
    if (location || !navigator.geolocation) return
    navigator.geolocation.getCurrentPosition(
      (pos) => setLocation({ latitude: pos.coords.latitude, longitude: pos.coords.longitude }),
      () => setLocation({ latitude: 17.3850, longitude: 78.4867 }) // Hyderabad default
    )
  }, [location, setLocation])
  
  const loadInfectionData = useCallback(async () => {
    if (!location) return
    setLoading(true)
    try {
      const data = await getLocationHistory(location.latitude, location.longitude)
      if (data && data.length > 0) {
        setInfections(data.map(record => ({
          id: record._id,
          lat: record.location?.latitude || location.latitude,
          lng: record.location?.longitude || location.longitude,
          disease: record.disease,
          risk: record.risk_score || 0.5,
          date: record.created_at,
          confidence: record.confidence || 0.85
        })))
      }
    } catch (err) {
      console.log('No history data, can use demo mode')
    }
    setLoading(false)
  }, [location])
  
  useEffect(() => {
    if (location) loadInfectionData()
  }, [location, loadInfectionData])
  
  const [scanProgress, setScanProgress] = useState(0)
  const [scanBounds, setScanBounds] = useState(null)
  const [revealedPoints, setRevealedPoints] = useState([])
  
  // Simulate drone analysis with progressive reveal
  const runDemoAnalysis = useCallback(() => {
    if (!location) return
    setAnalysisRunning(true)
    setDemoMode(true)
    setInfections([])
    setRevealedPoints([])
    setScanProgress(0)
    
    // Set scan area bounds
    const bounds = [
      [location.latitude - 0.005, location.longitude - 0.005],
      [location.latitude + 0.005, location.longitude + 0.005]
    ]
    setScanBounds(bounds)
    
    // Generate all data points
    const allData = generateDemoData(location.latitude, location.longitude)
    
    // Progressive scanning animation
    let progress = 0
    const scanInterval = setInterval(() => {
      progress += 2
      setScanProgress(progress)
      
      // Reveal points as scan line passes them
      const currentScanY = bounds[0][0] + (bounds[1][0] - bounds[0][0]) * (progress / 100)
      const newRevealed = allData.filter(p => p.lat <= currentScanY)
      setRevealedPoints(newRevealed)
      
      if (progress >= 100) {
        clearInterval(scanInterval)
        setTimeout(() => {
          setInfections(allData)
          setRevealedPoints([])
          setScanBounds(null)
          setAnalysisRunning(false)
        }, 500)
      }
    }, 80)
    
    return () => clearInterval(scanInterval)
  }, [location])
  
  const handleVideoUpload = useCallback((e) => {
    const file = e.target.files?.[0]
    if (!file || !location) return
    
    // Use same progressive scan for video
    setAnalysisRunning(true)
    setDemoMode(true)
    setInfections([])
    setRevealedPoints([])
    setScanProgress(0)
    
    const bounds = [
      [location.latitude - 0.006, location.longitude - 0.006],
      [location.latitude + 0.006, location.longitude + 0.006]
    ]
    setScanBounds(bounds)
    
    const allData = generateDemoData(location.latitude, location.longitude)
    // Add more points for video analysis
    const extraPoints = generateDemoData(location.latitude + 0.002, location.longitude + 0.002)
    const combinedData = [...allData, ...extraPoints.map((p, i) => ({ ...p, id: `extra-${i}` }))]
    
    let progress = 0
    const scanInterval = setInterval(() => {
      progress += 1.5
      setScanProgress(Math.min(progress, 100))
      
      const currentScanY = bounds[0][0] + (bounds[1][0] - bounds[0][0]) * (progress / 100)
      const newRevealed = combinedData.filter(p => p.lat <= currentScanY)
      setRevealedPoints(newRevealed)
      
      if (progress >= 100) {
        clearInterval(scanInterval)
        setTimeout(() => {
          setInfections(combinedData)
          setRevealedPoints([])
          setScanBounds(null)
          setAnalysisRunning(false)
        }, 500)
      }
    }, 80)
    
    e.target.value = ''
  }, [location])
  
  const criticalCount = useMemo(() => infections.filter(i => i.risk >= 0.8).length, [infections])
  const highCount = useMemo(() => infections.filter(i => i.risk >= 0.6 && i.risk < 0.8).length, [infections])
  const healthyCount = useMemo(() => infections.filter(i => i.disease?.includes('healthy')).length, [infections])
  
  return (
    <div className="flex flex-col h-full">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-xl font-bold">Field Map</h1>
        <div className="flex gap-2">
          <motion.button
            onClick={runDemoAnalysis}
            whileTap={{ scale: 0.95 }}
            disabled={analysisRunning}
            className="px-3 py-2 bg-accent text-white rounded-lg text-sm font-medium disabled:opacity-50"
          >
            {analysisRunning ? 'Analyzing...' : '🛰️ Demo Scan'}
          </motion.button>
          <motion.button
            onClick={() => fileInputRef.current?.click()}
            whileTap={{ scale: 0.95 }}
            disabled={analysisRunning}
            className="px-3 py-2 bg-secondary rounded-lg text-sm border border-theme disabled:opacity-50"
          >
            📹 Upload
          </motion.button>
        </div>
        <input
          ref={fileInputRef}
          type="file"
          accept="video/*,image/*"
          onChange={handleVideoUpload}
          className="hidden"
        />
      </div>
      
      {/* Analysis Progress - only show when not on map */}
      {analysisRunning && !location && (
        <div className="bg-accent/10 border border-accent/30 rounded-xl p-4 mb-4">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 border-2 border-accent border-t-transparent rounded-full animate-spin" />
            <div>
              <p className="font-medium text-accent">Analyzing Field...</p>
              <p className="text-xs text-gray-400">Processing drone imagery with AI model</p>
            </div>
          </div>
        </div>
      )}
      
      {/* Demo Mode Banner */}
      {demoMode && !analysisRunning && infections.length > 0 && (
        <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-2 mb-4 text-center">
          <span className="text-xs text-yellow-500">🎯 Demo Mode: Simulated field analysis data</span>
        </div>
      )}
      
      {(loading && !analysisRunning) && (
        <div className="flex items-center justify-center py-8">
          <div className="w-8 h-8 border-2 border-accent border-t-transparent rounded-full animate-spin" />
        </div>
      )}
      
      {location && (
        <div className="flex-1 rounded-xl overflow-hidden border border-theme min-h-[300px] relative">
          <MapContainer
            center={[location.latitude, location.longitude]}
            zoom={16}
            style={{ height: '100%', width: '100%' }}
          >
            <MapController center={[location.latitude, location.longitude]} zoom={16} />
            {/* Satellite imagery from ESRI */}
            <TileLayer
              url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
              attribution="ESRI"
            />
            {/* Scanning animation overlay */}
            {analysisRunning && scanBounds && (
              <ScanningOverlay bounds={scanBounds} progress={scanProgress} />
            )}
            {/* Revealed points during scan */}
            {analysisRunning && revealedPoints.map(point => (
              <Circle
                key={point.id}
                center={[point.lat, point.lng]}
                radius={30}
                pathOptions={{
                  color: getRiskColor(point.risk),
                  fillColor: getRiskColor(point.risk),
                  fillOpacity: 0.8,
                  weight: 2
                }}
              />
            ))}
            {/* Final infection points */}
            {!analysisRunning && infections.map(point => (
              <Circle
                key={point.id}
                center={[point.lat, point.lng]}
                radius={35}
                pathOptions={{
                  color: getRiskColor(point.risk),
                  fillColor: getRiskColor(point.risk),
                  fillOpacity: 0.7,
                  weight: 2
                }}
              >
                <Popup>
                  <div className="text-black text-sm p-1">
                    <strong className="capitalize">{point.disease?.replace(/_/g, ' ')}</strong>
                    <br />
                    <span className="text-gray-600">Risk: {(point.risk * 100).toFixed(0)}%</span>
                    <br />
                    <span className="text-gray-600">Confidence: {((point.confidence || 0.85) * 100).toFixed(0)}%</span>
                  </div>
                </Popup>
              </Circle>
            ))}
          </MapContainer>
          
          {/* Scanning HUD overlay */}
          {analysisRunning && (
            <div className="absolute top-2 left-2 right-2 z-[1000] bg-black/70 rounded-lg p-3">
              <div className="flex items-center justify-between text-green-400 text-sm font-mono">
                <span>🛰️ DRONE SCAN ACTIVE</span>
                <span>{scanProgress}%</span>
              </div>
              <div className="mt-2 h-1 bg-gray-700 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-green-500 transition-all duration-100"
                  style={{ width: `${scanProgress}%` }}
                />
              </div>
              <div className="mt-2 flex justify-between text-xs text-gray-400 font-mono">
                <span>Detections: {revealedPoints.length}</span>
                <span>Critical: {revealedPoints.filter(p => p.risk >= 0.8).length}</span>
              </div>
            </div>
          )}
        </div>
      )}
      
      {/* Legend */}
      <div className="grid grid-cols-4 gap-2 mt-4">
        {LEGEND_ITEMS.map(item => (
          <div key={item.label} className="bg-secondary rounded-lg p-2 text-center">
            <div className={`w-3 h-3 rounded-full ${item.color} mx-auto mb-1`} />
            <span className="text-xs text-gray-400">{item.label}</span>
          </div>
        ))}
      </div>
      
      {infections.length > 0 && (
        <div className="mt-4 bg-secondary rounded-xl p-4">
          <h3 className="text-sm font-medium mb-3 text-gray-400">Field Analysis Summary</h3>
          <div className="grid grid-cols-4 gap-3">
            <div className="text-center">
              <div className="text-2xl font-bold">{infections.length}</div>
              <div className="text-xs text-gray-400">Total Points</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-danger">{criticalCount}</div>
              <div className="text-xs text-gray-400">Critical</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-500">{highCount}</div>
              <div className="text-xs text-gray-400">High Risk</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-success">{healthyCount}</div>
              <div className="text-xs text-gray-400">Healthy</div>
            </div>
          </div>
          
          {/* Disease breakdown */}
          <div className="mt-4 pt-3 border-t border-theme">
            <h4 className="text-xs text-gray-400 mb-2">Detected Issues:</h4>
            <div className="flex flex-wrap gap-2">
              {[...new Set(infections.filter(i => !i.disease?.includes('healthy')).map(i => i.disease))].slice(0, 5).map(disease => (
                <span key={disease} className="px-2 py-1 bg-danger/20 text-danger text-xs rounded-full capitalize">
                  {disease?.replace(/_/g, ' ')}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}
      
      {/* Empty state */}
      {!loading && !analysisRunning && infections.length === 0 && (
        <div className="mt-4 bg-secondary rounded-xl p-6 text-center">
          <div className="text-4xl mb-2">🛰️</div>
          <h3 className="font-medium mb-1">No Field Data</h3>
          <p className="text-sm text-gray-400 mb-4">
            Click "Demo Scan" to simulate drone analysis or upload drone footage
          </p>
          <motion.button
            onClick={runDemoAnalysis}
            whileTap={{ scale: 0.95 }}
            className="px-4 py-2 bg-accent text-white rounded-lg text-sm font-medium"
          >
            Run Demo Analysis
          </motion.button>
        </div>
      )}
    </div>
  )
}

export default memo(DroneView)
