<template>
  <div>
    <b-container fluid>
      <b-row>
        <b-col cols="auto" class="ml-auto my-3">
          <b-button variant="primary" v-b-modal="'CreateTaskModal'">New task</b-button>
        </b-col>
      </b-row>
    </b-container>

    <TaskTable/>
    <TaskTypeModal/>

  </div>
</template>
<script>
import TaskTable from '@/components/TaskTable.vue'
import TaskTypeModal from '@/components/TaskTypeModal.vue'
export default {
  components: {
    TaskTable,
    TaskTypeModal
  },
}
</script>
