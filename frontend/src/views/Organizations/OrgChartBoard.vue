<script>
import UnitNode from "./UnitNode.vue";

export default {
  name: "OrgChartBoard",
  components: { UnitNode },
  emits: ["pick", "create-child", "create-emp"], // отдаём вверх выбранный unit
  props: {
    root: { type: Object, required: true },
    color: { type: String, default: "#c9cfda" },
  },
  methods: {
    emitUnit(node, path) {
      this.$emit("pick", { kind: "unit", payload: node, path });
    },
    emitCreateChild(node) {
      this.$emit("create-child", node);
    },
    emitCreateEmp(node) {
      this.$emit("create-emp", node);
    },
  },
};
</script>

<template>
  <div class="board">
    <UnitNode
      :node="root"
      :wire="color"
      @pick-unit="emitUnit"
      @create-child="emitCreateChild"
      @create-emp="emitCreateEmp"
    />
  </div>
</template>

<style scoped>
.board {
  display: grid;
  justify-items: center;
  overflow: visible;
}
</style>
