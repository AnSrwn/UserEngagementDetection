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
  numberOfUsers.value = 6 + high;
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
    <el-card class="info-card">
      <div class="large-text">{{ numberOfUsers }}</div>
      <div>Users online</div>
    </el-card>
    <el-divider />
    <div class="charts-container">
      <el-card class="engagement-card">
        <template #header>
          <h2>Engagement</h2>
        </template>
        <DonutChart v-if="numberOfUsers > 0" :data="engagementData" />
        <div v-else>There are no users online</div>
      </el-card>
      <el-card class="confusion-card">
        <template #header>
          <h2>Confusion</h2>
        </template>
        <VerticalBarChart
          v-if="numberOfUsers > 0"
          class="confusion-chart"
          :data="confusionData"
        />
        <div v-else>There are no users online</div>
      </el-card>
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
  width: 500px;
  height: fit-content;
}
.confusion-card {
  width: 500px;
  height: fit-content;
  .confusion-chart {
    width: 100%;
    height: fit-content;
  }
}
</style>