<template>
  <div>
    
    <b-container fluid>
      <b-row>
        <b-col>
            <b-img src="https://cdn.dribbble.com/users/436620/screenshots/8386175/no_results_found__4x.jpg" fluid alt="Responsive image"></b-img>
        </b-col>
      </b-row>

      <b-row align-h="center" class="my-5">
        <b-col cols="2">
          <b-button variant="primary" v-b-modal="'CreateTaskModal'">New task</b-button>
        </b-col>
      </b-row>
    </b-container>
    <TaskTypeModal/>

  </div>
</template>
<script>
import TaskTypeModal from '@/components/TaskTypeModal.vue'

export default {
  components: {
    TaskTypeModal
    },
}
</script>
