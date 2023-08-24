<script setup>
const {locales} = useI18n()
const localePath = useLocalePath()
</script>

<template>
  <header>
    <el-menu
        class="menu"
        mode="horizontal"
    >
      <NuxtLink :to="localePath('/')">
        <el-menu-item index="1">
          {{ $t('home.title') }}
        </el-menu-item>
      </NuxtLink>
      <NuxtLink :to="localePath('/detection')">
        <el-menu-item index="2">
          {{ $t('detection.title') }}
        </el-menu-item>
      </NuxtLink>
      <NuxtLink :to="localePath('/analysis')">
        <el-menu-item index="3">
          {{ $t('analysis.title') }}
        </el-menu-item>
      </NuxtLink>
      <el-menu-item index="4">
        <LanguageSwitcher/>
      </el-menu-item>
    </el-menu>
  </header>
</template>

<style lang='scss'>
.menu {
  display: flex;
  align-items: center;
  border-radius: 8px;
  background-color: ghostwhite;
}
</style>