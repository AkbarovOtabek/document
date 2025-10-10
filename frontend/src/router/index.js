import { createRouter, createWebHistory } from 'vue-router'
import {pages} from '../views/index.js'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/',                    name: 'organizations',   component: pages.Organizations },
    { path: '/category/organizations/:slug/',                    name: 'orgs-by-category',props: true ,   component: pages.OrganizationsList },
    { path: '/category/organizations/:slug/detail/',                    name: 'org-detail',props: true ,   component: pages.OrganizationDetail },
    { path: '/users/',               name: 'users',           component:  pages.Users },
    { path: '/search-documents/',    name: 'search',          component:  pages.SearchDocuments },
    { path: '/statistika/',          name: 'statistika',      component:  pages.Statistika },
    { path: '/account/',             name: 'account',         component:  pages.Account },
    { path: '/login/', name: 'login', component: pages.Login ,meta: { hideNav: true } }
  ],
  scrollBehavior() {
    return { top: 0 }
  }
})
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access') || sessionStorage.getItem('access')
  if (to.meta?.requiresAuth && !token) next({ name: 'login' })
  else next()
})
export default router
