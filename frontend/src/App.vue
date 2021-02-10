<template>
  <router-view></router-view>
</template>

<script>
  export default {
    mounted () {
      /*this.$notify(
        {
          component: NotificationSample,
          icon: 'nc-icon nc-app'
        })*/
    }
  }
</script>

<style lang="scss">
  @import 'assets/scss/style';

  @import '~bootstrap/scss/bootstrap.scss';
  @import '~bootstrap-vue/src/index.scss';
</style>