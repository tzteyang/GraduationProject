<!-- App.vue -->
<template>
  <div id="app">
    <div class="header">
      <HeaderMenu></HeaderMenu>
    </div>
    <div class="content">
      <RightSideMenu></RightSideMenu>
      <CardList v-show="info.relevant_experts.length"></CardList>
    </div>
    <div class="footer"></div>
  </div>
</template>

<script>
// import ProfileCard from "./components/ProfileCard.vue";
// import WelcomeMessage from './components/Welcome.vue'
import HeaderMenu from './components/HeaderMenu.vue'
import RightSideMenu from './components/RightSideMenu.vue'
import CardList from './components/CardList.vue'

export default {
  components: {
    HeaderMenu, RightSideMenu, CardList
    // ProfileCard, WelcomeMessage, HeaderMenu
  },
  data() {
    return {
      info:{
        firstLoad: true,
        isLoading: false,
        relevant_experts: [12,23],
      }
    }
  },
};
</script>

<style scoped>
.content{
  display: flex;
  justify-content: flex-start;
}
</style>
