<template>
  <div>
    <h3 class="my-5">Edit task</h3>

    <b-form>

        <label>Segment title</label>
        <b-form-input v-model="segment_title" disabled class="mb-5"></b-form-input>

        <label>Spreadsheet link</label>
        <b-form-input v-model="spreadsheet_link" disabled class="mb-5"></b-form-input>

        <label>Executor link</label>
        <b-form-input v-model="executor_link" disabled class="mb-5"></b-form-input>

        <label>Email header</label>
        <b-form-input v-model="email_header" placeholder="H5"></b-form-input>
        <b-form-text class="mb-5">Enter email header from spreadsheet</b-form-text>

        <label>Header row</label>
        <b-form-input v-model="header_row" placeholder="14"></b-form-input>
        <b-form-text class="mb-5">Enter header row from spreadsheet</b-form-text>

        <b-button type="reset" variant="primary" class="mx-2 mb-5" v-on:click="onCheck()">Check</b-button>
        <b-button type="submit" variant="primary" class="mx-2 mb-5" v-on:click="onSync()">Sync</b-button>

    </b-form>

  </div>
</template>
<script>

export default {
    components: {
      
    },
    data() {
      return {
        segment_title: 'some title',
        spreadsheet_link: 'link/spreadsheet',
        executor_link: 'executor@email.com',

        email_header: '',
        header_row: '',

      }
    },
    methods: {
      onCheck() {
        //
      },
      onSync() {
        //
      },
    },
    mounted() {
      
    }
  }
</script>
