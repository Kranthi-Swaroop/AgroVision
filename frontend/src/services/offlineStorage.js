// AgroSentinel Offline Storage using IndexedDB
// Stores scans, results, and pending uploads for offline mode

const DB_NAME = 'agrosentinel-offline';
const DB_VERSION = 1;

// Store names
const STORES = {
  SCANS: 'scans',
  PENDING: 'pending_uploads',
  CACHE: 'api_cache',
  SETTINGS: 'settings'
};

class OfflineStorage {
  constructor() {
    this.db = null;
    this.isReady = false;
    this.readyPromise = this.init();
  }

  async init() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(DB_NAME, DB_VERSION);

      request.onerror = () => {
        console.error('[OfflineStorage] Failed to open database');
        reject(request.error);
      };

      request.onsuccess = () => {
        this.db = request.result;
        this.isReady = true;
        console.log('[OfflineStorage] Database ready');
        resolve(this.db);
      };

      request.onupgradeneeded = (event) => {
        const db = event.target.result;

        // Scans store - completed scan results
        if (!db.objectStoreNames.contains(STORES.SCANS)) {
          const scansStore = db.createObjectStore(STORES.SCANS, { keyPath: 'id', autoIncrement: true });
          scansStore.createIndex('timestamp', 'timestamp', { unique: false });
          scansStore.createIndex('disease', 'disease', { unique: false });
        }

        // Pending uploads - scans waiting to sync
        if (!db.objectStoreNames.contains(STORES.PENDING)) {
          const pendingStore = db.createObjectStore(STORES.PENDING, { keyPath: 'id', autoIncrement: true });
          pendingStore.createIndex('timestamp', 'timestamp', { unique: false });
        }

        // API cache - cached API responses
        if (!db.objectStoreNames.contains(STORES.CACHE)) {
          const cacheStore = db.createObjectStore(STORES.CACHE, { keyPath: 'url' });
          cacheStore.createIndex('timestamp', 'timestamp', { unique: false });
        }

        // Settings store
        if (!db.objectStoreNames.contains(STORES.SETTINGS)) {
          db.createObjectStore(STORES.SETTINGS, { keyPath: 'key' });
        }
      };
    });
  }

  async ensureReady() {
    if (!this.isReady) {
      await this.readyPromise;
    }
  }

  // ============ SCANS ============

  async saveScan(scanData) {
    await this.ensureReady();
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([STORES.SCANS], 'readwrite');
      const store = transaction.objectStore(STORES.SCANS);
      
      const record = {
        ...scanData,
        timestamp: Date.now(),
        synced: true
      };
      
      const request = store.add(record);
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  async getScans(limit = 50) {
    await this.ensureReady();
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([STORES.SCANS], 'readonly');
      const store = transaction.objectStore(STORES.SCANS);
      const index = store.index('timestamp');
      
      const scans = [];
      const request = index.openCursor(null, 'prev');
      
      request.onsuccess = (event) => {
        const cursor = event.target.result;
        if (cursor && scans.length < limit) {
          scans.push(cursor.value);
          cursor.continue();
        } else {
          resolve(scans);
        }
      };
      request.onerror = () => reject(request.error);
    });
  }

  async clearScans() {
    await this.ensureReady();
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([STORES.SCANS], 'readwrite');
      const store = transaction.objectStore(STORES.SCANS);
      const request = store.clear();
      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  // ============ PENDING UPLOADS ============

  async savePendingScan(imageBlob, location) {
    await this.ensureReady();
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = async () => {
        const transaction = this.db.transaction([STORES.PENDING], 'readwrite');
        const store = transaction.objectStore(STORES.PENDING);
        
        const record = {
          imageData: reader.result, // base64
          location,
          timestamp: Date.now(),
          status: 'pending'
        };
        
        const request = store.add(record);
        request.onsuccess = () => {
          console.log('[OfflineStorage] Saved pending scan:', request.result);
          resolve(request.result);
        };
        request.onerror = () => reject(request.error);
      };
      reader.readAsDataURL(imageBlob);
    });
  }

  async getPendingScans() {
    await this.ensureReady();
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([STORES.PENDING], 'readonly');
      const store = transaction.objectStore(STORES.PENDING);
      const request = store.getAll();
      
      request.onsuccess = () => resolve(request.result || []);
      request.onerror = () => reject(request.error);
    });
  }

  async getPendingCount() {
    await this.ensureReady();
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([STORES.PENDING], 'readonly');
      const store = transaction.objectStore(STORES.PENDING);
      const request = store.count();
      
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  async removePendingScan(id) {
    await this.ensureReady();
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([STORES.PENDING], 'readwrite');
      const store = transaction.objectStore(STORES.PENDING);
      const request = store.delete(id);
      
      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  async clearPending() {
    await this.ensureReady();
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([STORES.PENDING], 'readwrite');
      const store = transaction.objectStore(STORES.PENDING);
      const request = store.clear();
      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  // ============ API CACHE ============

  async cacheApiResponse(url, data) {
    await this.ensureReady();
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([STORES.CACHE], 'readwrite');
      const store = transaction.objectStore(STORES.CACHE);
      
      const record = {
        url,
        data,
        timestamp: Date.now()
      };
      
      const request = store.put(record);
      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  async getCachedResponse(url, maxAge = 3600000) { // 1 hour default
    await this.ensureReady();
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([STORES.CACHE], 'readonly');
      const store = transaction.objectStore(STORES.CACHE);
      const request = store.get(url);
      
      request.onsuccess = () => {
        const record = request.result;
        if (record && (Date.now() - record.timestamp) < maxAge) {
          resolve(record.data);
        } else {
          resolve(null);
        }
      };
      request.onerror = () => reject(request.error);
    });
  }

  // ============ SETTINGS ============

  async setSetting(key, value) {
    await this.ensureReady();
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([STORES.SETTINGS], 'readwrite');
      const store = transaction.objectStore(STORES.SETTINGS);
      const request = store.put({ key, value });
      
      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  async getSetting(key, defaultValue = null) {
    await this.ensureReady();
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([STORES.SETTINGS], 'readonly');
      const store = transaction.objectStore(STORES.SETTINGS);
      const request = store.get(key);
      
      request.onsuccess = () => {
        resolve(request.result?.value ?? defaultValue);
      };
      request.onerror = () => reject(request.error);
    });
  }
}

// Singleton instance
export const offlineStorage = new OfflineStorage();
export default offlineStorage;
