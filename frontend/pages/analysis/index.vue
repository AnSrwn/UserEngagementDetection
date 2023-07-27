<script setup>
import { useApiFetch } from "~/composables/useApiFetch";

let numberOfUsers = ref()
let engagementData = ref({});
let boredomData = ref({});
let confusionData = ref({});
let frustrationData = ref({});

const { data, refresh } = await useApiFetch(`engagement/simple/`, {
  query: { time_period: 5 },
  transform: (data) => {
    numberOfUsers.value = data.users;
    engagementData.value = data.engagement; // { "high": 5, "middle": 4, "low": 3 };
    boredomData.value = data.boredom;
    confusionData.value = data.confusion;
    frustrationData.value = data.frustration;

    return data;
  },
});

function refreshing() {
  refresh();
}
setInterval(refreshing, 5000);

refresh();
</script>

<template>
  <div>
    <h1>Analysis</h1>
    <div class="charts-container">
      <div>Engagement: {{ engagementData }}</div>
      <div>Boredom: {{ boredomData }}</div>
      <div>Confusion: {{ confusionData }}</div>
      <div>Frustration: {{ frustrationData }}</div>
      <div>Number of users: {{ numberOfUsers }}</div>
      <DonutChart v-if="numberOfUsers > 0" :data="engagementData" />
      <div v-else>There are no users online</div>
    </div>
  </div>
</template>

<style lang='scss' scoped>
.charts-container {
  display: flex;
  flex-wrap: wrap;
  gap: 30px 30px;
}
</style>