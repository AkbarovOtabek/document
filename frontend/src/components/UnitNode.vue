<template>
  <div class="unit-node-item" :style="{ marginLeft: level * 16 + 'px' }">
    <!-- Заголовок узла -->
    <div class="unit-title">
      <strong>{{ node.name }}</strong>
      <span class="unit-type">({{ node.type }})</span>
    </div>

    <!-- Дочерние элементы -->
    <div
      v-for="child in node.children"
      :key="child.id"
      class="unit-child"
    >
      <UnitNode :node="child" :level="level + 1" />
    </div>
  </div>
</template>

<script>
export default {
  name: "UnitNode",
  props: {
    node: { type: Object, required: true },
    level: { type: Number, default: 0 },
  },
};
</script>

<style scoped>
.unit-node-item {
  margin-bottom: 8px;
}

.unit-title {
  font-size: 13px;
  color: #111827;
}

.unit-type {
  font-size: 11px;
  margin-left: 4px;
  color: #6b7280;
}

.unit-child {
  margin-top: 4px;
}
</style>
