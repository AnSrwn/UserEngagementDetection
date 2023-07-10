<script setup>
import { useApiFetch } from "~/composables/useApiFetch";

// let engagementData = ref([]);

// const { data, pending, error, refresh }
const { data, refresh } = await useApiFetch("/engagement", {
  transform: (data) => {
    // if (data === undefined) {
    //   return [];
    // }

    return data.map((item) => ({
      time: new Date(item.time),
      engagement: Number(item.engagement.toFixed(1)),
    }));
  },
  // server: false,
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
    <!-- <div>Engagement: {{ data }}</div> -->
    <Chart :data="data" />
  </div>
</template>

<style lang='scss'></style>