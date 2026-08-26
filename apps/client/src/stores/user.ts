import type { IUser } from '@/interfaces/IUser.js'
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { fetchMe, login, logout } from '../utils/auth'

export const useUserStore = defineStore('user', () => {
  const isLoggedIn = ref<boolean>()
  const userProfile = ref<IUser>()

  const checkAuth = async () => {
    const profile = await fetchMe()
    userProfile.value = profile ?? undefined
    isLoggedIn.value = !!profile
    return isLoggedIn.value
  }

  return {
    isLoggedIn,
    userProfile,
    checkAuth,
    login,
    logout,
  }
})
