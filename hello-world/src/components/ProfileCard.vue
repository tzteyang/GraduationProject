<template>
  <div class="profile-card">
    <div class="top-section">
      <div class="left-section">
        <div class="avatar">
          <img :src="expert.avatar" alt="头像" />
        </div>
        <p class="name"><i class="fas fa-user"></i> {{ expert.name }}</p>
      </div>
      <div class="right-section">
        
        <div class="stats">
          <div class="stat">
            <i class="fas fa-award"></i> 技术影响力：{{ expert.impact }}
          </div>
          <div class="stat">
            <i class="fas fa-download"></i> 下载量：{{ expert.downloads }}
          </div>
          <div class="stat">
            <i class="fas fa-quote-right"></i> 引用量：{{ expert.citations }}
          </div>
        </div>

        <div class="occupation">
            <p><i class="fas fa-briefcase"></i> {{ expert.company }} - {{ expert.position }}</p>
        </div>

        <div class="research-area">
          <div v-for="(area, index) in expert.researchArea" :key="index" class="area" :style="{ 'background-color': expert.colors[index] }">
            <p>{{ area }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      expert: {
        avatar: require("../assets/avatar.jpg"),
        name: "张三",
        company: "某知名公司",
        position: "首席科学家",
        impact: 85,
        downloads: 12000,
        citations: 1280,
        researchArea: ["人工智能与机器学习", "数据挖掘", "自然语言处理"],
        colors: ["#72cdf7", "#72f79a", "#dab551"],
      },
    };
  },
};
</script>


<style scoped>
.profile-card {
  background-color: #e1f5fe;
  /* background-color: #dab551; */
  border-radius: 25px;
  padding: 5px;
  max-width: 700px;
  max-height: 230px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  position: relative;
  overflow: hidden;
}

.top-section {
  display: flex;
}

.left-section {
  flex: 1;
  background-color: #7482cc;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 15px;
  /* border-radius: 15px; */
  border-top-left-radius: 15px;
  border-bottom-left-radius: 15px;
}

.avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  overflow: hidden;
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.name {
  font-size: 14px;
  margin-top: 10px;
  display: flex;
  align-items: center;
  color: #ffffff;
}

.name i {
  margin-right: 5px;
  color: #ffffff;
}

.right-section {
  flex: 3;
  display: flex;
  flex-direction: column;
  padding: 0 15px;
  background-color: #e1f5fe;
  border-radius: 5px;
  padding: 15px;
  margin-right: 15px;
  position: relative;
}

.right-section p {
  font-size: 14px;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  color: #5c6bc0;
}

.right-section i {
  margin-right: 5px;
  color: #5c6bc0;
}

.stats {
  display: flex;
  justify-content: space-between;
}

.stat {
  background-color: #e1f5fe;
  padding: 5px 10px;
  border: 1px solid #5c6bc0;
  border-radius: 5px;
  display: flex;
  align-items: center;
  color: #5c6bc0;
  margin-right: 5px;
}

.stat:last-child {
  margin-right: 0;
}

.stat i {
  margin-right: 5px;
  color: #5c6bc0;
}
.research-area {
  /* background-color: #cbe0f1; */
  padding: 8px 15px;
  border-top: 1px solid #ccc;
  margin-top: 15px;
  /* border-radius: 15px 15px 15px 15px; */
  position: absolute;
  bottom: 0px;
  right: 0px;
  left: 15px;
  display: flex;
  justify-content: space-between;
}

.occupation {
  display: flex; /* 将子元素设置为flex布局 */
  align-items: center; /* 在交叉轴上居中对齐 */
  justify-content: center; /* 在主轴上居中对齐 */
  margin-top: 10px;
}
.occupation p {
  align-self: center; /* 在交叉轴上居中对齐 */
  font-size: 20px;
}

.research-area p {
  font-size: 14px;
  color: #5a5958;
  margin: 0;
}
.area {
  width: 30%;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 1em; /* 设置字体大小为父级div的100% */
  height: 30px;
  border-radius: 15px;
  display: flex; /* 将子元素设置为flex布局 */
  align-items: center; /* 在交叉轴上居中对齐 */
  justify-content: center; /* 在主轴上居中对齐 */
}
.area p {
  font-size: 14px;
  align-self: center; /* 在交叉轴上居中对齐 */
  font-weight: bold;
}
</style>