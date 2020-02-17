<template>
    <div id="Footer">
        <p>{{msg}}</p>
    </div>
</template>
<script>
export default {
    name:'Footer',
    data(){
        return {
            msg:'Copyright 2019'
        }
    }
}
</script>
<style scoped>
#Footer{
    /*background:#F2F6FC;*/
    padding:6px;
    border-radius: 5px;
    width:80%;
    height:80px;
    margin:20px auto;
    margin-top:140px;
}

p{
    color:#21b3b9;
    text-align: center;
    margin:30px auto;
    font-size:1.1em;
}
</style>


