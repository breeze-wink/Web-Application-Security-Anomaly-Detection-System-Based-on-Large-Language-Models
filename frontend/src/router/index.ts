import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard/index.vue'),
    meta: {
      title: '监控大屏',
      icon: 'Monitor'
    }
  },
  {
    path: '/events',
    name: 'Events',
    component: () => import('@/views/Events/index.vue'),
    meta: {
      title: '事件管理',
      icon: 'Warning'
    }
  },
  {
    path: '/events/:id',
    name: 'EventDetail',
    component: () => import('@/views/Events/Detail.vue'),
    meta: {
      title: '事件详情',
      hidden: true
    }
  },
  {
    path: '/analytics',
    name: 'Analytics',
    component: () => import('@/views/Analytics/index.vue'),
    meta: {
      title: '统计分析',
      icon: 'DataAnalysis'
    }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/Settings/index.vue'),
    meta: {
      title: '系统配置',
      icon: 'Setting'
    }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/404.vue'),
    meta: {
      title: '页面不存在',
      hidden: true
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    }
    return { top: 0 }
  }
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  if (to.meta?.title) {
    document.title = `${to.meta.title} - Web安全事件管理系统`
  }
  next()
})

export default router 