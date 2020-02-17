<template>

  <div id="app">
    <app-header></app-header>
    <app-content></app-content>
    <app-footer></app-footer>
  </div>
</template>

<script>
import Header from './components/Header'
import Footer from './components/Footer'
import Content from './components/Content'
export default {
  name: "肿瘤辅助诊断系统",
  data() {
    return {

    }
  },
  components:{
    "app-header":Header,
    "app-footer":Footer,
    "app-content":Content
  },
  methods: {

  },

};
</script>

<style scope="this api replaced by slot-scope in 2.5.0+">

</style>
