<template>
  <div>
    <h3 class="mb-5">Youtube</h3>
    <h4 class="mb-5">Required</h4>

    <b-form>
        <label>Channel languages</label>
        <b-form-input v-model="formData.languages" placeholder="English, German..."></b-form-input>
        <b-form-text class="mb-5">Rquired profile languages</b-form-text>

        <b-container fluid>
          <b-row>
            <b-col md="6">
              <label>Min subscribers</label>
              <b-form-input type="number" min="0" v-model="formData.subscribers_min" placeholder="1 000"></b-form-input>
              <b-form-text class="mb-5">Min number of channel subscribers</b-form-text>
            </b-col>
            <b-col md="6">
              <label>Max subscribers</label>
              <b-form-input type="number" min="1" v-model="formData.subscribers_max" placeholder="100 000"></b-form-input>
              <b-form-text class="mb-5">Max number of channel subscribers</b-form-text>
            </b-col>
          </b-row>
        </b-container>

        <label>Categories</label>
        <b-form-input v-model="formData.categories" placeholder="Movies, Fashion..."></b-form-input>
        <b-form-text class="mb-5">Channel categories</b-form-text>

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
          languages: '',
          subscribers_min: null,
          subscribers_max: null,
          categories: '',
        }
      }
    },
    watch: {
      formData: {
          handler: function() {
            this.$emit('youtubeData', [this.formData.languages, this.formData.subscribers_min, this.formData.subscribers_max, this.formData.categories])
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
