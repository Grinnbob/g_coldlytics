<template>
  <div>
    <h3 class="mb-5">Custom</h3>
    <h4 class="mb-5">Required</h4>

    <b-form>
        <label>Geography</label>
        <b-form-input v-model="formData.geography" placeholder="USA, UK..."></b-form-input>
        <b-form-text class="mb-5">Rquired leads geography</b-form-text>

        <label>Number of contacts per company</label>
        <b-form-input type="number" min="1" v-model="formData.contacts_number" placeholder="3"></b-form-input>
        <b-form-text class="mb-5">Rquired number of contacts per company</b-form-text>
    </b-form>

  </div>
</template>
<script>

export default {
    components: {
      
    },
    data: function () {
      return {
        formData: {
          // required
          geography: '',
          contacts_number: null,
        }
      }
    },
    watch: {
      formData: {
          handler: function() {
            this.$emit('customData', [this.formData.geography, this.formData.contacts_number])
        },
        deep: true
      }
    },
    methods: {
      
    },
    mounted() {
      
    }
  }
</script>
