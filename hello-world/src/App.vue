<!-- App.vue -->
<template>
  <div id="app">
    <ProfileCard />
  </div>
</template>

<script>
import ProfileCard from "./components/ProfileCard.vue";

export default {
  components: {
    ProfileCard,
  },
};
</script>

<style>
#app {
  text-align: center;
  margin-top: 60px;
}
</style>
