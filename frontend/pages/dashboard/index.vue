<script setup>
import { useApiFetch } from "~/composables/useApiFetch";

let lastTimestamp = ref(0);
let engagementData = ref(Array());

const { data, refresh } = await useApiFetch(`/engagement`, {
  query: { from_datetime: lastTimestamp },
  transform: (data) => {
    const mappedData = data.map((item) => ({
      time: new Date(item.time),
      engagement: Number(item.engagement.toFixed(1)),
    }));
    lastTimestamp.value = data.at(-1).time;
    engagementData.value = [...engagementData.value, ...mappedData];
    return mappedData;
  },
});

function refreshing() {
  refresh();
  console.log("refreshing");
}
setInterval(refreshing, 3000);
</script>

<template>
  <div>
    <h1>Dashboard</h1>
    <Chart :data="engagementData" />
  </div>
</template>

<style lang='scss'></style>