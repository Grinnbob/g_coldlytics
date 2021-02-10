<template>
  <div>
    <h3 class="mb-5">Linkedin</h3>
    <h4 class="mb-5">Required</h4>

    <b-form>
        <label>Geography</label>
        <b-form-input v-model="formData.geography" placeholder="USA, UK..."></b-form-input>
        <b-form-text class="mb-5">Rquired leads geography</b-form-text>

        <label>Profile languages</label>
        <b-form-input v-model="formData.languages" placeholder="English, German..."></b-form-input>
        <b-form-text class="mb-5">Rquired profile languages</b-form-text>

        <label>Number of contacts per company</label>
        <b-form-input type="number" min="1" v-model="formData.contacts_number" placeholder="3"></b-form-input>
        <b-form-text class="mb-5">Rquired number of contacts per company</b-form-text>

        <h4 class="mb-5">Optional</h4>

        <b-container fluid>
          <b-row>
            <b-col md="6">
              <label>Min company headcount</label>
              <b-form-input type="number" min="0" v-model="formData.employees_min" placeholder="1 000"></b-form-input>
              <b-form-text class="mb-5">Min number of employees in the company</b-form-text>
            </b-col>
            <b-col md="6">
              <label>Max company headcount</label>
              <b-form-input type="number" min="1" v-model="formData.employees_max" placeholder="100 000"></b-form-input>
              <b-form-text class="mb-5">Max number of employees in the company</b-form-text>
            </b-col>
          </b-row>
        </b-container>

        <label>Industries</label>
        <b-form-input v-model="formData.industries" placeholder="Sales, Marketing..."></b-form-input>
        <b-form-text class="mb-5">Companies industries</b-form-text>

        <label>Job functions</label>
        <b-form-input v-model="formData.job_functions" placeholder="Marketing, Product development, HR..."></b-form-input>
        <b-form-text class="mb-5">Enter job functions</b-form-text>

        <label>Seniority level</label>
        <b-form-select v-model="formData.seniority_level" :options="seniority_levels" placeholder="Sales, Marketing..."></b-form-select>
        <b-form-text class="mb-5">Lead seniority level in company</b-form-text>

        <label>Lead groups (recommended)</label>
        <b-form-textarea rows="3" v-model="formData.groups" placeholder="Marketing for CEO, Business dev..."></b-form-textarea>
        <b-form-text class="mb-5">Enter target linkedin lead groups</b-form-text>

    </b-form>

  </div>
</template>
<script>

export default {
    components: {
      
    },
    data: function () {
      return {
        seniority_levels: [{ value: null, text: 'Please select an option' }, 'Senior', 'Partner', 'Freelancer', 'C-Level', 'Director'],

        formData: {
          // required
          geography: '',
          languages: '',
          contacts_number: null,

          // optional
          employees_min: null,
          employees_max: null,
          industries: '',
          job_functions: '',
          seniority_level: null,
          groups: '',
        }
      }
    },
    watch: {
      formData: {
          handler: function() {
            this.$emit('linkedinData', [this.formData.geography, this.formData.languages, this.formData.contacts_number, this.formData.employees_min, this.formData.employees_max, this.formData.industries, this.formData.job_functions, this.formData.seniority_level, this.formData.groups])
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
