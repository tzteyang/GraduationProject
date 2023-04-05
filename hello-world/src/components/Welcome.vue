<template>
    <transition name="fade">
      <div class="welcome-message">
        <h1>Welcome to My Website!</h1>
        <p>This is the first time you have visited our site. Thank you for your support!</p>
      </div>
    </transition>
</template>
  
<script>
export default {
    name: "WelcomeMessage",
};
</script>

<style>
.welcome-message {
text-align: center;
margin-top: 100px;
font-size: 2rem;
}

.fade-enter-active,
.fade-leave-active {
transition: opacity 0.5s ease-in-out;
}

.fade-enter,
.fade-leave-to {
opacity: 0;
}
</style>
  