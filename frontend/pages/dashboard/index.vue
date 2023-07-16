<script setup>
import { useApiFetch } from "~/composables/useApiFetch";

let lastTimestamp = ref(0);
let engagementData = ref(Array());
let boredomData = ref(Array());
let confusionData = ref(Array());
let frustrationData = ref(Array());

const { data, refresh } = await useApiFetch(`engagement/`, {
  query: { from_datetime: lastTimestamp },
  transform: (data) => {
    lastTimestamp.value = data.at(-1).time;

    const engagementMappedData = data.map((item) => ({
      time: new Date(item.time),
      item: Number(item.engagement.toFixed(1)),
    }));
    engagementData.value = [...engagementData.value, ...engagementMappedData];

    const boredomMappedData = data.map((item) => ({
      time: new Date(item.time),
      item: Number(item.boredom.toFixed(1)),
    }));
    boredomData.value = [...boredomData.value, ...boredomMappedData];

    const confusionMappedData = data.map((item) => ({
      time: new Date(item.time),
      item: Number(item.confusion.toFixed(1)),
    }));
    confusionData.value = [...confusionData.value, ...confusionMappedData];

    const frustrationMappedData = data.map((item) => ({
      time: new Date(item.time),
      item: Number(item.frustration.toFixed(1)),
    }));
    frustrationData.value = [
      ...frustrationData.value,
      ...frustrationMappedData,
    ];

    return data;
  },
});

function refreshing() {
  refresh();
}
setInterval(refreshing, 3000);
</script>

<template>
  <div>
    <h1>Dashboard</h1>
    <div class="charts-container">
      <div>
        <h2>Engagement:</h2>
        <Chart :data="engagementData" />
      </div>
      <div>
        <h2>Boredom:</h2>
        <Chart :data="boredomData" />
      </div>
      <div>
        <h2>Confusion:</h2>
        <Chart :data="confusionData" />
      </div>
      <div>
        <h2>Frustration:</h2>
        <Chart :data="frustrationData" />
      </div>
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