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
    // numberOfUsers.value = data.users;
    // engagementData.value = data.engagement;
    boredomData.value = data.boredom;
    // confusionData.value = data.confusion;
    frustrationData.value = data.frustration;

    return data;
  },
});

function refreshing() {
  high++;
  numberOfUsers.value = 12;
  engagementData.value = { high: high, middle: 4, low: 2 };
  confusionData.value = { high: high, middle: 2, low: 8 };
  refresh();
}
refreshing();
setInterval(refreshing, 5000);
</script>

<template>
  <div>
    <h1>Analysis</h1>
    <p>
      Engagement: {{ engagementData }}<br />Boredom: {{ boredomData
      }}<br />Confusion: {{ confusionData }}<br />Frustration:
      {{ frustrationData }}<br />Number of users: {{ numberOfUsers }}
    </p>
    <div class="charts-container">
      <div class="engagement-card">
        <h2>Engagement</h2>
        <DonutChart v-if="numberOfUsers > 0" :data="engagementData" />
        <div v-else>There are no users online</div>
      </div>
      <div class="confusion-card">
        <h2>Confusion</h2>
        <VerticalBarChart
          v-if="numberOfUsers > 0"
          class="confusion-chart"
          :data="confusionData"
        />
        <div v-else>There are no users online</div>
      </div>
    </div>
  </div>
</template>

<style lang='scss' scoped>
.engagement-card {
  width: 500px;
  height: 500px;
}
.confusion-card {
  width: 500px;
  .confusion-chart {
    width: 100%;
    height: 500px;
  }
}
.charts-container {
  display: flex;
  flex-wrap: wrap;
  flex-direction: row;
  justify-content: space-around;
  gap: 30px 30px;
}
</style>