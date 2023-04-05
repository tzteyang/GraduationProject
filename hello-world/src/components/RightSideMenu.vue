<template>
    <div>
      <el-menu
      default-active="2"
      class="el-menu-vertical-demo"
      @open="handleOpen"
      @close="handleClose"
      @select="handleSelect"
      background-color="#C6DAF9"
      text-color="#579AFE"
      active-text-color="#0C58CB">
        <el-submenu index="1">
          <template slot="title">
            <i class="el-icon-location"></i>
            <span>导航一</span>
          </template>
          <el-menu-item-group>
            <el-menu-item index="H_category">选项1</el-menu-item>
            <el-menu-item index="1-2">选项2</el-menu-item>
          </el-menu-item-group>
        </el-submenu>
    </el-menu>
</div>
</template>

<style>
.el-menu-vertical-demo:not(.el-menu--collapse) {
width: 200px;
min-height: 800px;
}
</style>

<script>
  export default {
    methods: {
      handleOpen(key, keyPath) {
        console.log(key, keyPath);
      },
      handleClose(key, keyPath) {
        console.log(key, keyPath);
      },
      handleSelect(key) {
        console.log(key);
      }
    }
  }
</script>

<style scoped>
.el-menu-item{
  font-size: 20px;
  font-weight: bold;
}
</style>

