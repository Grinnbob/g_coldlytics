<template>
  <div>
      <b-table
          id="tasks-table"
          striped
          hover
          :fields="fields"
          :items="items">

        <template #cell(title)="data">
          <a href="task_edit">{{ data.item.title }}</a>
        </template>

        <!-- A custom formatted column -->
        <template #cell(type)="data">
          <b class="text-info">{{ data.item.type }}</b>
        </template>

        <!-- A virtual composite column -->
        <template #cell(status)="data">
          {{ data.item.status }}
        </template>

        <!-- Optional default data cell scoped slot -->
        <template #cell(check)="data">
          <b-button variant="outline-primary">Check</b-button>
        </template>

        <template #cell(sync)="data">
          <b-button variant="outline-primary">Sync</b-button>
        </template>

      </b-table>
      <b-pagination
            align='right'
          v-model="currentPage"
          :total-rows="items.lenght"
          :per-page="perPage"
          aria-controls="tasks-table"
        ></b-pagination>
  </div>
</template>

<script>
  export default {
    name: 'TaskTable',
    data: function () {
      return {
        perPage: 3,
        currentPage: 1,
        items: [
          { title: "Hn-1 (500)", type: "Linkedin", status: "new", id: "1" },
          { title: "Hn-2 (50)", type: "Custom", status: "in progress", id: "2" },
          { title: "Hn-3 (250)", type: "Facebook", status: "need sync", id: "3" },
          { title: "Hn-5 (6250)", type: "Instagram", status: "completed", id: "4" },
        ],
         fields: [
          { key: 'title', label: 'Segment title' },
          { key: 'type', label: 'Type' },
          { key: 'status', label: 'Status' },

          { key: 'check', label: '' },
          { key: 'sync', label: '' },

        ],
      }
    }
  }
</script>