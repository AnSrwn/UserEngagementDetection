<script setup>
const {locale, locales, setLocale} = useI18n()
const localePath = useLocalePath()
</script>

<template>
  <header>
    <el-menu
        class="menu"
        mode="horizontal"
    >
      <el-menu-item index="1">
        <NuxtLink :to="localePath('/')">Home</NuxtLink>
      </el-menu-item>
      <el-menu-item index="2">
        <NuxtLink :to="localePath('/detection')">Detection</NuxtLink>
      </el-menu-item>
      <el-menu-item index="3">
        <NuxtLink :to="localePath('/analysis')">Analysis</NuxtLink>
      </el-menu-item>
<!--      <div class="flex-grow"/>-->
      <el-menu-item index="4">
        <LanguageSwitcher />
      </el-menu-item>
    </el-menu>
  </header>
</template>

<style lang='scss'>
.menu {
  display: flex;
  align-items: center;
}

//.flex-grow {
//  flex-grow: 1;
//}
</style>