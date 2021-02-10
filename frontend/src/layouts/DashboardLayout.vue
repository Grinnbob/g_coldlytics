<template>
<div>
    <b-container fluid>
        <b-navbar toggleable="md" type="dark" variant="dark">
            <b-navbar-brand href="/">ColdLytics</b-navbar-brand>

            <b-navbar-toggle target="nav-collapse"></b-navbar-toggle>

            <b-collapse id="nav-collapse" is-nav>
              <b-navbar-nav>
                <b-nav-item to="/tasks">Tasks</b-nav-item>
                <b-nav-item href="/task_empty">Integrations</b-nav-item>
                <b-nav-item href="#">Billing</b-nav-item>
                <b-nav-item href="#">Profile</b-nav-item>
              </b-navbar-nav>
            </b-collapse>
        </b-navbar>
    </b-container>

    <b-container fluid>
        <router-view></router-view>
    </b-container>

</div>
</template>
<script>

</script>
