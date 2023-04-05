<template lang="">
    <div class='card-list'>
        <ul>
            <ProfileCard class="profile-card" v-for="n in 5" :key="n"/>
        </ul>
    </div>
</template>

<script>
import ProfileCard from './ProfileCard.vue'

export default {
    components: {
        ProfileCard,
    },
    data() {
        return {
            
        }
    }
}
</script>

<style scoped>
.card-list ul{
    padding-inline-start: 40px;
    padding-inline-end: 40px;
}
.card-list{
    border: 2px solid black; /* 设置边框为2像素粗的实线 */
}
.profile-card{
    margin-bottom: 20px;
}
</style>