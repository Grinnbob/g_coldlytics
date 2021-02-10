<template>
    <b-modal id="CreateTaskModal" hide-footer title="Choose task type">

      <b-card no-body class="overflow-hidden" v-on:click="createTask('linkedin')">
        <b-row no-gutters>
          <b-col md="6">
            <b-card-img src="https://nakedsecurity.sophos.com/wp-content/uploads/sites/2/2017/12/linkedin.png?w=780&h=408&crop=1 alt='Image' class='rounded-0'"></b-card-img>
          </b-col>
          <b-col md="6">
            <b-card-body>
              <b-card-text>
                LinkedIn
              </b-card-text>
            </b-card-body>
          </b-col>
        </b-row>
      </b-card>

      <b-card no-body class="overflow-hidden" v-on:click="createTask('facebook')">
        <b-row no-gutters>
          <b-col md="6">
            <b-card-img src="https://cdn.iconscout.com/icon/free/png-256/facebook-logo-2019-1597680-1350125.png"></b-card-img>
          </b-col>
          <b-col md="6">
            <b-card-body>
              <b-card-text>
                Facebook
              </b-card-text>
            </b-card-body>
          </b-col>
        </b-row>
      </b-card>

      <b-card no-body class="overflow-hidden" v-on:click="createTask('youtube')">
        <b-row no-gutters>
          <b-col md="6">
            <b-card-img src="https://apkshki.com/storage/535/icon_5dcff2e78a41e_535_w256.png"></b-card-img>
          </b-col>
          <b-col md="6">
            <b-card-body>
              <b-card-text>
                Youtube
              </b-card-text>
            </b-card-body>
          </b-col>
        </b-row>
      </b-card>

      <b-card no-body class="overflow-hidden" v-on:click="createTask('custom')">
        <b-row no-gutters>
          <b-col md="6">
            
          </b-col>
          <b-col md="6">
            <b-card-body>
              <b-card-text>
                Custom
              </b-card-text>
            </b-card-body>
          </b-col>
        </b-row>
      </b-card>

    </b-modal>
</template>

<script>
  export default {
    components: {
      
    },
    name: 'TaskTypeModal',
    data: function () {
      return {

      }
    },
    methods: {
      createTask(task_type) {
        this.$router.push({path: "task_create", query: { "task_type": task_type }})
      }
    },
  }
</script>
