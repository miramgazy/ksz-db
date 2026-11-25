import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/LoginView.vue'),
    meta: { guest: true },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/RegisterView.vue'),
    meta: { guest: true },
  },
  {
    path: '/',
    name: 'Companies',
    component: () => import('../views/CompanyListView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/anydesk',
    name: 'AnyDesk',
    component: () => import('../views/AnydeskListView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/webkassa',
    name: 'WebKassa',
    component: () => import('../views/WebKassaView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/services',
    name: 'Services',
    component: () => import('../views/ItsServicesView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/distributions',
    name: 'Distributions',
    component: () => import('../views/DistributionsView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/users',
    name: 'Users',
    component: () => import('../views/UsersView.vue'),
    meta: { requiresAuth: true, superadminOnly: true },
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/',
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return next({ name: 'Login' })
  }

  if (to.meta.guest && authStore.isAuthenticated) {
    return next({ name: 'Companies' })
  }

  if (to.meta.superadminOnly && !authStore.isSuperAdmin) {
    return next({ name: 'Companies' })
  }

  next()
})

export default router
