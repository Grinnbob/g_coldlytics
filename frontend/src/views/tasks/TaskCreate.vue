<template>
  <div>

    <b-container class="my-3" fluid>
      <b-row>
        <b-col>
          <h3>Create task form</h3>
        </b-col>
      </b-row>
    </b-container>

    <b-container fluid>
      <b-row>
        <b-col md="6">
          <b-form>
            <LinkedinForm @linkedinData="handleLinkedinData($event)" v-if="task_type == 'linkedin'"/>
            <FacebookForm @facebookData="handleFacebookData($event)" v-if="task_type == 'facebook'"/>
            <YoutubeForm @youtubeData="handleYoutubeData($event)" v-if="task_type == 'youtube'"/>
            <CustomForm @customData="handleCustomData($event)" v-if="task_type == 'custom'"/>

            <h3 class="mb-5">General</h3>

            <label>Segment title</label>
            <b-form-input v-model="formData.segment_title" placeholder="Consumer goods (5 000 leads)"></b-form-input>
            <b-form-text class="mb-5">Type task (segment) title</b-form-text>

            <label for="leads-form">Total number of leads</label>
            <b-form-input id="leads-form" type="number" min="1"  v-model="form.leads_number" placeholder="1000"></b-form-input>
            <b-form-text id="leads-form-help" class="mb-5">Total number of leads for this task</b-form-text>

            <b-form-group
              label="Choose required options"
              v-slot="{ ariaDescribedby }"
              class="mb-5"
            >
              <b-form-checkbox-group
                v-model="form.selected_general_data"
                :options="options"
                :aria-describedby="ariaDescribedby"
                size="lg"
                stacked
                switches
              ></b-form-checkbox-group>
            </b-form-group>

            <label for="textarea">Other</label>
            <b-form-textarea
              id="textarea"
              v-model="form.task_text"
              placeholder="Any other task requirements..."
              rows="3"
              max-rows="6"
              class="mb-5"
            ></b-form-textarea>

            <b-button type="reset" variant="danger" class="mx-2 mb-5" v-on:click="onCancel()">Cancel</b-button>
            <b-button type="submit" variant="primary" class="mx-2 mb-5" v-on:click="onSubmit()">Create</b-button>
          </b-form>
        </b-col>
      </b-row>
    </b-container>

    {{ form }}

  </div>
</template>
<script>
import LinkedinForm from '@/components/forms/LinkedinForm.vue'
import FacebookForm from '@/components/forms/FacebookForm.vue'
import YoutubeForm from '@/components/forms/YoutubeForm.vue'
import CustomForm from '@/components/forms/CustomForm.vue'

export default {
    components: {
      LinkedinForm,
      FacebookForm,
      YoutubeForm,
      CustomForm,
    },
    data() {
      return {
        task_type: null,
        options: [
          { text: 'First name', value: 'first_name' },
          { text: 'Company name', value: 'company_name' },
          { text: 'Company website', value: 'company_website' },
          { text: 'Personal LinkedIn', value: 'personal_linkedin' },
          { text: 'Company LinkedIn', value: 'company_linkedin' },
          { text: 'Personal or business email', value: 'email' },
        ],

        form: {
          // facebook data
          facebook: {
            geography: '',
            languages: '',
            contacts_number: 1,
            employees_min: 1,
            employees_max: 1,
            industries: '',
            job_functions: '',
            seniority_level: '',
            groups: '',
          },

          // linkedin data
          linkedin: {
            geography: '',
            languages: '',
            contacts_number: 1,
            employees_min: 1,
            employees_max: 1,
            industries: '',
            job_functions: '',
            seniority_level: '',
            groups: '',
          },

          // youtube data
          youtube: {
            languages: '',
            subscribers_min: null,
            subscribers_max: null,
            categories: ''
          },

          // custom data
          custom: {
            geography: '',
            contacts_number: null,
          },

          // general data
          segment_title: '',
          task_text: '',
          leads_number: null,

          selected_general_data: [], // Must be an array reference!
        },
      }
    },
    methods: {
      handleLinkedinData: function(e) {
        [this.form.linkedin.geography, this.form.linkedin.languages, this.form.linkedin.contacts_number, this.form.linkedin.employees_min, this.form.linkedin.employees_max, this.form.linkedin.industries, this.form.linkedin.job_functions, this.form.linkedin.seniority_level, this.form.linkedin.groups] = e
      },
      handleFacebookData: function(e) {
        [this.form.facebook.geography, this.form.facebook.languages, this.form.facebook.contacts_number, this.form.facebook.employees_min, this.form.facebook.employees_max, this.form.facebook.industries, this.form.facebook.job_functions, this.form.facebook.seniority_level, this.form.facebook.groups] = e
      },
      handleYoutubeData: function(e) {
        [this.form.youtube.languages, this.form.youtube.subscribers_min, this.form.youtube.subscribers_max, this.form.youtube.categories] = e
      },
      handleCustomData: function(e) {
        [this.form.custom.geography, this.form.custom.contacts_number] = e
      },

      onSubmit() {
        alert(JSON.stringify(this.form))
      },
      onCancel() {
        // go back
        this.$router.push({path: "tasks"})
      }
    },
    mounted() {
      this.$set(this, 'task_type', this.$route.query.task_type)
      console.log(this.task_type)
    }
  }
</script>
