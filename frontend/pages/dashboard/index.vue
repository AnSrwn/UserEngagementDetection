<script setup>
import { useApiFetch } from "~/composables/useApiFetch";

// const { data, pending, error, refresh }
const { data } = await useApiFetch("/engagement", {
  transform: (data) => {
    return data.map((item) => ({
      time: new Date(item.time),
      engagement: Number(item.engagement.toFixed(1)),
    }));
  },
  server: false,
});

// function refreshing() {
//   refresh(); // <== Add parenthesis
//   console.log("refreshing");
// }
// setInterval(refreshing, 5000);
</script>

<template>
  <div>
    <h1>Dashboard</h1>
    <div>Engagement: {{ data }}</div>
    <Chart :chart-data="data" />
  </div>
</template>

<style lang='scss'></style>