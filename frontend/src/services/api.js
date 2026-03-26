import axios from 'axios'
import { useLoadingStore } from '@/stores/loading'
import alertService from './alertService'

// Create Axios instance for Backend API
const apiBackend = axios.create({
  baseURL: import.meta.env.VITE_API_ENDPOINT + '/v1/',
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json'
  },
  withCredentials: true
})

// Create Axios instance for Commons API
const apiCommons = axios.create({
  baseURL: 'https://commons.wikimedia.org/w/api.php',
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json'
  }
})

const addInterceptors = (instance, isBackend = false) => {
  instance.interceptors.request.use(
    (config) => {
      const loadingStore = useLoadingStore()
      loadingStore.setLoading(true)

      return config
    },
    (error) => {
      const loadingStore = useLoadingStore()
      loadingStore.setLoading(false)

      return Promise.reject(error)
    }
  )

  // Response Interceptor
  instance.interceptors.response.use(
    (response) => {
      const loadingStore = useLoadingStore()
      loadingStore.setLoading(false)

      const data = response.data

      // For the backend API, we handle the Montage-specific status contract
      if (isBackend) {
        if (data.status === 'success') {
          return data.data // Pass through only the relevant payload
        } else {
          // Global error handling for Montage API failures
          const errorMsg = data.errors && data.errors.length ? data.errors[0] : 'API Error'
          alertService.error({ message: errorMsg })
          return Promise.reject(data.errors)
        }
      }

      // For Commons API, just return the data directly
      return data
    },
    (error) => {
      const loadingStore = useLoadingStore()
      loadingStore.setLoading(false)

      // Global error handling for network/HTTP level errors
      alertService.error(error)

      return Promise.reject(error)
    }
  )
}

addInterceptors(apiBackend, true)
addInterceptors(apiCommons, false)

export { apiBackend, apiCommons }
