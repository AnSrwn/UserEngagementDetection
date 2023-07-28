<script setup>
import { useApiFetch } from "~/composables/useApiFetch";

let high = 0;
let numberOfUsers = ref();
let engagementData = ref();
let boredomData = ref();
let confusionData = ref();
let frustrationData = ref();

const { data, refresh } = await useApiFetch(`engagement/simple/`, {
  query: { time_period: 5 },
  transform: (data) => {
    numberOfUsers.value = 12; // data.users;
    // engagementData.value = data.engagement; // { "high": 5, "middle": 4, "low": 2 };
    boredomData.value = data.boredom;
    confusionData.value = data.confusion;
    frustrationData.value = data.frustration;

    return data;
  },
});

function refreshing() {
  high++;
  numberOfUsers.value = 12;
  engagementData.value = { high: high, middle: 4, low: 2 };
  refresh();
}
refreshing();
setInterval(refreshing, 5000);
</script>

<template>
  <div>
    <h1>Analysis</h1>
    <div class="charts-container">
      <div>
        <div>Engagement: {{ engagementData }}</div>
        <div>Boredom: {{ boredomData }}</div>
        <div>Confusion: {{ confusionData }}</div>
        <div>Frustration: {{ frustrationData }}</div>
        <div>Number of users: {{ numberOfUsers }}</div>
      </div>
      <div class="donut-chart">
        <h2>Engagement</h2>
        <DonutChart v-if="numberOfUsers > 0" :data="engagementData" />
        <div v-else>There are no users online</div>
      </div>
    </div>
  </div>
</template>

<style lang='scss' scoped>
.donut-chart {
  width: 100%;
  height: 100%;
  max-width: 500px;
  max-height: 500px;
}
.charts-container {
  display: flex;
  flex-wrap: wrap;
  flex-direction: column;
  gap: 30px 30px;
}
</style>