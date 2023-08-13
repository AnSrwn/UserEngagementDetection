<script setup>

</script>

<template>
  <div>
    <h1>{{ $t('privacy.title') }}</h1>
    <p class="privacy-text">{{ $t('privacy.introduction') }}</p>

    <h2>{{ $t('privacy.hosting-title') }}</h2>
    <p class="privacy-text">{{ $t('privacy.hosting-text-1') }}</p>
    <p class="privacy-text">{{ $t('privacy.hosting-text-2') }}</p>

    <h2>{{ $t('privacy.data-title') }}</h2>
    <p class="privacy-text">{{ $t('privacy.data-text-1') }}</p>

    <h2>{{ $t('privacy.revocation-title') }}</h2>
    <p class="privacy-text">{{ $t('privacy.revocation-text-1') }}</p>
  </div>
</template>

<style lang='scss'>

.privacy-text{
  text-align: justify;
}
</style>