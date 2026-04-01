/**
 * Vue Router 配置
 */

import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import ZoteroWorkspace from '../views/ZoteroWorkspace.vue'
import ResearchMapView from '../views/ResearchMapView.vue'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    redirect: '/zotero'
  },
  {
    path: '/zotero',
    name: 'ZoteroWorkspace',
    component: ZoteroWorkspace,
    meta: {
      title: 'Zotero 集成 - SmartPaper',
      description: '连接 Zotero 文献管理工具，导入文献到 SmartPaper'
    }
  },
  {
    path: '/research-map',
    name: 'ResearchMap',
    component: ResearchMapView,
    meta: {
      title: '研究地图 - SmartPaper',
      description: '交互式知识图谱可视化分析'
    }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 路由守卫：设置页面标题
router.beforeEach((to, _from, next) => {
  if (to.meta?.title) {
    document.title = to.meta.title as string
  }
  next()
})

export default router
