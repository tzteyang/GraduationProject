<template>
    <el-row type="flex" justify="space-between" >
      <el-row type="flex" justify="start">
        <img class="my-logo" src="../assets/mylogo.png" alt="img" />
        <p class="DemoName">基于多源开放数据的产业人才画像系统</p>
      </el-row>
      
      <el-menu 
      :default-active="activeIndex" 
      class="el-menu-demo" 
      mode="horizontal" 
      background-color="#DCEAFF" 
      @select="handleSelect"
      text-color="#579AFE"
      active-text-color="#0C58CB"
      >
          <el-menu-item index="1">
            <router-link class="link-a" active-class="active" to="/home">主页</router-link>
          </el-menu-item>
          <el-menu-item index="2">
            <router-link class="link-a" active-class="active" to="/home">人才检索</router-link>
          </el-menu-item>
      </el-menu>
  </el-row>
</template>


<script>
  export default {
    data() {
      return {
        activeIndex: '1',
      };
    },
    methods: {
      handleSelect(key, keyPath) {
        console.log(key, keyPath);
      }
    }
  }
</script>

<style scoped>
.my-logo{
  max-height: 58px;
}
.el-row{
  background-color: #DCEAFF;
}
.DemoName {
  min-width: 300px;
  font-size: 20px;
  font-weight: bold;
  color: #0C58CB;
}
.el-menu-item{
  font-size: 20px;
  font-weight: bold;
}
</style>