<script setup>
import {PieChart, VideoCamera} from '@element-plus/icons-vue'


const appConfig = useAppConfig()
const runtimeConfig = useRuntimeConfig()
</script>

<template>
  <div class="introduction-container">
    <div class="introduction-text-content">
      <div class="introduction-text-inner-content">
        <h1>{{$t('home.introduction-header')}}</h1>
        <p>{{$t('home.introduction-text')}}</p>
      </div>
    </div>
    <div class="image-container">
      <img :alt="$t('home.demo-image-title')" class="demo-image" src="/images/demo_analysis.png"/>
      <p style="color: gray;"><i>{{$t('home.demo-image-title')}}</i></p>
    </div>
  </div>
  <el-divider/>
  <div class="cards-container">
    <el-card class="card-participant">
      <h2>{{$t('home.card-participant-title')}}</h2>
      <div class="card-participant-content">
        <el-icon :size="100">
          <VideoCamera/>
        </el-icon>
        <p class="home-cards-text">{{$t('home.card-participant-text-1')}}</p>
        <p class="home-cards-text">{{$t('home.card-participant-text-2')}}</p>
        <el-button class="home-button" type="primary" @click="navigateTo('/detection')">{{$t('home.card-participant-button')}}</el-button>
      </div>
    </el-card>
    <el-card class="card-instructor">
      <h2>{{$t('home.card-instructor-title')}}</h2>
      <div class="card-instructor-content">
        <el-icon :size="100">
          <PieChart/>
        </el-icon>
        <p class="home-cards-text">{{$t('home.card-instructor-text-1')}}</p>
        <p class="home-cards-text">{{$t('home.card-instructor-text-2')}}</p>
        <el-button class="home-button" type="primary" @click="navigateTo('/analysis')">{{$t('home.card-instructor-button')}}</el-button>
      </div>
    </el-card>
  </div>
</template>

<style lang='scss'>
.introduction-container {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  justify-content: space-between;
  margin-top: 30px;
  margin-bottom: 60px;
  gap: 30px 30px;
}

.introduction-text-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex-grow: 1
}

.introduction-text-inner-content {
  max-width: 400px;
}

.image-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex-grow: 1
}

.demo-image {
  max-width: 400px;
}

.cards-container {
  display: flex;
  flex-wrap: wrap;
  flex-direction: row;
  justify-content: center;
  gap: 30px 100px;
  margin-top: 60px;
}

.home-cards-text {
  text-align: center;
}

.card-participant {
  display: flex;
  max-width: 400px;
  flex-grow: 1;

  .card-participant-content {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
  }
}

.card-instructor {
  display: flex;
  justify-content: center;
  max-width: 400px;
  flex-grow: 1;

  .card-instructor-content {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
  }
}

.home-button {
  margin-top: 20px;
}
</style>