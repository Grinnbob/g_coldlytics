import Vue from 'vue'
import VueRouter from 'vue-router'

Vue.use(VueRouter)

const DashboardLayout = () => import('@/layouts/DashboardLayout.vue')

// Tasks
const TaskList = () => import('@/views/tasks/TasksList.vue')
const TaskCreate = () => import('@/views/tasks/TaskCreate.vue')
const TaskEdit = () => import('@/views/tasks/TaskEdit.vue')
const EmptyTaskList = () => import('@/views/tasks/EmptyTasksList.vue')


const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes: configRoutes()
})

function configRoutes () {
  return [
    {
      path: '/',
      name: 'Dashboard',
      component: DashboardLayout,
      children: [
        {
          path: '/tasks',
          name: 'Tasks List',
          component: TaskList
        },
        {
          path: '/task_empty',
          name: 'Empty tasks List',
          component: EmptyTaskList
        },
        {
          path: '/task_create',
          name: 'Task create form',
          component: TaskCreate
        },
        {
          path: '/task_edit',
          name: 'Task edit form',
          component: TaskEdit
        },
      ]
     }
  ]
}


export default router
