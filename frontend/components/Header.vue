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
      <el-menu-item index="1" @click="navigateTo('/')">
        {{ $t('home.title') }}
      </el-menu-item>
      <el-menu-item index="2" @click="navigateTo('/detection')">
        {{ $t('detection.title') }}
      </el-menu-item>
      <el-menu-item index="3" @click="navigateTo('/analysis')">
        {{ $t('analysis.title') }}
      </el-menu-item>
      <!--      <div class="flex-grow"/>-->
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

//.flex-grow {
//  flex-grow: 1;
//}
</style>