<script setup>
import {useApiFetch} from "~/composables/useApiFetch";

let high = 0;
let connectedUsers = ref();
let visibleUsers = ref();
let allData = ref();
let engagementData = ref();
let boredomData = ref();
let confusionData = ref();
let frustrationData = ref();

const {data, refresh} = await useApiFetch(`engagement/simple`, {
  query: {time_period: 5},
  transform: (data) => {
    connectedUsers.value = data.connections;
    visibleUsers.value = data.visible_users;
    allData = data;
    engagementData.value = data.engagement;
    boredomData.value = data.boredom;
    confusionData.value = data.confusion;
    frustrationData.value = data.frustration;

    return data;
  },
});

function refreshing() {
  // high++;
  // numberOfUsers.value = 12 + high;
  // engagementData.value = { high: high, middle: 4, low: 2 };
  // confusionData.value = { high: 1, middle: high, low: 8 };
  // boredomData.value = { high: 1, middle: 0, low: 0 };
  // frustrationData.value = { high: 3, middle: 1, low: high };
  // allData.value = {
  //   users: numberOfUsers,
  //   engagement: engagementData,
  //   boredom: boredomData,
  //   confusion: confusionData,
  //   frustration: frustrationData,
  // };
  refresh();
}

let requestInterval;

onMounted(() => {
  refreshing();
  requestInterval = setInterval(refreshing, 5000);
})

onDeactivated(() => {
  clearInterval(requestInterval);
})

onBeforeUnmount(() => {
  clearInterval(requestInterval);
})
</script>

<template>
  <div>
    <h1>{{ $t('analysis.title') }}</h1>
    <client-only>
      <div class="info-container">
        <el-card class="info-card">
          <div class="large-text">{{ connectedUsers }}</div>
          <div>{{ $t('analysis.info-connected-users') }}</div>
        </el-card>
        <el-card class="info-card">
          <div class="large-text">{{ visibleUsers }}</div>
          <div>{{ $t('analysis.info-visible-users') }}</div>
        </el-card>
      </div>
      <el-divider/>
      <MoodWave v-if="visibleUsers > 0" :data="allData"/>
      <div class="charts-container">
        <el-card class="engagement-card">
          <template #header>
            <h2>{{ $t('analysis.engagement') }}</h2>
          </template>
          <DonutChart v-if="visibleUsers > 0" :data="engagementData"/>
          <div v-else>{{ $t('analysis.no-data') }}</div>
        </el-card>
        <div class="bar-chart-container">
          <el-card class="bar-card">
            <template #header>
              <h2>{{ $t('analysis.confusion') }}</h2>
            </template>
            <BarChart
                v-if="visibleUsers > 0"
                :data="confusionData"
                class="bar-chart"
                :tooltipText="$t('analysis.tooltip-confused')"
            />
            <div v-else>{{ $t('analysis.no-data') }}</div>
          </el-card>
          <el-card class="bar-card">
            <template #header>
              <h2>{{ $t('analysis.boredom') }}</h2>
            </template>
            <BarChart
                v-if="visibleUsers > 0"
                :data="boredomData"
                class="bar-chart"
                :tooltipText="$t('analysis.tooltip-bored')"
            />
            <div v-else>{{ $t('analysis.no-data') }}</div>
          </el-card>
          <el-card class="bar-card">
            <template #header>
              <h2>{{ $t('analysis.frustration') }}</h2>
            </template>
            <BarChart
                v-if="visibleUsers > 0"
                :data="frustrationData"
                class="bar-chart"
                :tooltipText="$t('analysis.tooltip-frustrated')"
            />
            <div v-else>{{ $t('analysis.no-data') }}</div>
          </el-card>
        </div>
      </div>
    </client-only>
  </div>
</template>

<style lang='scss' scoped>
.info-container{
  display: flex;
  flex-direction: row;
  gap: 20px 20px;
}

.info-card {
  width: fit-content;
  height: fit-content;

  .large-text {
    font-weight: bold;
    font-size: 2.5em;
  }
}

.charts-container {
  display: flex;
  flex-wrap: wrap;
  flex-direction: row;
  height: 500px;
  gap: 30px 30px;
}

.engagement-card {
  max-width: 600px;
  min-width: 400px;
  flex-grow: 1;
  height: fit-content;
}

@media only screen and (max-width: 400px) {
  .engagement-card {
    min-width: 100%;
  }
}

.bar-chart-container {
  display: flex;
  max-width: 600px;
  min-width: 400px;
  flex-direction: column;
  flex-grow: 1;
  gap: 30px 30px;
  padding-bottom: 20px;
}

@media only screen and (max-width: 400px) {
  .bar-chart-container {
    min-width: 100%;
  }
}

.bar-card {
  width: 100%;
  height: fit-content;

  .bar-chart {
    width: 100%;
    height: fit-content;
  }
}
</style>