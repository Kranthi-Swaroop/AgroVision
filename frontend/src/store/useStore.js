import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export const useStore = create(
  persist(
    (set) => ({
      result: null,
      loading: false,
      location: null,
      history: [],
      theme: 'system',
      
      setResult: (result) => set({ result }),
      setLoading: (loading) => set({ loading }),
      setLocation: (location) => set({ location }),
      setHistory: (history) => set({ history }),
      setTheme: (theme) => set({ theme }),
      clearResult: () => set({ result: null })
    }),
    {
      name: 'agrosentinel-storage',
      partialize: (state) => ({ theme: state.theme })
    }
  )
)
