<script lang="ts" setup>
const {locale, locales, setLocale} = useI18n()

const language = computed({
  get: () => locale.value,
  set: (value) => {
    setLocale(value);
  }
});
</script>

<template>
  <el-select v-model="language" :placeholder="$t('general.select-placeholder')">
    <el-option
        v-for="item in locales"
        :key="item"
        :label="item.name"
        :value="item.code"
    />
  </el-select>
</template>

<style lang="scss" scoped>

</style>