<script setup>
import {useApiFetch} from "~/composables/useApiFetch";

let high = 0;
let numberOfUsers = ref();
let allData = ref();
let engagementData = ref();
let boredomData = ref();
let confusionData = ref();
let frustrationData = ref();

const {data, refresh} = await useApiFetch(`engagement/simple`, {
  query: {time_period: 5},
  transform: (data) => {
    numberOfUsers.value = data.users;
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
  // boredomData.value = { high: 5, middle: 3, low: high };
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
    <h1>Analysis</h1>
    <el-card class="info-card">
      <div class="large-text">{{ numberOfUsers }}</div>
      <div>Users online</div>
    </el-card>
    <el-divider/>
    <MoodWave v-if="numberOfUsers > 0" :data="allData"/>
    <div class="charts-container">
      <el-card class="engagement-card">
        <template #header>
          <h2>Engagement</h2>
        </template>
        <DonutChart v-if="numberOfUsers > 0" :data="engagementData"/>
        <div v-else>There are no users online</div>
      </el-card>
      <div class="bar-chart-container">
        <el-card class="bar-card">
          <template #header>
            <h2>Confusion</h2>
          </template>
          <BarChart
              v-if="numberOfUsers > 0"
              :data="confusionData"
              class="bar-chart"
              tooltipText="Confused"
          />
          <div v-else>There are no users online</div>
        </el-card>
        <el-card class="bar-card">
          <template #header>
            <h2>Boredom</h2>
          </template>
          <BarChart
              v-if="numberOfUsers > 0"
              :data="boredomData"
              class="bar-chart"
              tooltipText="Bored"
          />
          <div v-else>There are no users online</div>
        </el-card>
        <el-card class="bar-card">
          <template #header>
            <h2>Frustration</h2>
          </template>
          <BarChart
              v-if="numberOfUsers > 0"
              :data="frustrationData"
              class="bar-chart"
              tooltipText="Frustrated"
          />
          <div v-else>There are no users online</div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<style lang='scss' scoped>
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